import logging
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from post_office.utils import send_templated_email
from .models import UserPurchase, UserAccess

logger = logging.getLogger(__name__)

def fulfill_purchase(user, product, payment_provider, paypal_order_id=None, paypal_capture_id=None, stripe_checkout_id=None, paid_at=None):
    """
    Grants access to a product after a successful payment.
    This is used by both PayPal and Stripe webhooks.
    """
    if not paid_at:
        paid_at = timezone.now()

    # Idempotency check
    if payment_provider == 'paypal':
        # Check if already exists by either order_id or capture_id
        from django.db.models import Q
        q_obj = Q(paypal_order_id=paypal_order_id)
        if paypal_capture_id:
            q_obj |= Q(paypal_capture_id=paypal_capture_id)

        purchase_exists = UserPurchase.objects.filter(q_obj).exists()
    elif payment_provider == 'stripe':
        purchase_exists = UserPurchase.objects.filter(
            stripe_checkout_id=stripe_checkout_id
        ).exists()
    else:
        purchase_exists = False

    if purchase_exists:
        logger.info(f"Purchase already processed for {payment_provider} ID: {paypal_order_id or stripe_checkout_id}")
        return False

    # Create UserPurchase
    UserPurchase.objects.create(
        user=user,
        user_email=user.email,
        product=product,
        paypal_order_id=paypal_order_id,
        paypal_capture_id=paypal_capture_id,
        stripe_checkout_id=stripe_checkout_id,
        paid_at=paid_at,
        payment_provider=payment_provider,
        status="completed"
    )
    logger.info(f"Created UserPurchase for user {user.id} and product {product.machine_name} via {payment_provider}.")

    # Activate in UserAccess
    expiry_date = None
    if product.duration:
        expiry_date = paid_at + relativedelta(months=product.duration)

    UserAccess.objects.update_or_create(
        user=user,
        product=product,
        defaults={
            'active': True,
            'activated_at': paid_at,
            'expiry_date': expiry_date
        }
    )
    logger.info(f"Product {product.machine_name} activated for user {user.id}.")

    # Send confirmation email
    send_purchase_confirmation_email(user, product, paid_at)
    return True

def send_purchase_confirmation_email(user, product, paid_at):
    """
    Sends a purchase confirmation email in the user's language.
    """
    try:
        lang = getattr(user, 'language_code', 'ca')

        context = {
            'user': user,
            'product_name': str(product),
            'payment_date': paid_at.strftime('%d/%m/%Y %H:%M'),
            'purchase_url': f"https://dual.cat/{lang}/accounts/purchases/"
        }

        send_templated_email(
            template_name='purchase_confirmation',
            context=context,
            to_email=user.email,
            language=lang
        )
        logger.info(f"Confirmation email sent to {user.email}")
    except Exception as e:
        logger.error(f"Error sending confirmation email: {e}")
