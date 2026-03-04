from django.urls import path
from .views import CreateOrderView, OrderListView, AdminOrderAPIView, MonthlyRevenueAPIView, VerifyPaymentView

urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('create-order/', CreateOrderView.as_view(), name='create-order'),
    path('verify-payment/', VerifyPaymentView.as_view(), name='verify-payment'),
    path('<int:pk>/', AdminOrderAPIView.as_view(), name='order-detail'),
    path('revenue/', MonthlyRevenueAPIView.as_view(), name='monthly-revenue')
]
