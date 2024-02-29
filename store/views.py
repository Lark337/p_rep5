from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime

from .models import *
from .utils import cookieCart, cartData, guestOrder

# Create your views here.

def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    products = Product.objects.all()
    context = {'products':products,'cartItems': cartItems}
    return render(request,'store/store.html',context)


def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {'items':items,'order':order, 'cartItems':cartItems}
    return render(request,'store/cart.html',context)

def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {'items':items,'order':order,'cartItems':cartItems}
    return render(request,'store/checkout.html',context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer,complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity =(orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("item was added", safe=False)

def processOrder(request):
    # print('Data:',request.body)
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            phoneNumber =customer.phoneNumber,
            address=data['shipping']['address']
        )
    else:
        customer, order = guestOrder(request,data)
        total = data['form']['total']
        order.transaction_id = transaction_id
        if total == order.get_cart_total:
            order.complete = True
        order.save()
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            phoneNumber=data['form']['phoneNumber'],
            address=data['shipping']['address'],
        )

    return JsonResponse('Payment complete', safe=False)

def active_orders(request):
    data = ShippingAddress.objects.all()
    context = {'shippingAddress':data}
    return render(request, 'store/active_orders.html', context)

