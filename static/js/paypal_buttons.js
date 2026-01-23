/**
 * Renders a PayPal button for a specific product.
 * @param {string} target - The CSS selector for the button container.
 * @param {string} name - The product name.
 * @param {string|number} price - The product price.
 * @param {string} productCode - The product machine name/SKU.
 * @param {string} successUrl - The URL to redirect to on success.
 * @param {string|number} userId - The ID of the authenticated user.
 */
function renderButton(target, name, price, productCode, successUrl, userId) {
  // Ensure we have a valid target element
  const targetElement = document.querySelector(target);
  if (!targetElement) {
    console.warn(`PayPal target element not found: ${target}`);
    return;
  }

  // Ensure price is formatted correctly for PayPal (dot as decimal separator)
  const formattedPrice = price.toString().replace(',', '.');

  // Check if PayPal SDK is loaded
  if (typeof paypal === 'undefined') {
    console.error('PayPal SDK not loaded.');
    return;
  }

  paypal.Buttons({
    style: {
      layout: 'vertical',
      color: 'gold',
      shape: 'rect',
      label: 'paypal'
    },

    createOrder: function(data, actions) {
      return actions.order.create({
        purchase_units: [{
          description: name,
          custom_id: userId.toString(),
          amount: {
            currency_code: 'EUR',
            value: formattedPrice,
            breakdown: {
              item_total: {
                currency_code: 'EUR',
                value: formattedPrice
              }
            }
          },
          items: [{
            name: name,
            sku: productCode,
            unit_amount: {
              currency_code: 'EUR',
              value: formattedPrice
            },
            quantity: "1"
          }]
        }]
      });
    },

    onApprove: function(data, actions) {
      return actions.order.capture().then(function(details) {
        window.location.href =
          successUrl + "?product=" + productCode +
          "&order=" + data.orderID;
      });
    },

    onError: function(err) {
      // Log to console instead of alerting the user to avoid disruptive UX on page load failures
      console.error('PayPal Error for product ' + productCode + ':', err);
    }

  }).render(target);
}
