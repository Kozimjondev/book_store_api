from django.db.models import Count, Case, When, Avg
from django.http import HttpResponseNotFound
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, RetrieveUpdateAPIView, \
    GenericAPIView, UpdateAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin, RetrieveModelMixin, CreateModelMixin
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
    queryset = Book.objects.all().annotate(rating=Avg('userbookrelation__rate')
                                           ).select_related('owner').order_by('id')
    serializer_class = BookListSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_fields = ('category', 'name', 'author_name')
    search_fields = ('category__name', 'name', 'author_name')
    pagination_class = CustomPagination
    permission_classes = [AllowAny, ]

class BookDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all().annotate(rating=Avg('userbookrelation__rate')
                                           ).select_related('owner').order_by('id')
    serializer_class = BookDetailSerializer
    lookup_field = 'url'
    permission_classes = [IsAdminOrReadOnly, ]


# class UserBookRelationView(RetrieveUpdateAPIView):
#     queryset = UserBookRelation.objects.all()
#     serializer_class = UserBookRelationSerializer
#     permission_classes = [IsAuthenticated]
#     # lookup_field = 'pk'
#     #
#     # def get_object(self):
#     #     return self.request.user
#
#     def get_object(self):
#         return UserBookRelation.objects.get(user=self.request.user)

# class UserBookRateAPIView(GenericAPIView):
#     serializer_class = UserBookRelationSerializer
#     # permission_classes = [IsAuthenticated]
#
#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def put(self, request, *args, **kwargs):
#         pk = kwargs.get('pk', None)
#         if not pk:
#             return Response({'error': 'Method PUT is not allowed'})
#         try:
#             book = UserBookRelation.objects.get(pk=pk)
#         except:
#             return Response({'error': 'Object does not exists'})
#         serializer = self.serializer_class(book, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#     def delete(self, request, *args, **kwargs):
#         pk = kwargs.get('pk', None)
#         if not pk:
#             return Response({'error': 'Method PUT is not allowed'})
#         try:
#             book = UserBookRelation.objects.get(pk=pk)
#         except:
#             return Response({'error': 'Object does not exists'})
#         book.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
#
#     def get_object(self):
#         return UserBookRelation.objects.get(user=self.request.user)

# @api_view(['GET', 'PUT'])
# def user_rate(request, url):
#     if request.method == 'GET':
#         # items = get_object_or_404(UserBookRelation, book__url=url) user=request.user
#         items = UserBookRelation.objects.filter(user=request.user, book__url=url)
#         serializer = UserBookRelationSerializer(items, many=True)
#         return Response(serializer.data)
#     elif request.method == 'PUT':
#         instance = UserBookRelation.objects.filter(user=request.user, book__url=url)
#         serializer = UserBookRelationSerializer(instance=instance, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors)

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
        book = Book.objects.get_or_create(url=self.kwargs['url'])
        # print((book))
        obj, _ = UserBookRelation.objects.get_or_create(user=self.request.user,
                                                        book=book)
        # print(obj)
        return obj


def pageNotFound(request, exception):
    return HttpResponseNotFound("<h1> Page not found! </h1>")

