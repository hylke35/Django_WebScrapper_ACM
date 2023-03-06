from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('update/', views.update, name='update'),
    path('scan_company/<str:name>', views.detail, name='scan_company'),
    path('back/', views.update, name='back')
]