from .models import Book, Category, UserBookRelation
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
    category = serializers.SlugRelatedField(slug_field='name', read_only=True,)
    likes_count = serializers.SerializerMethodField()
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)

    class Meta:
        model = Book
        fields = ['name', 'description', 'photo', 'price', 'author_name', 'category', 'likes_count', 'rating']

    def get_likes_count(self, instance):
        return UserBookRelation.objects.filter(book=instance, like=True).count()


class BookAdminDetailSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    category = serializers.SlugRelatedField(slug_field='name', read_only=True,)
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
        read_only_fields = ('book', )










    # def update(self, instance, validated_data):
    #     user = self.context['request'].user
    #     if user.pk != instance.pk:
    #         raise serializers.ValidationError({"authorize": "You dont have permission for this book."})
    #     instance.book = validated_data['book']
    #     instance.like = validated_data['like']
    #     instance.rate = validated_data['rate']
    #     instance.in_bookmarks = validated_data['in_bookmarks']
    #     instance.save()
    #     return instance































    # def update(self, instance, validated_data):
    #     user_data = validated_data.pop('user')
    #     instance = super().update(instance, validated_data)
    #     UserBookRelation.objects.filter(book__name=instance).update(**user_data)
    #     return instance

    # def update(self, instance, validated_data):
    #     userprofile_serializer = self.fields['profile']
    #     userprofile_instance = instance.userprofile
    #     userprofile_data = validated_data.pop('userprofile', {})
    #     userprofile_serializer.update(userprofile_instance, userprofile_data)
    #     instance = super().update(instance, validated_data)
    #     return instance

    # def update(self, instance, validated_data):
    #     user_data = validated_data.pop('user')
    #     game_data = validated_data.pop('games')
    #     username = self.data['user']['username']
    #     user = User.objects.get(username=username)
    #     print user
    #     user_serializer = UserSerializer(data=user_data)
    #     if user_serializer.is_valid():
    #         user_serializer.update(user, user_data)
    #     instance.save()
    #     return instance
