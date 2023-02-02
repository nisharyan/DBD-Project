from django.urls import path, include
from . import views

urlpatterns = [
       path('', views.base, name="index"),
       path('home/', views.home, name="Home"),
       path('login/', views.loginPage, name="login"),
       path('logout/', views.logoutPage, name="logout"),
       path('userProfile/<str:pk>/', views.userProfile, name="user"),
       path('resources/', views.findResource, name="resources"),
       path('create/', views.createResource, name="create"),
       path('upload/',views.simple_upload, name='upload'),
       path('staffs/', views.staff, name="staffs"),
       path('database/<str:pk>/', views.filter, name="database"),
       path('update/<str:pk>/', views.updateResource, name="update"),
       path('delete/<str:pk>/', views.deleteResource, name="delete"),
]