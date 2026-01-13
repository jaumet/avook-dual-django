function renderButton(target, name, price, productCode, successUrl) {
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
          amount: {
            value: price
          }
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
