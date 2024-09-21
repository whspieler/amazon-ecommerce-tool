
# **Amazon E-Commerce Tool**

## **Project Overview**

The Amazon E-Commerce Tool is a web-based application designed to help users compare Amazon products, analyze customer reviews, and find similar products based on user input. This tool uses APIs to fetch and analyze product data, providing users with detailed product information, including key features, pricing, and availability, to make well-informed purchase decisions.

## **Key Features**

- **Amazon Product Comparison:** Users can input an Amazon product URL to compare the product with similar items, displaying essential details like price, rating, and availability.
  
- **Review Summarization:** The tool provides a concise summary of customer reviews, highlighting what users like and dislike about each product.

- **Didn't Find What You’re Looking For:** Allows users to input product requirements and returns suggestions for products that match their criteria.

- **Key Feature Summarization:** The tool summarizes the most important product features into three concise bullet points.

- **Product Analysis:** The tool offers an analysis of each product’s pros and cons, making it easier for users to identify which product best suits their needs.

## **How It Works**

1. **Input Amazon Product URL**:  
   - The user inputs an Amazon product URL and clicks "Compare Products."

2. **API Integration**:
   - The application fetches product data, reviews, and features using PriceAPI and Groq API for comparisons and Gemini API for review summaries.

3. **Comparison & Display**:
   - The tool compares the user’s product with other similar products.
   - It generates a detailed analysis of the products, summarizes key features, and provides review summaries for each.

4. **Search for More Products**:  
   - If the user is not satisfied with the results, they can use the “Didn’t Find What You’re Looking For” feature to input specific product needs, and the tool will search for suitable products.

## **Technologies Used**

- **HTML5**: Structure of the webpage.
- **CSS3**: Styling and layout of the page.
- **JavaScript**: Handles product comparison, review analysis, and feature summarization.
- **APIs**: 
  - **PriceAPI**: For retrieving product information.
  - **Groq API**: For summarizing product features and analyzing pros and cons.
  - **Gemini API**: For customer review summarization.

## **How to Run the Project**

1. **Clone the Repository**:
   ```
   git clone https://github.com/whspieler/amazon-ecommerce-tool.git
   ```

2. **Install Dependencies**:
   Navigate to the project folder and install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```
   python app.py
   ```

4. **Access the Tool**:
   - Open your web browser and go to `http://127.0.0.1:5000`.
   - Input an Amazon product URL to compare products or search for alternatives.


## **Screenshots**

1. **Homepage**: <br />
   <img width="400" alt="Screenshot 2024-09-20 at 4 55 28 PM" src="https://github.com/user-attachments/assets/5d362bb3-5298-4ec9-8c5c-d1dc6b66c414">
   
2. **Product Display**: <br />
    <img width="400" alt="Screenshot 2024-09-20 at 4 57 29 PM" src="https://github.com/user-attachments/assets/bb0e2d6c-89cf-495d-a23f-962620314e05">

3. **Other Products You Should Consider Feature**: <br />
    <img width="400" alt="Screenshot 2024-09-20 at 4 58 23 PM" src="https://github.com/user-attachments/assets/6d1c0528-776c-4085-90de-8409f8d5f689">

4. **Which Product Is Best For You Feature**: <br />
    <img width="400" alt="Screenshot 2024-09-20 at 5 01 42 PM" src="https://github.com/user-attachments/assets/91c7f2e0-8e8d-4436-b2a8-500345a79811">

5. **What Do Others Think Feature**: <br />

    <img width="400" alt="Screenshot 2024-09-20 at 5 02 35 PM" src="https://github.com/user-attachments/assets/7e94397d-3317-48c6-b9ea-9ffc1ddfbcbd">

6. **Didn't Find What You're Looking For Feature**: <br />

    <img width="400" alt="Screenshot 2024-09-20 at 5 03 06 PM" src="https://github.com/user-attachments/assets/56e572bd-3ec9-4373-b4bf-23cacc66de3c">
    <br />
    <img width="400" alt="Screenshot 2024-09-20 at 5 03 52 PM" src="https://github.com/user-attachments/assets/baccfcbf-c4ba-4917-b50f-071d28113991">


