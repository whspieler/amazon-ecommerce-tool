import requests
import time
import json

API_KEY = 'MAREZOKQLLDVUQHSXPBEAVZDRKPOHXWRHFXWPTYZPPIKPBFQSVAICKHPOAVQNNIH'
BASE_URL = 'https://api.priceapi.com/v2/'

def extract_asin(url):
    """
    Extracts the ASIN from a given Amazon product URL.
    """
    try:
        asin = url.split('/dp/')[1].split('/')[0].split('?')[0]
        return asin
    except IndexError:
        print("Failed to extract ASIN from the URL.")
        return None

def create_job(asin):
    """
    Creates a job to retrieve product data for a specific ASIN from PriceAPI.
    """
    endpoint = BASE_URL + 'jobs'
    payload = {
        'token': API_KEY,
        'source': 'amazon',
        'country': 'us',
        'topic': 'product_and_offers',
        'key': 'asin',
        'values': asin,
        'max_age': 0,
        'max_pages': 1
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
    except requests.RequestException as e:
        print(f"Error creating job with PriceAPI: {e}")
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

        if 'results' in data and len(data['results']) > 0:
            target_product = data['results'][0].get('content', {})
            carousels = data['results'][0].get('content', {}).get('carousels', [])
            
            comparison_data = []

            # Include the target product in the comparison
            if target_product:
                comparison_data.append({
                    'name': target_product.get('name'),
                    'price': target_product.get('buybox', {}).get('min_price'),
                    'url': target_product.get('url'),
                    'rating': target_product.get('review_rating'),
                    'reviews': target_product.get('review_count'),
                    'type': 'target'  # To identify the target product
                })

            # Add similar products to the comparison
            for carousel in carousels:
                for product in carousel.get('products', []):
                    comparison_data.append({
                        'name': product.get('name'),
                        'price': product.get('min_price'),
                        'url': product.get('url'),
                        'rating': None,  # You may not have ratings for similar products
                        'reviews': None,  # You may not have reviews for similar products
                        'type': 'similar'  # To identify similar products
                    })

            return comparison_data
        else:
            print("Unexpected results format.")
            return []
    except requests.RequestException as e:
        print(f"Error fetching results from PriceAPI: {e}")
        return []
    except ValueError as e:
        print(f"Error parsing JSON response: {e}")
        return []

def compare_product(asin):
    """
    Orchestrates the process of creating a job, polling job status, and retrieving product comparison data.
    """
    job_id = create_job(asin)
    if not job_id:
        print("Failed to create job on PriceAPI.")
        return []

    results_url = poll_job_status(job_id)
    if not results_url:
        print("Failed to retrieve results URL from PriceAPI.")
        return []

    return fetch_results(results_url)

# Example usage
if __name__ == "__main__":
    product_url = "https://www.amazon.com/dp/B08N5WRWNW"
    asin = extract_asin(product_url)
    if asin:
        comparison_data = compare_product(asin)
        if comparison_data:
            for product in comparison_data:
                print(f"Product Name: {product['name']}, Price: {product['price']}, URL: {product['url']}, Type: {product['type']}")
        else:
            print("Failed to retrieve comparison data.")
    else:
        print("Invalid Amazon URL provided.")
