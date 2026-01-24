/**
 * Renders a link-based PayPal button by fetching a payment link from the backend.
 * This approach uses the "Payment Links and Buttons API" as specified in the manual.
 *
 * @param {string|HTMLElement} target - The CSS selector for the button container or the element itself.
 * @param {string} name - The product name (for display/logging).
 * @param {string|number} price - The product price.
 * @param {string} machineName - The product machine name/SKU.
 * @param {string} successUrl - URL to redirect after successful payment (handled by backend).
 * @param {string|number} userId - The ID of the authenticated user.
 * @param {string|number} productId - The database ID of the product.
 */
async function renderLinkButton(target, name, price, machineName, successUrl, userId, productId) {
    console.log(`Initializing PayPal button for product ID: ${productId}`);

    let container;
    if (typeof target === 'string') {
        container = document.querySelector(target);
        if (!container && target.startsWith('#')) {
            container = document.getElementById(target.substring(1));
        }
    } else if (target instanceof HTMLElement) {
        container = target;
    }

    if (!container) {
        console.error(`PayPal target element not found:`, target);
        return;
    }

    // Show a loading state with a spinner look if possible, or just text
    container.innerHTML = '<div class="paypal-loading">Carregant PayPal...</div>';

    // Inject styles if they don't exist
    if (!document.getElementById('paypal-link-styles')) {
        const style = document.createElement('style');
        style.id = 'paypal-link-styles';
        style.innerHTML = `
            .paypal-link-button {
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: #ffc439;
                border-radius: 4px;
                padding: 10px 24px;
                text-decoration: none;
                transition: background-color 0.2s, transform 0.1s;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                min-width: 200px;
                max-width: 300px;
                margin: 10px 0;
            }
            .paypal-link-button:hover {
                background-color: #f2ba36;
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }
            .paypal-link-button:active {
                transform: translateY(0);
            }
            .paypal-link-button img {
                height: 24px;
                width: auto;
                display: block;
            }
            .paypal-loading {
                display: inline-block;
                padding: 10px;
                font-size: 0.9rem;
                color: #666;
                font-style: italic;
            }
            .paypal-error-msg {
                color: #dc3545;
                font-size: 0.85rem;
                margin-top: 5px;
                padding: 8px;
                border: 1px solid #f5c6cb;
                border-radius: 4px;
                background-color: #f8d7da;
            }
        `;
        document.head.appendChild(style);
    }

    try {
        const response = await fetch(`/paypal/create-link/${productId}/`);

        if (!response.ok) {
            let errorText = "Error del servidor";
            try {
                const errorData = await response.json();
                errorText = errorData.error || errorText;
            } catch (e) {}
            throw new Error(errorText);
        }

        const data = await response.json();

        if (data.payment_link) {
            // Use the official PayPal Logo SVG or a high-quality PNG
            container.innerHTML = `
                <a href="${data.payment_link}" class="paypal-link-button" title="Pagar amb PayPal">
                    <img src="https://www.paypalobjects.com/webstatic/en_US/i/buttons/checkout-logo-medium.png" alt="PayPal Checkout" />
                </a>
            `;
        } else {
            throw new Error("No s'ha pogut generar l'enllaç de pagament.");
        }
    } catch (error) {
        console.error(`Error rendering PayPal button for product ${productId}:`, error);
        container.innerHTML = `<div class="paypal-error-msg"><strong>Error:</strong> ${error.message}. Si us plau, torna-ho a provar més tard.</div>`;
    }
}

// Fallback for legacy calls
function renderButton(target, name, price, productCode, successUrl, userId) {
    console.warn("renderButton is deprecated. Use renderLinkButton instead.");
}
