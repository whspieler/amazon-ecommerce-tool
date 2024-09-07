from flask import Flask, request, jsonify, render_template
from scraper import compare_product, extract_id, analyze_product_with_groq  # Updated import to include analysis
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

            # Return the comparison and analysis data to the frontend
            return jsonify({'comparison': comparison_data})
        else:
            return jsonify({'error': 'Failed to retrieve comparison data'}), 500
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({'error': 'An error occurred while processing your request.'}), 500

if __name__ == "__main__":
    app.run(debug=True)
