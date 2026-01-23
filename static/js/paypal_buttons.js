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
    console.log(`Initializing PayPal button for product ID: ${productId}, target: ${target}`);

    const targetElement = document.querySelector(target);
    if (!targetElement) {
        console.error(`PayPal target element not found: ${target}`);
        // Attempt fallback if target is an ID
        if (target.startsWith('#')) {
            const fallbackId = target.substring(1);
            const fallbackElement = document.getElementById(fallbackId);
            if (fallbackElement) {
                console.log(`Found element via getElementById fallback: ${fallbackId}`);
                return renderLinkButton(fallbackElement, name, price, machineName, successUrl, userId, productId);
            }
        }
        return;
    }

    // If target is an element object, we can use it directly
    const container = (typeof target === 'string') ? targetElement : target;

    // Show a loading state
    container.innerHTML = '<div class="paypal-loading">Loading PayPal...</div>';

    try {
        console.log(`Fetching payment link for product ${productId}...`);
        // Fetch the payment link from our backend
        const response = await fetch(`/paypal/create-link/${productId}/`);

        if (!response.ok) {
            throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        if (data.payment_link) {
            console.log(`Payment link received for product ${productId}. Rendering button.`);
            // Render a styled link that looks like a PayPal button
            container.innerHTML = `
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
                        margin: 10px 0;
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
                        margin: 10px 0;
                    }
                `;
                document.head.appendChild(style);
            }
        } else {
            container.innerHTML = '<p class="text-danger">Error loading payment link.</p>';
            console.error(`Error fetching payment link for product ${productId}:`, data.error);
        }
    } catch (error) {
        container.innerHTML = '<p class="text-danger">Error connecting to payment service.</p>';
        console.error(`Fetch error for product ${productId}:`, error);
    }
}

// Compatibility wrapper for old renderButton calls if any remain
function renderButton(target, name, price, productCode, successUrl, userId) {
    console.warn("renderButton is deprecated. Use renderLinkButton instead.");
}
