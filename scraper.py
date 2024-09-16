import google.generativeai as genai
import requests
import time
import json
import os
from groq import Client

# PriceAPI details
API_KEY = 'JRGAWLNYUFTIVBBTDCKYJFNLIERTXJEVUWRJFHVKUMSTKEBHXKVVOVSVJRUNBJOG'
BASE_URL = 'https://api.priceapi.com/v2/'

# Groq API details
groq_api_key = os.getenv('GROQ_API_KEY', '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')  # Can be set in env
client = Client(api_key=groq_api_key)

# Directly configure Gemini API with your provided key
genai.configure(api_key='AIzaSyCXwlibA4A8m4OqjFU9xk6Ix-A_VqUKRbM')

def extract_id(url):
    """
    Extracts the ID (ASIN) from a given Amazon product URL.
    This function now supports both "/dp/" and "/gp/product/" style URLs.
    """
    try:
        if '/dp/' in url:
            product_id = url.split('/dp/')[1].split('/')[0].split('?')[0]
        elif '/gp/product/' in url:
            product_id = url.split('/gp/product/')[1].split('/')[0].split('?')[0]
        else:
            raise ValueError("Failed to extract ID from the URL format.")
        return product_id
    except IndexError:
        print("Failed to extract ID from the URL.")
        return None


def create_job(ids):
    """
    Creates a job to retrieve product data for multiple IDs from PriceAPI.
    """
    endpoint = BASE_URL + 'jobs'
    payload = {
        'token': API_KEY,
        'source': 'amazon',
        'country': 'us',
        'topic': 'product',  # Using 'product' topic
        'key': 'id',  # Using 'id' as key
        'values': '\n'.join(ids),  # Supports multiple IDs
    }

    print("Creating job with the following details:")
    print(f"Endpoint: {endpoint}")
    print(f"Payload: {payload}")

    try:
        response = requests.post(endpoint, data=payload)
        response.raise_for_status()
        data = response.json()

        if 'job_id' in data:
            job_id = data['job_id']
            print(f"Job created successfully. Job ID: {job_id}")
            return job_id
        else:
            print(f"Job creation failed: {data}")
            return None
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request exception occurred: {req_err}")
    return None

def poll_job_status(job_id):
    """
    Polls the status of a job until it is finished.
    """
    endpoint = BASE_URL + f'jobs/{job_id}'
    params = {'token': API_KEY}

    while True:
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()

            current_status = data.get('status')
            print(f"Current job status: {current_status}")

            if current_status == 'finished':
                print("Job finished successfully.")
                return BASE_URL + f'jobs/{job_id}/download.json?token={API_KEY}'
            elif current_status in ['working', 'finishing']:
                print("Job still in progress... Checking again in 10 seconds.")
                time.sleep(10)
            elif current_status == 'new':
                print("Job is in 'new' status. Waiting for it to start processing...")
                time.sleep(10)
            else:
                print(f"Unexpected job status: {current_status}")
                return None
        except requests.RequestException as e:
            print(f"Error polling job status from PriceAPI: {e}")
            return None

def fetch_results(results_url):
    """
    Fetches and parses the results from a finished job.
    """
    try:
        response = requests.get(results_url)
        response.raise_for_status()
        data = response.json()

        print("Fetched Results: ", json.dumps(data, indent=4))

        comparison_data = []
        additional_ids = set()  # Using a set to prevent duplicates
        similar_brand_ids = []  # Store similar brand product IDs separately

        if 'results' in data and len(data['results']) > 0:
            original_brand = None
            for result in data['results']:
                content = result.get('content', {})

                # Include the target product in the comparison
                product_brand = content.get('brand_name', 'N/A')
                if not original_brand:
                    original_brand = product_brand  # Store the brand of the original product

                comparison_data.append({
                    'name': content.get('name', 'N/A'),
                    'price': content.get('rrp', 'N/A'),  # Adjusted for 'product' topic
                    'url': content.get('url', 'N/A'),
                    'rating': content.get('review_rating', 'N/A'),
                    'reviews': content.get('review_count', 'N/A'),
                    'features': content.get('feature_bullets', []),
                    'dimensions': content.get('dimensions', 'N/A'),
                    'availability': content.get('buybox', {}).get('availability_text', 'N/A') if 'buybox' in content else 'N/A',
                    'delivery_info': ', '.join(content.get('buybox', {}).get('delivery_info', [])) if content.get('buybox', {}).get('delivery_info') else 'N/A',
                    'brand': product_brand,
                    'image_url': content.get('image_url', 'N/A'),
                    'type': 'target'
                })

                # Collect IDs from the "Similar brands on Amazon" section
                if 'carousels' in content:
                    for carousel in content.get('carousels', []):
                        if carousel.get('title') == 'Similar brands on Amazon':
                            for product in carousel.get('products', []):
                                similar_brand_ids.append(product['id'])

                # Collect additional IDs from related content (only if they are not similar brands)
                if 'product_links' in content:
                    for link_type in ['variants', 'substitutes', 'sponsored']:
                        if content['product_links'].get(link_type):
                            additional_ids.update(content['product_links'][link_type])

        # If we have similar brand IDs, prefer those over the additional IDs
        if similar_brand_ids:
            return comparison_data, similar_brand_ids[:5], original_brand
        else:
            return comparison_data, list(additional_ids)[:5], original_brand  # Limit additional IDs to 5

    except requests.RequestException as e:
        print(f"Error fetching results from PriceAPI: {e}")
        return [], [], None
    except ValueError as e:
        print(f"Error parsing JSON response: {e}")
        return [], [], None


