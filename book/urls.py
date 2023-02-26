from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter

from .views import *

router = DefaultRouter()
router.register(r'user-rate', UserBookRateAPIView)

urlpatterns = [
    path('', BookListView.as_view(), name='book'),
    path('category/', CategoryCreateView.as_view(), name='category-create'),
    path('category/<slug:url>/', CategoryCreateView.as_view(), name='category-update'),
    path('create/', BookCreateView.as_view(), name='book-create'),
    path('create/<slug:url>/', BookCreateView.as_view(), name='book-update'),
    path('', include(router.urls), name='rate-update'),
    # path('user-rate/<int:id>/', UserBookRateAPIView.as_view({'get': 'retrieve'}), name='rate-retrieve'),
    # path('user-rate/<int:id>/', UserBookRateAPIView.as_view({'put': 'update'}), name='rate-update'),
    # path('user-rate/<int:id>/', UserBookRateAPIView.as_view({'delete': 'destroy'}), name='rate-delete'),
    path('<slug:url>/', BookDetailView.as_view(), name='detail'),
]



