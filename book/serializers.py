from django.db.models import Avg

from .models import Book, Category, UserBookRelation, UserBuyBook
from rest_framework import serializers


class CategoryCreateSerializer(serializers.ModelSerializer):
    url = serializers.CharField(read_only=True)

    class Meta:
        model = Category
        fields = '__all__'

    def validate(self, attrs):
        if not self.context["request"].user.is_staff:
            raise serializers.ValidationError("Validation error")
        return attrs


class BookListSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)

    class Meta:
        model = Book
        fields = ['name', 'photo', 'price', 'author_name', 'likes_count', 'rating', ]

    def get_likes_count(self, instance):
        return UserBookRelation.objects.filter(book=instance, like=True).count()

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     representation['likes'] = instance.like.count()
    #
    #     return representation


class BookCreateSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    url = serializers.CharField(read_only=True)

    class Meta:
        model = Book
        fields = "__all__"

    def validate(self, attrs):
        if not self.context["request"].user.is_staff:
            raise serializers.ValidationError("Validation error")
        return attrs


class BookDetailSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='name', read_only=True, )
    likes_count = serializers.SerializerMethodField()
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)

    class Meta:
        model = Book
        fields = ['name', 'description', 'photo', 'price', 'author_name', 'category', 'likes_count', 'rating']

    def get_likes_count(self, instance):
        return UserBookRelation.objects.filter(book=instance, like=True).count()


class BookAdminDetailSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    category = serializers.SlugRelatedField(slug_field='name', read_only=True, )
    readers = serializers.SlugRelatedField(slug_field='email', read_only=True, many=True)
    likes_count = serializers.SerializerMethodField()
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)

    class Meta:
        model = Book
        fields = "__all__"

    def get_likes_count(self, instance):
        return UserBookRelation.objects.filter(book=instance, like=True).count()


class UserBookRelationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = UserBookRelation
        fields = ('user', 'book', 'like', 'rate', 'in_bookmarks')
        lookup_field = 'book__url'
        read_only_fields = ('book',)


class AdminDashboardSerializer(serializers.ModelSerializer):
    likes = serializers.IntegerField(read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)

    class Meta:
        model = Book
        fields = ['name', 'price', 'likes', 'rating']

    # def get_rating(self, instance):
    #     # return Book.objects.all().annotate(Avg('userbookrelation__rate'))
    #     # return UserBookRelation.objects.filter(book=instance).annotate(Avg('userbookrelation__rate'))
    #
    #     return Book.objects.filter(owner=instance).annotate(Avg('userbookrelation__rate'))
    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     representation['owner__rate'] = instance.rate.Avg()
    #
    #     return representation


class UserBuyBookSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    book = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = UserBuyBook
        fields = ['is_bought', 'user', 'book']
        read_only_fields = ('book',)
        lookup_field = 'book__url'

