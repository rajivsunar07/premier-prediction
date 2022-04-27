from django.urls import path
from soupsieve import match

from core.views import home, match_detail

app_name = "core"

urlpatterns = [
    path('', home, name='home'),
    path('<id>/', match_detail, name='detail'),
]