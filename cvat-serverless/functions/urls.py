from django.urls import path
from functions import views

urlpatterns = [
    path('api/functions', views.function_list),
    path('api/functions/<str:name>', views.function_detail),
    path('api/function_invocations', views.function_invoke)
]