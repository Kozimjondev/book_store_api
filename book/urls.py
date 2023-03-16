from django.urls import path, include, re_path
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
    re_path('', include(router.urls), name='rate-update'),
    path('admin-dashboard', admin_dashboard, name='admin-dashboard'),
    path('admin-detail/<int:pk>', admin_detail, name='admin-detail'),
    # path('user-rate/<int:id>/', UserBookRateAPIView.as_view({'get': 'retrieve'}), name='rate-retrieve'),
    # path('user-rate/<int:id>/', UserBookRateAPIView.as_view({'put': 'update'}), name='rate-update'),
    # path('user-rate/<int:id>/', UserBookRateAPIView.as_view({'delete': 'destroy'}), name='rate-delete'),
    path('detail/<slug:url>/', BookDetailView.as_view(), name='detail'),

]



