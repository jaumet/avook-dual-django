import stripe
import json
import logging
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from products.models import Product
from accounts.models import CustomUser
from products.services import fulfill_purchase

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)

@login_required
@require_POST
def create_checkout_session(request):
    product_id = request.POST.get('product_id')
    if not product_id:
        # Try to get it from JSON body if not in POST
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
        except:
            pass

    product = get_object_or_404(Product, pk=product_id)

    if not product.stripe_price_id:
        return JsonResponse({'error': 'Product does not have a Stripe Price ID configured.'}, status=400)

    try:
        success_url = request.build_absolute_uri(reverse('products:success')) + "?session_id={CHECKOUT_SESSION_ID}"
        cancel_url = request.build_absolute_uri(reverse('products:product_list'))

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': product.stripe_price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'user_id': request.user.id,
                'product_id': product.id,
                'payment_provider': 'stripe'
            },
            customer_email=request.user.email,
        )
        return JsonResponse({'url': checkout_session.url})
    except Exception as e:
        logger.error(f"Error creating Stripe checkout session: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        metadata = session.get('metadata', {})
        user_id = metadata.get('user_id')
        product_id = metadata.get('product_id')

        if user_id and product_id:
            try:
                user = CustomUser.objects.get(pk=user_id)
                product = Product.objects.get(pk=product_id)

                fulfill_purchase(
                    user=user,
                    product=product,
                    payment_provider='stripe',
                    stripe_checkout_id=session.get('id'),
                    paid_at=timezone.now()
                )
                logger.info(f"Stripe purchase fulfilled for user {user_id}, product {product_id}")
            except Exception as e:
                logger.error(f"Error fulfilling Stripe purchase: {e}")
                return HttpResponse(status=500)

    return HttpResponse(status=200)
