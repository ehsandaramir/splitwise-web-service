from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter

from split_wise import views

router = DefaultRouter()
router.register(r'profiles', views.ProfileViewSet, base_name='profile')
router.register(r'users', views.UserViewSet, base_name='user')
router.register(r'groups', views.GroupViewSet, base_name='group')

router.register(r'bills', views.BillViewSet, base_name='bill')
router.register(r'bills_instant', views.BillInstantViewSet, base_name='bill-instant')
router.register(r'transactions', views.TransactionViewSet, base_name='transaction')

urlpatterns = [
    path('api-auth/', include('rest_framework.urls'), name='api-auth'),
    path('docs/', include_docs_urls(title='Split Wise Documentations'), name='api-docs'),
    path('token-auth/', obtain_auth_token),
    path('signup/', views.api_signup, name='api-signup'),
    path('self/', views.SelfUserDetail.as_view(), name='self-detail')
]

urlpatterns += router.urls