def filter_and_fetch_different_brand_products(additional_data, original_brand):
    """
    Filters additional data to include only products from different brands.
    """
    different_brand_products = []
    
    for product in additional_data:
        if product.get('brand') and product['brand'] != original_brand:
            different_brand_products.append(product)

    return different_brand_products

def summarize_features_with_groq(features):
    """
    Summarizes the product features into three concise bullet points using Groq API.
    """
    try:
        if not features:
            return ["No features available"]  # Handling empty features list

        features_text = "; ".join(features)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert summarizer."},
                {"role": "user", "content": f"Summarize the following features into three short, concise bullet points (with this symbol: '•'), and *important* DO NOT return any introductory text: {features_text}"}
            ],
            model="llama3-8b-8192"
        )
        if chat_completion.choices and len(chat_completion.choices) > 0:
            summary = chat_completion.choices[0].message.content
            return summary.strip().split('\n')[:3]  # Return the top 3 points
        else:
            raise ValueError("Unexpected response format from Groq API")
    except Exception as e:
        print(f"Error summarizing features with Groq API: {e}")
        return ["Error generating summary."]

def analyze_product_with_groq(product):
    """
    Analyzes a product's details using Groq API and provides pros/cons and best-suited consumer.
    """
    try:
        # Combine all product details
        product_details = (
            f"Name: {product['name']}, Price: {product['price']}, Rating: {product['rating']}, "
            f"Reviews: {product['reviews']}, Features: {'; '.join(product['features'])}, "
            f"Availability: {product['availability']}, Delivery Info: {product['delivery_info']}"
        )
        
        # Make a Groq API call to analyze the product
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert product reviewer."},
                {"role": "user", "content": f"Please provide a detailed analysis of this product, ONLY including pros, cons, and what kind of consumer it would be best suited for (with these headers surrounded by asterisks no bullet points). **do not include any introductory text** and make sure the text is center aligned with bullet points and with one space from the headers, and **do not return the title of the product** and please ONLY include pros, cons, and best suited for: {product_details}"}
            ],
            model="llama3-8b-8192"
        )

        # Extract the analysis from the Groq response
        if chat_completion.choices and len(chat_completion.choices) > 0:
            analysis = chat_completion.choices[0].message.content
            return analysis.strip()
        else:
            raise ValueError("Unexpected response format from Groq API")
    except Exception as e:
        print(f"Error analyzing product with Groq API: {e}")
        return "Error generating analysis."

def analyze_reviews_with_gemini(products):
    """
    Analyzes the reviews of all products using Gemini API, providing the product link for context.
    """
    reviews_summary = []
    for product in products:
        # Combine product reviews and URL
        product_reviews = f"Product: {product['name']}, URL: {product['url']}, Reviews: {product['reviews']}"

        # Call Gemini API using google-generativeai SDK to summarize reviews
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(f"Summarize customer reviews for the product, highlighting what consumers like and dislike about the product, and do not include any introductory text and the format should be a header for likes and dislikes (surrounded with asterisks) with a bullet point (with this symbol: '•') followed by the information: {product_reviews}")

            # Check for valid response and handle blocked/empty responses
            if response and hasattr(response, 'text') and response.text:
                summary = response.text
            else:
                print(f"Blocked or empty response from Gemini API for product {product['name']}")
                # Retry with a separate API call for that product
                summary = retry_fetch_product_details_with_gemini(product['url'])

            reviews_summary.append({
                'name': product['name'],
                'review_summary': summary,
                'url': product['url']
            })
        except Exception as e:
            print(f"Error analyzing reviews with Gemini API: {e}")
            reviews_summary.append({
                'name': product['name'],
                'review_summary': 'Error summarizing reviews',
                'url': product['url']
            })

    return reviews_summary

