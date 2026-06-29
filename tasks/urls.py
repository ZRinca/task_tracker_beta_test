from django.contrib import admin
from django.urls import path
from tasks import views

urlpatterns = [
    path('taskworkend/add/', views.add_task),
    path('taskworkend/execute/', views.execute_task),
    path('taskworkend/get_total_time_spent/', views.get_total_time_spent)
]