"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login, name="login"),
    path('login', views.login, name="login"),
    path('register', views.register, name="register"),
    path('settings', views.settings, name="settings"),
    path('logout', views.logout, name="logout"),
    path('edit-profile', views.editProfile, name="editProfile"),
    path('change-password', views.changePassword, name="changePassword"), 
    path('send-message', views.sendMessage, name="sendMessage"),
    path('change-username', views.changeUsername, name="changeUsername"),
    path('change-email', views.changeEmail, name="changeEmail"),
    path('delete-message/<int:id>', views.deleteMessage, name="deleteMessage"),
    path('messages', views.userMessages, name="userMessages"),
    path('activation-email/<uidb64>/<token>', views.activate_user_account, name="activationEmail"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('profile', views.profile, name="profile"),
    path('reset-password', views.reset_password, name="reset_password"),
    path('reset-token-confirmation', views.reset_token_confirmation, name="reset_token_confirmation")
    
    
]
