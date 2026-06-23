from django.contrib import admin
from django.urls import path
from tasks import views

urlpatterns = [
    path('taskworkend/add/', views.add_task),
    path('taskworkend/execute/', views.execute_task),
]