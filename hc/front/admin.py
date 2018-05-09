from django.contrib import admin
from .models import Category, Blog, Comment
# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    exclude = ('slug',)
    search_fields = ('title',)

class BlogAdmin(admin.ModelAdmin):
    exclude = ('slug',)
    list_filter = ('category','title',)
    search_fields = ('title',)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(Comment)