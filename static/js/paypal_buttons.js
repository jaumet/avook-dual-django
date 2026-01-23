/**
 * Renders a link-based PayPal button by fetching a payment link from the backend.
 * @param {string} target - The CSS selector for the button container.
 * @param {string} name - The product name (for display/logging).
 * @param {string|number} price - The product price.
 * @param {string} machineName - The product machine name/SKU.
 * @param {string} successUrl - (Not used directly here as it's handled by the backend link)
 * @param {string|number} userId - The ID of the authenticated user.
 * @param {string|number} productId - The database ID of the product.
 */
async function renderLinkButton(target, name, price, machineName, successUrl, userId, productId) {
    const targetElement = document.querySelector(target);
    if (!targetElement) {
        console.warn(`PayPal target element not found: ${target}`);
        return;
    }

    // Show a loading state
    targetElement.innerHTML = '<div class="paypal-loading">Loading PayPal...</div>';

    try {
        // Fetch the payment link from our backend
        // Note: we use productId here to call the backend view
        const response = await fetch(`/paypal/create-link/${productId}/`);
        const data = await response.json();

        if (data.payment_link) {
            // Render a styled link that looks like a PayPal button
            targetElement.innerHTML = `
                <a href="${data.payment_link}" class="paypal-link-button" title="Pay with PayPal">
                    <img src="https://www.paypalobjects.com/webstatic/en_US/i/buttons/checkout-logo-medium.png" alt="Check out with PayPal" />
                </a>
            `;

            // Add some basic styling if not already present
            if (!document.getElementById('paypal-link-styles')) {
                const style = document.createElement('style');
                style.id = 'paypal-link-styles';
                style.innerHTML = `
                    .paypal-link-button {
                        display: inline-block;
                        max-width: 100%;
                        transition: opacity 0.2s;
                    }
                    .paypal-link-button:hover {
                        opacity: 0.9;
                    }
                    .paypal-link-button img {
                        max-width: 200px;
                        display: block;
                    }
                    .paypal-loading {
                        font-size: 0.9rem;
                        color: #666;
                        font-style: italic;
                    }
                `;
                document.head.appendChild(style);
            }
        } else {
            targetElement.innerHTML = '<p class="text-danger">Error loading payment link.</p>';
            console.error('Error fetching payment link:', data.error);
        }
    } catch (error) {
        targetElement.innerHTML = '<p class="text-danger">Error connecting to payment service.</p>';
        console.error('Fetch error:', error);
    }
}

// Compatibility wrapper for old renderButton calls if any remain
function renderButton(target, name, price, productCode, successUrl, userId) {
    console.warn("renderButton is deprecated. Use renderLinkButton instead.");
    // We try to find the product ID from the container if we can,
    // but in the templates we will update the calls to pass the ID.
    // For now, this is just a placeholder.
}
