from django.db.models import Count, Case, When, Avg, Max, Q, OuterRef
import json
from django.http import HttpResponseNotFound, Http404, HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, RetrieveUpdateAPIView, \
    GenericAPIView, UpdateAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin, RetrieveModelMixin, CreateModelMixin

from user.models import CustomUser
from .custompermissions import IsAdminOrReadOnly
from .models import Book
from .serializers import *
from .custompaginations import CustomPagination


# class CategoryUpdateAPIView(UpdateAPIView):
#     serializer_class = CategoryCreateSerializer
#     queryset = Category.objects.all()
#     lookup_field = 'url'
#     permission_classes = [IsAdminUser, ]


class CategoryCreateView(GenericAPIView):
    serializer_class = CategoryCreateSerializer
    permission_classes = [IsAdminUser, ]
    lookup_field = 'url'

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        url = kwargs.get('url', None)
        if not url:
            return Response({'error': 'Method PUT is not allowed'})
        try:
            book = Category.objects.get(url=url)
        except:
            return Response({'error': 'Object does not exists'})
        serializer = self.serializer_class(book, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BookCreateView(GenericAPIView):
    permission_classes = [IsAdminUser, ]
    serializer_class = BookCreateSerializer

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        url = kwargs.get('url', None)
        if not url:
            return Response({'error': 'Method PUT is not allowed'})
        try:
            book = Book.objects.get(url=url)
        except:
            return Response({'error': 'Object does not exists'})
        serializer = self.serializer_class(book, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BookListView(ListAPIView):
    queryset = Book.objects.all().annotate(rating=Avg('userbookrelation__rate'),
                                           likes_count=Count('userbookrelation__like')
                                           ).select_related('owner').order_by('-id')
    serializer_class = BookListSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ('category', 'name', 'author_name', 'price')
    search_fields = ('category__name', 'name', 'author_name', 'price')
    pagination_class = CustomPagination
    permission_classes = [AllowAny, ]
    ordering_fields = ['price', 'likes_count', 'rating']
    ordering = ('-rating', '-likes_count')


class BookDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all().annotate(rating=Avg('userbookrelation__rate')
                                           ).select_related('owner')
    serializer_class = BookDetailSerializer
    lookup_field = 'url'
    permission_classes = [IsAdminOrReadOnly, ]

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return BookAdminDetailSerializer
        return BookDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        print('something')
        return super().retrieve(request, *args, **kwargs)


class UserBookRateAPIView(RetrieveModelMixin,
                          DestroyModelMixin,
                          UpdateModelMixin,
                          GenericViewSet,
                          ):
    permission_classes = [IsAuthenticated]
    queryset = UserBookRelation.objects.all()
    serializer_class = UserBookRelationSerializer
    lookup_field = 'book__url'

    def get_object(self):
        try:
            book = Book.objects.get(url=self.kwargs['book__url'])
        except:
            return Http404()
        obj, _ = UserBookRelation.objects.get_or_create(user=self.request.user,
                                                        book=book)
        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        try:
            instance = self.get_object
        except:
            return Http404()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)


def pageNotFound(request, exception):
    return HttpResponseNotFound("<h1> Page not found! </h1>")


@api_view(['GET'])
@permission_classes([IsAdminUser, ])
def admin_dashboard(request):

    # A list of admins
    admins = CustomUser.objects.filter(Q(is_superuser=True) | Q(is_staff=True)).values_list('email', flat=True)

    # Number of books of each admin
    count_books = Book.objects.all().values('owner__email').annotate(count=Count('id'))

    # the best ten ranked books by users
    books = Book.objects.all().annotate(rating=Avg('userbookrelation__rate'),
            ).select_related('owner').values('name', 'owner__email', 'rating').order_by('-rating')[:10]

    # the best ten liked books by users
    liked_books = Book.objects.all().annotate(likes=Count('userbookrelation__like'),
            ).select_related('owner').values('name', 'owner__email', 'likes').order_by('-likes')[:10]

    # ten the most expensive books
    expensive_books = Book.objects.all().values('name', 'owner__email', 'price').order_by('-price')

    data = {
        'list of admins': admins,
        'Each admin`s number of books': count_books,
        'the best ten ranked books by users': books,
        'the best ten liked books by users': liked_books,
        'ten the most expensive books': expensive_books,
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdminUser, ])

def admin_detail(request, pk):
    try:
        admin = CustomUser.objects.filter(Q(is_superuser=True) | Q(is_staff=True)).get(pk=pk)
    except:
        return Response({'message': 'The admin does not exist'}, status=status.HTTP_404_NOT_FOUND)

    books = Book.objects.filter(owner=admin).annotate(rating=Avg('userbookrelation__rate'),
                                                      likes=Count('userbookrelation__like')
                                                      ).order_by('-likes')[:3]

    serializer = AdminDashboardSerializer(books, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

