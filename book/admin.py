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
    readonly_fields = ['collected_money', ]


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
