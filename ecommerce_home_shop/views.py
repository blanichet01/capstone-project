from rest_framework import viewsets
from .models import Product, Cart, Order
from .serializers import ProductSerializer, CartSerializer, OrderSerializer

import paypalrestsdk
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer



# Asegúrate de importar tu archivo de configuración de PayPal
from .paypal_config import paypalrestsdk

def create_payment(request):
    # Crear un objeto de pago
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": "http://localhost:8000/payment/execute",
            "cancel_url": "http://localhost:8000/payment/cancel"
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "Producto 1",
                    "sku": "12345",
                    "price": "10.00",
                    "currency": "USD",
                    "quantity": 1
                }]
            },
            "amount": {
                "total": "10.00",
                "currency": "USD"
            },
            "description": "Descripción del producto."
        }]
    })

    if payment.create():
        # Redireccionar al usuario a PayPal para completar el pago
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = str(link.href)
                return redirect(approval_url)
    else:
        return JsonResponse({'error': payment.error})
    
def execute_payment(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        # Pago exitoso, puedes procesar el pedido aquí
        return JsonResponse({'status': 'Pago completado con éxito'})
    else:
        return JsonResponse({'error': payment.error})

