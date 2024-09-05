import requests
import time
import json

API_KEY = 'MAREZOKQLLDVUQHSXPBEAVZDRKPOHXWRHFXWPTYZPPIKPBFQSVAICKHPOAVQNNIH'
BASE_URL = 'https://api.priceapi.com/v2/'

def extract_id(url):
    """
    Extracts the ID (ASIN) from a given Amazon product URL.
    """
    try:
        product_id = url.split('/dp/')[1].split('/')[0].split('?')[0]
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
        response.raise_for_status()  # Will raise an HTTPError for 4xx/5xx responses
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
        additional_ids = []

        if 'results' in data and len(data['results']) > 0:
            for result in data['results']:
                content = result.get('content', {})
                
                # Include the target product in the comparison
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
                    'brand': content.get('brand_name', 'N/A'),
                    'image_url': content.get('image_url', 'N/A'),
                    'type': 'target'
                })

                # Collect additional IDs from related content
                if 'product_links' in content:
                    for link_type in ['variants', 'substitutes', 'sponsored']:
                        if content['product_links'].get(link_type):
                            additional_ids.extend(content['product_links'][link_type])

                # Collect IDs from carousels
                carousels = content.get('carousels', [])
                for carousel in carousels:
                    for product in carousel.get('products', []):
                        additional_ids.append(product['id'])

        # Remove duplicates and limit to top 4-5 additional IDs
        additional_ids = list(set(additional_ids))[:5]
        return comparison_data, additional_ids
    except requests.RequestException as e:
        print(f"Error fetching results from PriceAPI: {e}")
        return [], []
    except ValueError as e:
        print(f"Error parsing JSON response: {e}")
        return [], []

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

    comparison_data, additional_ids = fetch_results(results_url)

    # Fetch details for additional IDs, limiting to top 4-5 similar products
    if additional_ids:
        print(f"Fetching additional details for IDs: {additional_ids}")
        job_id = create_job(additional_ids)
        if job_id:
            results_url = poll_job_status(job_id)
            if results_url:
                additional_data, _ = fetch_results(results_url)
                
                # Ensure only detailed products are appended and they have necessary fields
                for product in additional_data:
                    if 'name' in product and 'price' in product and 'rating' in product and 'reviews' in product:
                        product['type'] = 'similar'  # Marking similar products
                        comparison_data.append(product)
    
    # Limit to show top 4-5 products including the original
    return comparison_data[:5]

# Example usage
if __name__ == "__main__":
    product_url = "https://www.amazon.com/dp/B08N5WRWNW"
    product_id = extract_id(product_url)
    if product_id:
        comparison_data = compare_product(product_id)
        if comparison_data:
            for product in comparison_data:
                print(f"Product Name: {product['name']}, Price: {product['price']}, URL: {product['url']}, Rating: {product.get('rating', 'N/A')}, Reviews: {product.get('reviews', 'N/A')}, Features: {product.get('features', 'N/A')}, Dimensions: {product.get('dimensions', 'N/A')}, Availability: {product.get('availability', 'N/A')}, Delivery Info: {product.get('delivery_info', 'N/A')}, Brand: {product.get('brand', 'N/A')}, Image URL: {product.get('image_url', 'N/A')}")
        else:
            print("Failed to retrieve comparison data.")
    else:
        print("Invalid Amazon URL provided.")
