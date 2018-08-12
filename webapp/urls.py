from django.urls import path

from webapp import views

urlpatterns = [
    path('', views.webapp_main, name='webapp-main'),
    path('signup/', views.webapp_signup, name='webapp-signup'),
    path('dashboard/', views.webapp_dashboard, name='webapp-dashboard'),
    path('dashboard/view/<int:pk>/', views.webapp_view, name='webapp-view'),
]
