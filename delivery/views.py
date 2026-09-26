from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from requests.exceptions import RequestException

from .models import Customer, Restaurant, Item, Cart, CartItem, Order, OrderLine

import razorpay
from django.conf import settings

# Create your views here.
def index(request):
    return render(request, 'delivery/index.html')

def open_signup(request):
    return render(request, 'delivery/signup.html')

def open_signin(request):
    return render(request, 'delivery/signin.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')

        if Customer.objects.filter(username=username).exists():
            return HttpResponse("Duplicate username!")
        Customer.objects.create(
            username=username,
            password=make_password(password),
            email=email,
            mobile=mobile,
            address=address,
        )
    return render(request, 'delivery/signin.html')

def signin(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    username = request.POST.get('username', '')
    password = request.POST.get('password', '')

    try:
        customer = Customer.objects.get(username=username)
        if not check_password(password, customer.password):
            if password != customer.password:
                return HttpResponse("Registration failed")
            customer.password = make_password(password)
            customer.save(update_fields=['password'])

        if username == 'admin':
            return render(request, 'delivery/admin_home.html')
        return redirect('customer_home', username=username)

    except Customer.DoesNotExist:
        return HttpResponse("Registration failed")
    
def open_add_restaurant(request):
    return render(request, 'delivery/add_restaurant.html')

def add_restaurant(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')
        
        try:
            Restaurant.objects.get(name = name)
            return HttpResponse("Duplicate restaurant!")
        except:
            Restaurant.objects.create(
                name = name,
                picture = picture,
                cuisine = cuisine,
                rating = rating,
            )
    return render(request, 'delivery/admin_home.html')

def open_show_restaurant(request):
    restaurantList = Restaurant.objects.all()
    return render(request, 'delivery/show_restaurants.html',{"restaurantList" : restaurantList})

def open_update_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    return render(request, 'delivery/update_restaurant.html', {"restaurant" : restaurant})

def update_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')
        
        restaurant.name = name
        restaurant.picture = picture
        restaurant.cuisine = cuisine
        restaurant.rating = rating

        restaurant.save()

    restaurantList = Restaurant.objects.all()
    return render(request, 'delivery/show_restaurants.html',{"restaurantList" : restaurantList})

def delete_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    restaurant.delete()

    restaurantList = Restaurant.objects.all()
    return render(request, 'delivery/show_restaurants.html',{"restaurantList" : restaurantList})

def open_update_menu(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    itemList = restaurant.items.filter(vegeterian=True)
    #itemList = Item.objects.all()
    return render(request, 'delivery/update_menu.html',{"itemList" : itemList, "restaurant" : restaurant})

def update_menu(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        vegeterian = True
        picture = request.POST.get('picture')
        
        try:
            Item.objects.get(name = name)
            return HttpResponse("Duplicate item!")
        except:
            Item.objects.create(
                restaurant = restaurant,
                name = name,
                description = description,
                price = price,
                vegeterian = vegeterian,
                picture = picture,
            )
    return render(request, 'delivery/admin_home.html')

def view_menu(request, restaurant_id, username):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    itemList = restaurant.items.filter(vegeterian=True)
    #itemList = Item.objects.all()
    return render(request, 'delivery/customer_menu.html'
                  ,{"itemList" : itemList,
                     "restaurant" : restaurant, 
                     "username":username})

def customer_home(request, username):
    customer = get_object_or_404(Customer, username=username)
    restaurantList = Restaurant.objects.all()
    return render(request, 'delivery/customer_home.html', {
        'restaurantList': restaurantList,
        'username': customer.username,
    })
    
def add_to_cart(request, item_id, username):
    item = get_object_or_404(Item, id=item_id)
    customer = get_object_or_404(Customer, username=username)

    cart, created = Cart.objects.get_or_create(customer = customer)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
    if not created:
        cart_item.quantity += 1
        cart_item.save(update_fields=['quantity'])

    messages.success(request, 'Item added successfully.')
    return redirect('show_cart', username=username)

def adjust_cart_item(request, item_id, username):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    customer = get_object_or_404(Customer, username=username)
    cart = get_object_or_404(Cart, customer=customer)
    cart_item = get_object_or_404(CartItem, cart=cart, item_id=item_id)
    action = request.POST.get('action')

    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save(update_fields=['quantity'])
        messages.success(request, 'Quantity updated.')
    elif action == 'decrease':
        if cart_item.quantity <= 1:
            cart_item.delete()
            messages.success(request, 'Item removed from your cart.')
        else:
            cart_item.quantity -= 1
            cart_item.save(update_fields=['quantity'])
            messages.success(request, 'Quantity updated.')
    else:
        return HttpResponseBadRequest('Unknown cart action.')

    return redirect('show_cart', username=username)

def save_delivery_address(request, username):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    customer = get_object_or_404(Customer, username=username)
    address = request.POST.get('address', '').strip()
    if not address or len(address) > 250:
        messages.error(request, 'Enter a delivery address up to 250 characters long.')
    else:
        customer.address = address
        customer.save(update_fields=['address'])
        messages.success(request, 'Delivery address updated.')

    return redirect('show_cart', username=username)

def show_cart(request, username):
    customer = get_object_or_404(Customer, username=username)
    cart = Cart.objects.filter(customer=customer).first()
    cart_lines = cart.cart_lines.select_related('item') if cart else []
    total_price = cart.total_price() if cart else 0

    return render(request, 'delivery/cart.html', {
        'cart_lines': cart_lines,
        'total_price': total_price,
        'username': username,
        'customer': customer,
    })

# Checkout View
def checkout(request, username):
    customer = get_object_or_404(Customer, username=username)
    cart = Cart.objects.filter(customer=customer).first()
    cart_lines = cart.cart_lines.select_related('item') if cart else []
    total_price = cart.total_price() if cart else 0
    context = {
        'username': username,
        'customer': customer,
        'cart_lines': cart_lines,
        'total_price': total_price,
        'payment_available': False,
    }

    if total_price == 0:
        context['error'] = 'Your cart is empty.'
        return render(request, 'delivery/checkout.html', context)

    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        context['payment_notice'] = 'Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET to enable online payment. Cash on delivery is available now.'
        return render(request, 'delivery/checkout.html', context)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    amount_paise = int(round(total_price * 100))
    order_data = {
        'amount': amount_paise,
        'currency': 'INR',
        'payment_capture': '1',
    }
    try:
        order = client.order.create(data=order_data)
    except (razorpay.errors.BadRequestError, razorpay.errors.GatewayError,
            razorpay.errors.ServerError, RequestException):
        context['payment_notice'] = 'Razorpay could not start. Check your gateway keys or choose cash on delivery.'
        return render(request, 'delivery/checkout.html', context)

    context.update({
        'payment_available': True,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'order_id': order['id'],
        'amount_paise': amount_paise,
    })
    return render(request, 'delivery/checkout.html', context)
    
# Orders Page
def orders(request, username):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    customer = get_object_or_404(Customer, username=username)
    cart = Cart.objects.filter(customer=customer).first()
    cart_lines = list(cart.cart_lines.select_related('item')) if cart else []
    total_price = cart.total_price() if cart else 0
    if not cart_lines:
        messages.error(request, 'Your cart is empty.')
        return redirect('show_cart', username=username)

    payment_method = request.POST.get('payment_method')
    if payment_method == 'cod':
        if not customer.address.strip():
            messages.error(request, 'Add a delivery address before placing your order.')
            return redirect('show_cart', username=username)
        success_message = 'Order placed! Pay cash when it arrives.'
        saved_payment_method = 'cod'
    elif payment_method == 'razorpay':
        if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
            messages.error(request, 'Online payments are not configured. Choose cash on delivery instead.')
            return redirect('checkout', username=username)

        payment_details = {
            'razorpay_order_id': request.POST.get('razorpay_order_id', ''),
            'razorpay_payment_id': request.POST.get('razorpay_payment_id', ''),
            'razorpay_signature': request.POST.get('razorpay_signature', ''),
        }
        if not all(payment_details.values()):
            messages.error(request, 'The online payment could not be verified. Your cart is unchanged.')
            return redirect('checkout', username=username)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature(payment_details)
            order = client.order.fetch(payment_details['razorpay_order_id'])
            payment = client.payment.fetch(payment_details['razorpay_payment_id'])
        except (razorpay.errors.BadRequestError, razorpay.errors.GatewayError,
                razorpay.errors.ServerError, razorpay.errors.SignatureVerificationError,
                RequestException):
            messages.error(request, 'The online payment could not be verified. Your cart is unchanged.')
            return redirect('checkout', username=username)

        expected_amount = int(round(total_price * 100))
        if (
            order.get('amount') != expected_amount
            or order.get('currency') != 'INR'
            or payment.get('order_id') != payment_details['razorpay_order_id']
            or payment.get('amount') != expected_amount
            or payment.get('status') != 'captured'
        ):
            messages.error(request, 'The payment amount or status did not match this order. Your cart is unchanged.')
            return redirect('checkout', username=username)
        success_message = 'Payment successful! Your order has been placed.'
        saved_payment_method = 'razorpay'
    else:
        return HttpResponseBadRequest('Choose a supported payment method.')

    with transaction.atomic():
        placed_order = Order.objects.create(
            customer=customer,
            delivery_address=customer.address,
            total_price=f'{total_price:.2f}',
            payment_method=saved_payment_method,
        )
        OrderLine.objects.bulk_create([
            OrderLine(
                order=placed_order,
                item=line.item,
                item_name=line.item.name,
                item_picture=line.item.picture,
                unit_price=f'{line.item.price:.2f}',
                quantity=line.quantity,
            )
            for line in cart_lines
        ])
        cart.cart_lines.all().delete()

    messages.success(request, success_message)
    return redirect('order_detail', username=username, order_id=placed_order.pk)


def order_history(request, username):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    customer = get_object_or_404(Customer, username=username)
    orders = customer.orders.order_by('-created_at')
    return render(request, 'delivery/order_history.html', {
        'username': customer.username,
        'orders': orders,
    })


def order_detail(request, username, order_id):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    customer = get_object_or_404(Customer, username=username)
    order = get_object_or_404(
        Order.objects.prefetch_related('lines'),
        pk=order_id,
        customer=customer,
    )
    return render(request, 'delivery/order_detail.html', {
        'username': customer.username,
        'order': order,
    })