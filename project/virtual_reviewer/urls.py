from django.urls import path, include
from .views.product import *
from .views.user import *
from .views.review import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('gioi-thieu/', AboutView.as_view(), name='about'),
    path('so-sanh/', CompareView.as_view(), name='compare'),
    path('huong-dan/', GuideView.as_view(), name='guide'),
    path('tim-kiem/', SearchView.as_view(), name='search'),
    path('san-pham/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path("tao-review/", GenerateReviewView.as_view(), name="generate_review"),
]