def retry_fetch_product_details_with_gemini(product_url):
    """
    If the first Gemini API call fails or is blocked, retry fetching the product details with a new call.
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"Generate detailed product insights and customer feedback from this Amazon product URL: {product_url}, and summarize into three concise bullet points, max is 100 characters per bullet point."
        response = model.generate_content(prompt)

        if response and hasattr(response, 'text') and response.text:
            return response.text.strip()
        else:
            print(f"Second attempt to fetch product details from Gemini failed for {product_url}")
            return "Error generating detailed product insights."
    except Exception as e:
        print(f"Retry error fetching Gemini details: {e}")
        return "Error generating detailed product insights."

def summarize_product_features_with_gemini(product_url):
    """
    Uses Gemini AI to generate three key bullet points of information about a product based on its Amazon URL.
    """
    try:
        # Call Gemini API to summarize the product features
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"Generate a list of three short, concise key bullet points (aim for 10 words per bullet point) summarizing the product from this Amazon URL, and please do not include any introductory text and the format should be a bullet point followed by the information, do not include any asterisk introduction for each bullet point either: {product_url}"
        response = model.generate_content(prompt)

        # Handle empty or blocked responses gracefully
        if response and hasattr(response, 'text') and response.text:
            # Extract bullet points
            summary = response.text.strip().split('\n')[:3]
            return summary if summary else ["No key features found."]
        else:
            print(f"Blocked or empty response from Gemini API for URL {product_url}")
            return ["Error: No valid content returned."]
    except Exception as e:
        print(f"Error summarizing product features with Gemini: {e}")
        return ["Error generating key features."]

def process_and_analyze_products(comparison_data):
    """
    Processes each product and analyzes it using Groq API.
    """
    analyzed_data = []
    for product in comparison_data:
        # Generate analysis for each product
        analysis = analyze_product_with_groq(product)
        product['analysis'] = analysis  # Add the analysis to the product data

        # Generate a 3-bullet-point summary for the product's features
        if product.get('features'):
            product['features_summary'] = summarize_features_with_groq(product['features'])
        else:
            product['features_summary'] = ["No features available"]

        analyzed_data.append(product)
    
    return analyzed_data

def compare_product(product_id):
    """
    Orchestrates the process of creating a job, polling job status, and retrieving product comparison data.
    """
    # Start with the initial ID
    ids = [product_id]

    # First API call to get initial data and additional IDs
    job_id = create_job(ids)
    if not job_id:
        print("Failed to create job on PriceAPI.")
        return []

    results_url = poll_job_status(job_id)
    if not results_url:
        print("Failed to retrieve results URL from PriceAPI.")
        return []

    comparison_data, additional_ids, original_brand = fetch_results(results_url)

    # Fetch details for additional IDs, limiting to top 4-5 similar products
    if additional_ids:
        print(f"Fetching additional details for IDs: {additional_ids[:5]}")  # Limit to 5 IDs
        job_id = create_job(list(additional_ids[:5]))  # Limit the second call to 5 IDs
        if job_id:
            results_url = poll_job_status(job_id)
            if results_url:
                additional_data, _, _ = fetch_results(results_url)  # Expect three values

                # Ensure we get products from different brands
                additional_data_filtered = filter_and_fetch_different_brand_products(additional_data, original_brand)

                # If not enough products from different brands, append similar products as fallback
                while len(additional_data_filtered) < 4 and len(additional_data) > len(additional_data_filtered):
                    additional_data_filtered.append(additional_data[len(additional_data_filtered)])

                # Add filtered products to the comparison
                comparison_data.extend(additional_data_filtered)

    # Process and analyze products
    analyzed_data = process_and_analyze_products(comparison_data)

    # Limit to show top 4-5 products including the original
    return analyzed_data[:5]

# New independent function for "Didn't Find What You're Looking For?" feature
def create_search_job(search_term):
    """
    Creates a job for searching products based on a search term.
    """
    endpoint = BASE_URL + 'jobs'
    payload = {
        'token': API_KEY,
        'source': 'amazon',
        'country': 'us',
        'topic': 'search_results',  # Using 'search_results' topic
        'key': 'term',  # Using 'term' as the key
        'values': search_term,  # The search term entered by the user
    }

    try:
        response = requests.post(endpoint, data=payload)
        response.raise_for_status()
        data = response.json()

        if 'job_id' in data:
            return data['job_id']
        else:
            print(f"Job creation failed: {data}")
            return None
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request exception occurred: {req_err}")
    return None

def fetch_search_results(results_url):
    """
    Fetches and parses the search results from a finished job.
    """
    try:
        response = requests.get(results_url)
        response.raise_for_status()
        data = response.json()

        products = []
        if 'results' in data and len(data['results']) > 0:
            for result in data['results']:
                # Access the `content` key and extract the `search_results` array
                search_results = result.get('content', {}).get('search_results', [])

                # Iterate over the search results and extract relevant fields
                for product in search_results:
                    products.append({
                        'name': product.get('name', 'N/A'),
                        'price': product.get('min_price', 'N/A'),
                        'url': product.get('url', 'N/A'),
                        'rating': product.get('review_rating', 'N/A'),
                        'reviews': product.get('review_count', 'N/A'),
                        'image_url': product.get('image_url', 'https://via.placeholder.com/150'),
                    })
        return products
    except requests.RequestException as e:
        print(f"Error fetching search results from PriceAPI: {e}")
        return []


def search_products_by_term(search_term):
    """
    Orchestrates the process of creating a search job, polling job status, and retrieving search results.
    """
    # Create a search job using the search term
    job_id = create_search_job(search_term)
    if not job_id:
        return []

    # Poll the job status until it's finished
    results_url = poll_job_status(job_id)
    if not results_url:
        return []

    # Fetch and return the search results
    search_results = fetch_search_results(results_url)
    return search_results
