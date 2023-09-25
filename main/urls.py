from django.urls import path

from main.views import CreateAccountApiView, LoginApiView, ShoppingListApiView

ACCOUNT_URLS = [
    path("create/", CreateAccountApiView.as_view(), name="create-account"),
    path("login/", LoginApiView.as_view(), name="login"),
]


urlpatterns = [
    path("shopping-list/", ShoppingListApiView.as_view(), name="shopping-list"),
    *ACCOUNT_URLS,
]
