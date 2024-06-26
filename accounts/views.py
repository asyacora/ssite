from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required


from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from django.http import HttpResponse
from carts.views import __cart_id
from carts.models import Cart, CartItem
from orders.models import Order

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email,
                                               username=username, password=password)
            user.phone_number = phone_number
            user.save()


            ##USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account.'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),

            })

            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            #messages.success(request, 'Thank you for registering with us. We have sent you a verification email to your email address. Please verify it.')
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form = RegistrationForm()

    context = {
        'form': form
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = auth.authenticate(request, email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=__cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                print(is_cart_item_exists)
                if is_cart_item_exists:
                    cart_items = CartItem.objects.filter(cart=cart)
                    print(cart_items)
                    for item in cart_items:
                        item.cart = None
                        item.user = user
                        item.save()
                    cart.delete()
            except Cart.DoesNotExist:
                pass
            auth.login(request, user)
            messages.success(request, 'You are logged in.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('dashboard')
    return render(request, 'accounts/login.html')

@login_required(login_url= 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('home')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.default_manager.get(pk=uid)

    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')

    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')

def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=False).order_by('-created_at')
    context = {
        'orders':orders,
    }
    return render(request, 'accounts/my_orders.html', context)

@login_required(login_url='accounts/login')
def dashboard(request):
    orders = Order.objects.filter(user_id=request.user.id, is_ordered=False) ##True olarak düzelicek!
    orders_count = orders.count()
    context = {
        'orders_count': orders_count,
    }
    return render(request, 'accounts/dashboard.html', context)