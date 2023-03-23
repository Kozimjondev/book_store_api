from django.contrib import admin
from .models import Book, Category, UserBookRelation, UserBuyBook


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'author_name', 'category']
    list_display_links = ['name', 'author_name']
    search_fields = ['name', 'author_name', 'category']
    ordering = ['-id']
    list_filter = ['created_at', 'name', 'category']
    prepopulated_fields = {'url': ('name', )}
    readonly_fields = ['money_from_user', 'collected_money', ]

    @admin.display(description='List of users who buy the book')
    def money_from_user(self, obj, id=None):
        list_of_users = []
        queryset = obj.userbuybook_set.all().values_list('user__email', flat=True)
        # queryset = UserBuyBook.objects.filter(is_bought=True).values_list('user__email', flat=True)
        print(queryset)
        for i in queryset.iterator():
            list_of_users.append(i)
        return list_of_users


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['name', ]
    search_fields = ['name', ]
    prepopulated_fields = {'url': ('name', )}


admin.site.register(UserBookRelation)


@admin.register(UserBuyBook)
class UserBuyBookAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['name', ]
    readonly_fields = ['is_bought', ]
