document.addEventListener('DOMContentLoaded', function () {
    const products = [
        { id: 'dual-start', price: '19.00' },
        { id: 'dual-progress', price: '29.00' },
        { id: 'dual-advanced', price: '36.00' },
        { id: 'dual-full-access', price: '49.00' }
    ];

    function renderPayPalButtons() {
        if (typeof paypal === 'undefined') {
            console.log('PayPal SDK not loaded, retrying...');
            setTimeout(renderPayPalButtons, 500);
            return;
        }
        console.log('PayPal SDK loaded, rendering buttons...');

        products.forEach(product => {
            const container = document.getElementById(`paypal-${product.id}`);
            if (container) {
                paypal.Buttons({
                    createOrder: function(data, actions) {
                        return actions.order.create({
                            purchase_units: [{
                                amount: {
                                    value: product.price
                                }
                            }]
                        });
                    }
                }).render(container).catch(err => console.error(`Error rendering PayPal button for ${product.id}:`, err));
            }
        });
    }

    renderPayPalButtons();
});
