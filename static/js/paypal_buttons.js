
document.addEventListener('DOMContentLoaded', function () {
  function renderPayPalButtons() {
    if (typeof paypal === 'undefined') {
      console.log('PayPal SDK not loaded, retrying...');
      setTimeout(renderPayPalButtons, 500);
      return;
    }
    console.log('PayPal SDK loaded, rendering buttons...');

    paypal.Buttons({
      createOrder: function(data, actions) {
        return actions.order.create({
          purchase_units: [{
            amount: {
              value: '39.99'
            }
          }]
        });
      }
    }).render('#paypal-dual-start').catch(err => console.error('Error rendering PayPal button for start:', err));

    paypal.Buttons({
      createOrder: function(data, actions) {
        return actions.order.create({
          purchase_units: [{
            amount: {
              value: '39.99'
            }
          }]
        });
      }
    }).render('#paypal-dual-progress').catch(err => console.error('Error rendering PayPal button for progress:', err));

    paypal.Buttons({
      createOrder: function(data, actions) {
        return actions.order.create({
          purchase_units: [{
            amount: {
              value: '39.99'
            }
          }]
        });
      }
    }).render('#paypal-dual-advanced').catch(err => console.error('Error rendering PayPal button for advanced:', err));

    paypal.Buttons({
      createOrder: function(data, actions) {
        return actions.order.create({
          purchase_units: [{
            amount: {
              value: '59.99'
            }
          }]
        });
      }
    }).render('#paypal-dual-full').catch(err => console.error('Error rendering PayPal button for full:', err));
  }

  renderPayPalButtons();
});
