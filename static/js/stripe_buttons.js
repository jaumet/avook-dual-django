/**
 * Renders a Stripe Checkout button.
 *
 * @param {string|HTMLElement} target - The CSS selector for the button container or the element itself.
 * @param {string} name - The product name (for display/logging).
 * @param {string|number} productId - The database ID of the product.
 */
function renderStripeButton(target, name, productId) {
    console.log(`Initializing Stripe button for product ID: ${productId}`);

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
        console.error(`Stripe target element not found:`, target);
        return;
    }

    // Inject styles if they don't exist
    if (!document.getElementById('stripe-link-styles')) {
        const style = document.createElement('style');
        style.id = 'stripe-link-styles';
        style.innerHTML = `
            .stripe-checkout-button {
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: #6772e5;
                color: white;
                border-radius: 4px;
                padding: 10px 24px;
                text-decoration: none;
                transition: background-color 0.2s, transform 0.1s;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                min-width: 200px;
                max-width: 300px;
                margin: 10px 0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                font-weight: 600;
                border: none;
                cursor: pointer;
            }
            .stripe-checkout-button:hover {
                background-color: #5469d4;
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                color: white;
                text-decoration: none;
            }
            .stripe-checkout-button:active {
                transform: translateY(0);
            }
            .stripe-loading {
                display: inline-block;
                padding: 10px;
                font-size: 0.9rem;
                color: #666;
                font-style: italic;
            }
            .stripe-error-msg {
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

    container.innerHTML = `
        <button class="stripe-checkout-button" title="Pagar amb Targeta (Stripe)">
            Pagar amb Targeta
        </button>
    `;

    const button = container.querySelector('.stripe-checkout-button');
    button.addEventListener('click', async () => {
        button.disabled = true;
        const originalContent = button.innerHTML;
        button.innerHTML = 'Processant...';

        try {
            const response = await fetch('/stripe/create-checkout-session/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    product_id: productId
                })
            });

            if (!response.ok) {
                let errorText = 'Error al crear la sessió de Stripe';
                try {
                    const errorData = await response.json();
                    errorText = errorData.error || errorText;
                } catch (e) {}
                throw new Error(errorText);
            }

            const data = await response.json();
            if (data.url) {
                window.location.href = data.url;
            } else {
                throw new Error('No s\'ha rebut cap URL de redirecció');
            }
        } catch (error) {
            console.error('Stripe error:', error);
            // Remove previous error messages if any
            const existingError = container.querySelector('.stripe-error-msg');
            if (existingError) existingError.remove();

            container.insertAdjacentHTML('beforeend', `<div class="stripe-error-msg"><strong>Error:</strong> ${error.message}</div>`);
            button.disabled = false;
            button.innerHTML = originalContent;
        }
    });
}

// Helper to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
