from django.urls import path
from . import views

urlpatterns = [
    path(
        '',
        views.home,
        name='home'),
    path(
        'convert',
        views.cartoonize,
        name='cartoonize'),
    path(
        'style_transfer/',
        views.style_transfer_page,
        name='style_transfer'),
    path(
        'process_style_transfer',
        views.style_transfer,
        name='process_style_transfer'),
]
