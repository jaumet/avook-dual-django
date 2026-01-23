function renderButton(target, name, price, productCode, successUrl, userId) {
  const formattedPrice = price.toString().replace(',', '.');
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
      alert("Error en el pagament. Torna-ho a intentar.");
      console.error(err);
    }

  }).render(target);
}
