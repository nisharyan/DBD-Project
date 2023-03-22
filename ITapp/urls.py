from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
       path('', views.base, name="index"),
       path('home/', views.home, name="Home"),
       path('login/', views.loginPage, name="login"),
       path('logout/', views.logoutPage, name="logout"),
       path('userProfile/<str:pk>/', views.userProfile, name="user"),
       path('password/<str:pk>/', views.MyPasswordChangeView.as_view(), name='changePassword'),
       path('password/done', views.MyPasswordChangeDoneView.as_view(), name="changePasswordDone"),
       path('resources/', views.findResource, name="resources"),
       path('create/', views.createResource, name="create"),
       path('upload/',views.simple_upload, name='upload'),
       path('staffs/', views.staff, name="staffs"),
       path('database/<str:pk>/', views.filter, name="database"),
       path('update/<str:pk>/', views.updateResource, name="update"),
       path('delete/<str:pk>/', views.deleteResource, name="delete"),
       path('resourceStats/<str:pk>/', views.resource_stats, name="resourceStats"),
       path('departmentStats/<str:pk>/', views.department_stats, name="deaprtmentStats"),
       path('department/',views.department,name="department"),
       path('chatbot/',views.chats,name="chatbot")
]