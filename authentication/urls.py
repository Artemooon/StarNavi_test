from django.urls import path

from . import views

urlpatterns = [
    path('sign-up/', views.RegisterUser.as_view(), name="register_new_user"),
    path('sign-in/', views.LoginUser.as_view(), name="login_user"),
    path('logout/', views.LogoutUser.as_view(), name="logout_user"),
    path('refresh-token/', views.RefreshAuthToken.as_view(), name="refresh_auth_token"),
    path('auth-tokens-lifetime/', views.AuthTokensLifetime.as_view(), name="get_auth_token_lifetime"),
    path('user-analytics/<int:id>/', views.LastUserActivity.as_view(), name="get_last_user_activity")
]
