from flask import Flask, request, jsonify, render_template
from scraper import compare_product, extract_id, analyze_product_with_groq, analyze_reviews_with_gemini, search_products_by_term, summarize_product_features_with_gemini  # Updated import
from database import insert_comparison, create_database
import sqlite3

app = Flask(__name__)

# Initialize the database
create_database()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compare_products', methods=['POST'])
def compare_products():
    try:
        data = request.json
        url = data['url']
        product_id = extract_id(url)  # Use extract_id instead of extract_asin

        # Get comparison data using PriceAPI
        comparison_data = compare_product(product_id)
        
        if comparison_data:
            # Optionally, save the comparison data to a database
            for product in comparison_data:
                if product['type'] == 'target':  # Only save the target product's price
                    insert_comparison(product_id, product['price'])
            
            # Generate the analysis for each product using the Groq API
            for product in comparison_data:
                product['analysis'] = analyze_product_with_groq(product)  # Perform analysis for each product

            # Generate the reviews summary for each product using Gemini API
            reviews_summary = analyze_reviews_with_gemini(comparison_data)

            # Return the comparison, analysis, and reviews data to the frontend
            return jsonify({
                'comparison': comparison_data,
                'reviews_summary': reviews_summary
            })
        else:
            return jsonify({'error': 'Failed to retrieve comparison data'}), 500
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({'error': 'An error occurred while processing your request.'}), 500

# New route for the "Didn't Find What You're Looking For?" feature
@app.route('/price-api/search', methods=['POST'])
def search_products():
    try:
        data = request.json
        search_term = data.get('values', None)

        if not search_term:
            return jsonify({'error': 'No search term provided'}), 400

        # Use scraper.py's search_products_by_term function to search products
        search_results = search_products_by_term(search_term)

        # Summarize key features using Gemini for each product
        for product in search_results:
            product['key_features'] = summarize_product_features_with_gemini(product['url'])

        if search_results:
            return jsonify({'products': search_results})
        else:
            return jsonify({'error': 'No products found for the given search term'}), 500

    except Exception as e:
        print(f"Error occurred while searching for products: {e}")
        return jsonify({'error': 'An error occurred while processing your search request.'}), 500

if __name__ == "__main__":
    app.run(debug=True)
