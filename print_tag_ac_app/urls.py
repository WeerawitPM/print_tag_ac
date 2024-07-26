from django.urls import path
from print_tag_ac_app import views
# from .views import get_modal_data

urlpatterns = [
    path("", views.index),
    path('save_selected', views.save_selected, name='save_selected'),
]