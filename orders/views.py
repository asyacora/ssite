from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from carts.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from store.models import Product
import json
import stripe
import datetime
import time


stripe.api_key = settings.STRIPE_SECRET_KEY_TEST


@login_required(login_url='/accounts/login')
def product_page(request):
    if request.method == 'POST':
        current_user = request.user
        cart_items = CartItem.objects.filter(user=current_user)
        cart_count = cart_items.count()
        if cart_count <= 0:
            return redirect('store')

        total = sum(cart_item.product.price * cart_item.quantity for cart_item in cart_items)
        tax = (2 * total) / 100
        grand_total = total + tax

        # Create the order
        form = OrderForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data['user'] = current_user
            data['order_total'] = grand_total
            data['tax'] = tax
            data['ip'] = request.META.get('REMOTE_ADDR')
            order = Order.objects.create(**data)

            # Generate order number
            yr = datetime.date.today().strftime('%Y')
            dt = datetime.date.today().strftime('%d')
            mt = datetime.date.today().strftime('%m')
            d = datetime.date(int(yr), int(mt), int(dt))
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(order.id)
            order.order_number = order_number
            order.save()

            # Create order products and reduce product stock
            for cart_item in cart_items:
                order_product = OrderProduct.objects.create(
                    order=order,
                    payment=None,
                    user=current_user,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    product_price=cart_item.product.price,
                    ordered=True
                )
                product = Product.objects.get(id=cart_item.product_id)
                product.stock -= cart_item.quantity
                product.save()

            # Clear the cart
            CartItem.objects.filter(user=current_user).delete()

            # Create Stripe checkout session
            try:
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[
                        {
                            'price': settings.PRODUCT_PRICE,
                            'quantity': 1,
                        },
                    ],
                    mode='payment',
                    customer_email=current_user.email,
                    success_url=settings.REDIRECT_DOMAIN + '/orders/payment_successful',
                    cancel_url=settings.REDIRECT_DOMAIN + '/orders/payment_cancelled',
                )
                payment = Payment.objects.create(
                    user=current_user,
                    payment_id='',
                    payment_method='',
                    amount_paid=str(grand_total),
                    status='Pending',
                    stripe_checkout_id=checkout_session.id,
                )

                return redirect(checkout_session.url, code=303)

            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'orders/payments.html')



"""def place_order(request):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    total = 0
    quantity = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data['user'] = current_user
            data['order_total'] = grand_total
            data['tax'] = tax
            data['ip'] = request.META.get('REMOTE_ADDR')
            order = Order.objects.create(**data)
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(order.id)
            order.order_number = order_number
            order.save()
            for cart_item in cart_items:
                orderproduct = OrderProduct.objects.create(
                    order_id=order.id,
                    payment=None,
                    user_id=current_user.id,
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    product_price=cart_item.product.price,
                    ordered=True
                )
                product = Product.objects.get(id=cart_item.product_id)
                product.stock -= cart_item.quantity
                product.save()
            CartItem.objects.filter(user=current_user).delete()
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')"""


## use Stripe dummy card: 4242 4242 4242 4242
def payment_successful(request):
    checkout_session_id = request.GET.get('session_id')

    try:
        session = stripe.checkout.Session.retrieve(checkout_session_id)
        customer = stripe.Customer.retrieve(session.customer)

        order_number = request.GET.get('order_number')
        transID = request.GET.get('payment_id')

        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order=order)
        subtotal = sum(op.product_price * op.quantity for op in ordered_products)
        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order_number,
            'transID': transID,
            'payment': payment,
            'subtotal': subtotal,
        }

        return render(request, 'orders/payment_successful.html', context)
    except stripe.error.InvalidRequestError as e:
        # Handle the error gracefully
        return render(request, 'orders/payment_cancelled.html', {'error': str(e)})
    except Exception as e:
        # Handle any other unexpected errors
        return render(request, 'orders/payment_cancelled.html', {'error': str(e)})

"""def payment_successful(request):
    checkout_session_id = request.GET.get('session_id', None)

    try:
        session = stripe.checkout.Session.retrieve(checkout_session_id)
        customer = stripe.Customer.retrieve(session.customer)
        # Assuming you have a user_id field in your Payment model
        user_payment = Payment.objects.get(user_id=request.user.id, stripe_checkout_id=checkout_session_id)
        user_payment.stripe_checkout_id = checkout_session_id
        user_payment.save()

        return render(request, 'orders/payment_successful.html', {'customer': customer})
    except stripe.error.InvalidRequestError as e:
        # Handle the error gracefully
        return render(request, 'orders/payment_cancelled.html')"""




def payment_cancelled(request):
	stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
	return render(request, 'orders/payment_cancelled.html')


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    signature_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, signature_header, settings.STRIPE_WEBHOOK_SECRET_TEST
        )
    except ValueError as e:
        print("Invalid payload")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print("Invalid signature")
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session.get('id', None)

        time.sleep(15)  # Ensure the session is available

        try:
            user_payment = Payment.objects.get(stripe_checkout_id=session_id)
            user_payment.status = 'Paid'
            user_payment.save()

            print(f"Payment found: {user_payment.payment_id}, status updated to Paid")

            order = Order.objects.get(payment=user_payment)
            order.is_ordered = True
            order.save()

            print(f"Order {order.order_number} updated to is_ordered=True")

        except Payment.DoesNotExist:
            print(f"No Payment found for session ID: {session_id}")
        except Order.DoesNotExist:
            print(f"No Order found for payment ID: {user_payment.payment_id}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    return HttpResponse(status=200)


