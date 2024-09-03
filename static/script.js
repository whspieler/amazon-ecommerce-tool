document.getElementById('url-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const url = document.getElementById('url-input').value;

    // Show loading indicator
    document.getElementById('loading-indicator').style.display = 'block';

    try {
        // Send a POST request to the server with the Amazon URL
        const response = await fetch('/compare_products', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: url })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        // Check if data contains the expected properties
        if (data.comparison) {
            displayComparison(data.comparison);
        } else {
            throw new Error('Unexpected response structure');
        }

    } catch (error) {
        console.error('Error:', error);
        alert('Failed to compare products. Please check the console for more details.');
    } finally {
        // Hide loading indicator
        document.getElementById('loading-indicator').style.display = 'none';
    }
});

function displayComparison(comparison) {
    const comparisonContainer = document.getElementById('comparison-container');
    comparisonContainer.innerHTML = ''; // Clear any existing content

    comparison.forEach(product => {
        const productDiv = document.createElement('div');
        productDiv.classList.add('product');

        const name = document.createElement('h3');
        name.innerText = product.name;

        const price = document.createElement('p');
        price.innerText = `Price: $${product.price}`;

        const rating = document.createElement('p');
        rating.innerText = `Rating: ${product.rating ? product.rating + ' / 100' : 'N/A'}`;

        const reviews = document.createElement('p');
        reviews.innerText = `Reviews: ${product.reviews ? product.reviews : 'N/A'}`;

        const link = document.createElement('a');
        link.href = product.url;
        link.innerText = "View Product";
        link.target = "_blank";

        productDiv.appendChild(name);
        productDiv.appendChild(price);
        productDiv.appendChild(rating);
        productDiv.appendChild(reviews);
        productDiv.appendChild(link);

        comparisonContainer.appendChild(productDiv);
    });
}
