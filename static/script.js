document.getElementById('url-form').addEventListener('submit', async function (event) {
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
        if (data.comparison && data.comparison.length > 0) {
            clearPreviousContent();  // Clear any previous product or comparison content
            displayOriginalProduct(data.comparison[0]); // Display the original product first
            displayToggleableComparison(data.comparison.slice(1)); // Display other products toggleable
            displayProductAnalysis(data.comparison); // Display product analysis (new feature)

            // Display reviews summary using Gemini API
            if (data.reviews_summary) {
                displayReviewsSummary(data.reviews_summary); // Display the new review summary feature
            }

            // Show "Your Product" section
            document.querySelector('.original-product-section').style.display = 'block';
        } else {
            alert('No comparison data found.');
        }

    } catch (error) {
        console.error('Error:', error);
        alert('Failed to compare products. Please check the console for more details.');
    } finally {
        // Hide loading indicator
        document.getElementById('loading-indicator').style.display = 'none';
    }
});

// Function to clear out previous content to prevent duplication
function clearPreviousContent() {
    const comparisonContainer = document.getElementById('comparison-container');
    const originalProductSection = document.getElementById('original-product');
    const analysisSection = document.getElementById('analysis-container');
    const reviewsContainer = document.getElementById('reviews-container'); // Added for review summary
    comparisonContainer.innerHTML = '';  // Clear other products
    originalProductSection.innerHTML = ''; // Clear original product content
    analysisSection.innerHTML = ''; // Clear previous analysis content
    reviewsContainer.innerHTML = ''; // Clear review summary content

    // Only remove the toggle box if it already exists to avoid duplicates
    const existingToggleBox = document.querySelector('.toggle-box');
    if (existingToggleBox) {
        existingToggleBox.remove();
    }
}

function displayOriginalProduct(product) {
    const originalProductSection = document.getElementById('original-product');
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
    price.innerText = `Price: $${product.price ?? 'N/A'}`;

    const rating = document.createElement('p');
    rating.innerText = `Rating: ${product.rating ? product.rating + ' / 100' : 'N/A'}`;

    const reviews = document.createElement('p');
    reviews.innerText = `Reviews: ${product.reviews ? product.reviews : 'N/A'}`;

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

    // Display only the summarized key features (3 bullet points)
    if (product.features_summary && product.features_summary.length > 0) {
        const summaryTitle = document.createElement('p');
        summaryTitle.innerText = 'Key Features:';
        summaryTitle.style.fontWeight = 'bold';

        const summaryList = document.createElement('ul');
        product.features_summary.forEach(summary => {
            const summaryItem = document.createElement('li');
            summaryItem.innerText = summary;
            summaryList.appendChild(summaryItem);
        });

        productDiv.appendChild(summaryTitle);
        productDiv.appendChild(summaryList);
    }

    productDiv.appendChild(name);
    productDiv.appendChild(price);
    productDiv.appendChild(rating);
    productDiv.appendChild(reviews);
    productDiv.appendChild(dimensions);
    productDiv.appendChild(availability);
    productDiv.appendChild(deliveryInfo);
    productDiv.appendChild(brand);
    productDiv.appendChild(link);

    originalProductSection.appendChild(productDiv);
}

function displayToggleableComparison(comparison) {
    const comparisonContainer = document.getElementById('comparison-container');
    
    // Clear previous comparison to avoid duplicating products
    comparisonContainer.innerHTML = '';

    // Create the toggle box if it doesn't exist already
    let toggleBox = document.querySelector('.toggle-box');
    if (!toggleBox) {
        toggleBox = document.createElement('div');
        toggleBox.classList.add('toggle-box');
    
        const toggleHeader = document.createElement('div');
        toggleHeader.classList.add('toggle-header');
        toggleHeader.innerText = 'Other Products You Should Consider:';
    
        // Add arrow icon
        const arrow = document.createElement('span');
        arrow.innerHTML = '▼';
        arrow.classList.add('toggle-arrow');
        toggleHeader.appendChild(arrow);
    
        // Add the header to the toggleBox
        toggleBox.appendChild(toggleHeader);
    
        // Add the toggleBox before the other products container
        comparisonContainer.parentNode.insertBefore(toggleBox, comparisonContainer);
    
        // Initially hide the comparison container
        comparisonContainer.style.display = 'none';

        // Toggle event to show/hide other products
        toggleHeader.addEventListener('click', function () {
            if (comparisonContainer.style.display === 'none') {
                comparisonContainer.style.display = 'grid';
                arrow.innerHTML = '▲'; // Change arrow direction
            } else {
                comparisonContainer.style.display = 'none';
                arrow.innerHTML = '▼'; // Change arrow direction
            }
        });
    }

    // Create a container to hold the other products
    const otherProductsContainer = document.createElement('div');
    otherProductsContainer.classList.add('other-products');
    otherProductsContainer.style.display = 'grid'; // Set it to grid for displaying

    comparison.forEach(product => {
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
        price.innerText = `Price: $${product.price ?? 'N/A'}`;

        const rating = document.createElement('p');
        rating.innerText = `Rating: ${product.rating ? product.rating + ' / 100' : 'N/A'}`;

        const reviews = document.createElement('p');
        reviews.innerText = `Reviews: ${product.reviews ? product.reviews : 'N/A'}`;

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

        // Display only the summarized key features (3 bullet points)
        if (product.features_summary && product.features_summary.length > 0) {
            const summaryTitle = document.createElement('p');
            summaryTitle.innerText = 'Key Features:';
            summaryTitle.style.fontWeight = 'bold';

            const summaryList = document.createElement('ul');
            product.features_summary.forEach(summary => {
                const summaryItem = document.createElement('li');
                summaryItem.innerText = summary;
                summaryList.appendChild(summaryItem);
            });

            productDiv.appendChild(summaryTitle);
            productDiv.appendChild(summaryList);
        }

        productDiv.appendChild(name);
        productDiv.appendChild(price);
        productDiv.appendChild(rating);
        productDiv.appendChild(reviews);
        productDiv.appendChild(dimensions);
        productDiv.appendChild(availability);
        productDiv.appendChild(deliveryInfo);
        productDiv.appendChild(brand);
        productDiv.appendChild(link);

        otherProductsContainer.appendChild(productDiv);
    });

    // Add the product container to the comparison container
    comparisonContainer.appendChild(otherProductsContainer);
}

