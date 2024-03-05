"""
URL configuration for DjangoAPI project.

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
from Cafeapp.views import index
from rest_framework.routers import DefaultRouter
from Cafeapp.views import query_word2vec
from Cafeapp.views import query_sentiment



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name="index"),
    #path('data/<str:search_string>/', call_store_labels, name='call_store_labels'),
    # path('data', call_store_labels, name='call_store_labels'),
    # path('tokens', call_tokens, name='call_tokens'),
    path('query_word2vec/<str:q>/', query_word2vec, name="query_word2vec"),
    path('query_sentiment/<str:q>/', query_sentiment, name="query_sentiment")
]


# router = DefaultRouter()
# router.register(r'your-model', YourModelViewSet, basename='your-model')
# urlpatterns = router.urls