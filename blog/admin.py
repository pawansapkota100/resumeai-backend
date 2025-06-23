from django.contrib import admin
from .models import Blog, BlogCategories
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class BlogAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Blog
        fields = '__all__'

@admin.register(BlogCategories)
class BlogCategoriesAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    form = BlogAdminForm
    list_display = ['title', 'status', 'author', 'created_at', 'categories', 'reading_time']
    list_filter = ['status', 'categories', 'created_at']
    search_fields = ['title', 'description', 'tag']
    prepopulated_fields = {"slug": ("title",)}
    ordering = ['-created_at']
