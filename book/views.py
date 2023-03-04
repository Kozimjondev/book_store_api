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

    # books = Book.objects.filter().annotate(likes=Count('userbookrelation__like')).order_by('-likes')[:3]
    data = {
        'list of admins': admins,
        'books of each admin': books,
        'Each admin`s number of books': count_books
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdminUser, ])
def admin_detail(request, pk):
    try:
        admin = CustomUser.objects.get(pk=pk, is_superuser=True, is_staff=True)
    except:
        return Response({'message': 'The admin does not exist'}, status=status.HTTP_404_NOT_FOUND)

    books = Book.objects.filter(owner=admin).annotate(likes=Count('userbookrelation__like')).order_by('-likes')[:3]

    data = {
        'The most liked books': books
    }

    return Response(data, status=status.HTTP_200_OK)

# @api_view(['GET', 'PUT', 'DELETE'])
# def tutorial_detail(request, pk):
#     try:
#         tutorial = Tutorial.objects.get(pk=pk)
#     except Tutorial.DoesNotExist:
#         return JsonResponse({'message': 'The tutorial does not exist'}, status=status.HTTP_404_NOT_FOUND)
#
#     if request.method == 'GET':
#         tutorial_serializer = TutorialSerializer(tutorial)
#         return JsonResponse(tutorial_serializer.data)
#
#     elif request.method == 'PUT':
#         tutorial_data = JSONParser().parse(request)
#         tutorial_serializer = TutorialSerializer(tutorial, data=tutorial_data)
#         if tutorial_serializer.is_valid():
#             tutorial_serializer.save()
#             return JsonResponse(tutorial_serializer.data)
#         return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     elif request.method == 'DELETE':
#         tutorial.delete()
#         return JsonResponse({'message': 'Tutorial was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)


# @api_view(['GET'])
# def tutorial_list_published(request):
#     tutorials = Tutorial.objects.filter(published=True)
#
#     if request.method == 'GET':
#         tutorials_serializer = TutorialSerializer(tutorials, many=True)
#         return JsonResponse(tutorials_serializer.data, safe=False)

