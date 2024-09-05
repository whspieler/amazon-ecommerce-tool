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

    // Filter products to show only those with complete information
    const filteredComparison = comparison.filter(product => product.rating && product.reviews);

    filteredComparison.forEach(product => {
        const productDiv = document.createElement('div');
        productDiv.classList.add('product');

        // Display product image if available
        if (product.image_url) {
            const image = document.createElement('img');
            image.src = product.image_url;
            image.alt = product.name;
            image.classList.add('product-image');
            productDiv.appendChild(image);
        }

        const name = document.createElement('h3');
        name.innerText = product.name;

        const price = document.createElement('p');
        price.innerText = `Price: $${product.price}`;

        const rating = document.createElement('p');
        rating.innerText = `Rating: ${product.rating ? product.rating + ' / 100' : 'N/A'}`;

        const reviews = document.createElement('p');
        reviews.innerText = `Reviews: ${product.reviews ? product.reviews : 'N/A'}`;

        // Display product features if available
        if (product.features && product.features.length > 0) {
            const featuresTitle = document.createElement('p');
            featuresTitle.innerText = 'Features:';
            featuresTitle.style.fontWeight = 'bold';

            const featuresList = document.createElement('ul');
            product.features.forEach(feature => {
                const featureItem = document.createElement('li');
                featureItem.innerText = feature;
                featuresList.appendChild(featureItem);
            });

            productDiv.appendChild(featuresTitle);
            productDiv.appendChild(featuresList);
        }

        // Display additional product details if available
        const dimensions = document.createElement('p');
        dimensions.innerText = `Dimensions: ${product.dimensions || 'N/A'}`;

        const availability = document.createElement('p');
        availability.innerText = `Availability: ${product.availability || 'N/A'}`;

        const deliveryInfo = document.createElement('p');
        deliveryInfo.innerText = `Delivery Info: ${product.delivery_info || 'N/A'}`;

        const brand = document.createElement('p');
        brand.innerText = `Brand: ${product.brand || 'N/A'}`;

        const link = document.createElement('a');
        link.href = product.url;
        link.innerText = "View Product";
        link.target = "_blank";

        // Append all elements to the productDiv
        productDiv.appendChild(name);
        productDiv.appendChild(price);
        productDiv.appendChild(rating);
        productDiv.appendChild(reviews);
        productDiv.appendChild(dimensions);
        productDiv.appendChild(availability);
        productDiv.appendChild(deliveryInfo);
        productDiv.appendChild(brand);
        productDiv.appendChild(link);

        comparisonContainer.appendChild(productDiv);
    });

    // Display message if no products with complete information are found
    if (filteredComparison.length === 0) {
        const noResultsMessage = document.createElement('p');
        noResultsMessage.innerText = 'No products with complete information available for comparison.';
        comparisonContainer.appendChild(noResultsMessage);
    }
}

// Add event listener to sort products by price
document.getElementById('sort-price').addEventListener('click', function() {
    const comparisonContainer = document.getElementById('comparison-container');
    const products = Array.from(comparisonContainer.getElementsByClassName('product'));

    products.sort((a, b) => {
        const priceA = parseFloat(a.querySelector('p:nth-child(3)').innerText.replace('Price: $', '')) || 0;
        const priceB = parseFloat(b.querySelector('p:nth-child(3)').innerText.replace('Price: $', '')) || 0;
        return priceA - priceB;
    });

    comparisonContainer.innerHTML = '';
    products.forEach(product => comparisonContainer.appendChild(product));
});

// Add event listener to sort products by rating
document.getElementById('sort-rating').addEventListener('click', function() {
    const comparisonContainer = document.getElementById('comparison-container');
    const products = Array.from(comparisonContainer.getElementsByClassName('product'));

    products.sort((a, b) => {
        const ratingA = parseFloat(a.querySelector('p:nth-child(4)').innerText.replace('Rating: ', '').replace(' / 100', '')) || 0;
        const ratingB = parseFloat(b.querySelector('p:nth-child(4)').innerText.replace('Rating: ', '').replace(' / 100', '')) || 0;
        return ratingB - ratingA;
    });

    comparisonContainer.innerHTML = '';
    products.forEach(product => comparisonContainer.appendChild(product));
});
