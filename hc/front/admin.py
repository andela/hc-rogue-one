from django.contrib import admin
from .models import Category, Blog, Comment, EmailTasks

from hc.front.models import FrequentlyAskedQuestion

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    exclude = ('slug',)
    search_fields = ('title',)

class BlogAdmin(admin.ModelAdmin):
    exclude = ('slug',)
    list_filter = ('category','title',)
    search_fields = ('title',)
class EmailTasksAdmin(admin.ModelAdmin):
    exclude = ('',)
    search_fields = ('task_name',)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(Comment)
admin.site.register(EmailTasks, EmailTasksAdmin)

# Register your models here.
@admin.register(FrequentlyAskedQuestion)
class FaqAdmin(admin.ModelAdmin):
    fields = ('email','question','answer','status')
    list_display = ('id','email','question', 'answer', 'status')
    list_filter = ('status',)
    ordering= ('-id',)

