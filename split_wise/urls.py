from django.urls import path, include
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter

from split_wise import views

router = DefaultRouter()
router.register(r'profiles', views.ProfileViewSet, base_name='profile')
router.register(r'users', views.UserViewSet, base_name='user')
router.register(r'groups', views.GroupViewSet, base_name='group')
router.register(r'self', views.SelfUserViewSet, base_name='self')

router.register(r'bills', views.BillViewSet, base_name='bill')
router.register(r'transactions', views.TransactionViewSet, base_name='transaction')

urlpatterns = [
    path('api-auth/', include('rest_framework.urls'), name='api-auth'),
    path('docs/', include_docs_urls(title='Split Wise Documentations'), name='api-docs'),
]

urlpatterns += router.urls
