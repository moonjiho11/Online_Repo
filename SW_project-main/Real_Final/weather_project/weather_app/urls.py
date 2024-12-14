from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('weather/', views.weather, name='weather'),
    path('get-weather-data', views.get_weather_data, name='get_weather_data'),
    path('accounts/', include('django.contrib.auth.urls'
]