// New function to display product analysis
function displayProductAnalysis(comparison) {
    const analysisContainer = document.getElementById('analysis-container');

    // Create a toggle box for the analysis section
    let analysisToggleBox = document.querySelector('.analysis-toggle-box');
    if (!analysisToggleBox) {
        analysisToggleBox = document.createElement('div');
        analysisToggleBox.classList.add('analysis-toggle-box');

        const toggleHeader = document.createElement('div');
        toggleHeader.classList.add('toggle-header');
        toggleHeader.innerText = 'Which Product is Best For You?';

        // Add arrow icon
        const arrow = document.createElement('span');
        arrow.innerHTML = '▼';
        arrow.classList.add('toggle-arrow');
        toggleHeader.appendChild(arrow);

        // Add the header to the toggleBox
        analysisToggleBox.appendChild(toggleHeader);

        // Add the toggleBox before the analysis container
        analysisContainer.parentNode.insertBefore(analysisToggleBox, analysisContainer);

        // Initially hide the analysis container
        analysisContainer.style.display = 'none';

        // Toggle event to show/hide analysis
        toggleHeader.addEventListener('click', function () {
            if (analysisContainer.style.display === 'none') {
                analysisContainer.style.display = 'block';
                arrow.innerHTML = '▲'; // Change arrow direction
            } else {
                analysisContainer.style.display = 'none';
                arrow.innerHTML = '▼'; // Change arrow direction
            }
        });
    }

    // Clear previous content
    analysisContainer.innerHTML = '';

    // Create analysis details for each product
    comparison.forEach(product => {
        const analysisDiv = document.createElement('div');
        analysisDiv.classList.add('analysis-product');

        const name = document.createElement('h3');
        name.innerText = `${product.name}: Pros and Cons`;

        const analysisText = document.createElement('p');
        analysisText.innerText = product.analysis || 'No analysis available.';

        analysisDiv.appendChild(name);
        analysisDiv.appendChild(analysisText);

        analysisContainer.appendChild(analysisDiv);
    });
}

// New function to display reviews summary from Gemini API
function displayReviewsSummary(reviews) {
    const reviewsContainer = document.getElementById('reviews-container');

    // Create a toggle box for the reviews section
    let reviewsToggleBox = document.querySelector('.reviews-toggle-box');
    if (!reviewsToggleBox) {
        reviewsToggleBox = document.createElement('div');
        reviewsToggleBox.classList.add('reviews-toggle-box');

        const toggleHeader = document.createElement('div');
        toggleHeader.classList.add('toggle-header');
        toggleHeader.innerText = 'What Do Others Think?';

        // Add arrow icon
        const arrow = document.createElement('span');
        arrow.innerHTML = '▼';
        arrow.classList.add('toggle-arrow');
        toggleHeader.appendChild(arrow);

        reviewsToggleBox.appendChild(toggleHeader);
        reviewsContainer.parentNode.insertBefore(reviewsToggleBox, reviewsContainer);

        reviewsContainer.style.display = 'none';

        // Toggle event to show/hide reviews summary
        toggleHeader.addEventListener('click', function () {
            if (reviewsContainer.style.display === 'none') {
                reviewsContainer.style.display = 'block';
                arrow.innerHTML = '▲';
            } else {
                reviewsContainer.style.display = 'none';
                arrow.innerHTML = '▼';
            }
        });
    }

    reviewsContainer.innerHTML = '';
    reviews.forEach(product => {
        const reviewDiv = document.createElement('div');
        reviewDiv.classList.add('review-product');

        const name = document.createElement('h3');
        name.innerText = `${product.name}: Review Summary`;

        const reviewText = document.createElement('p');
        reviewText.innerText = product.review_summary || 'No reviews available.';

        reviewDiv.appendChild(name);
        reviewDiv.appendChild(reviewText);
        reviewsContainer.appendChild(reviewDiv);
    });
}
