from django.contrib import admin
from django.urls import path, include
# from .views import UserApiView
from rest_framework.routers import DefaultRouter

from split_wise import views

router = DefaultRouter()
router.register(r'profiles', views.ProfileViewSet, base_name='profiles')
router.register(r'users', views.UserViewSet, base_name='users')
router.register(r'bills', views.BillViewSet, base_name='bills')
router.register(r'payments', views.PaymentViewSet, base_name='payments')
router.register(r'debts', views.DebtViewSet, base_name='debts')

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
]

urlpatterns += router.urls
