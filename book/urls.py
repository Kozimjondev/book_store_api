from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import *

# router = SimpleRouter()
# router.register(r'user-rate', UserBookRateAPIView)

urlpatterns = [
    path('', BookListView.as_view(), name='book'),
    path('category/', CategoryCreateView.as_view(), name='category-create'),
    path('create/', BookCreateView.as_view(), name='book-create'),
    path('user-rate/<slug:book__url>', UserBookRateAPIView.as_view({'put': 'update'}), name='user-rate'),
    path('<slug:url>/', BookDetailView.as_view(), name='detail'),
]

# urlpatterns += router.urls

