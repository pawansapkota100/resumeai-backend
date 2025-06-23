from rest_framework.serializers import ModelSerializer
from .models import Blog,BlogCategories
from rest_framework import serializers



class BlogSerializer(ModelSerializer):
    categories= serializers.CharField(source='categories.name',read_only=True)
    author= serializers.CharField(source='author.first_name',read_only=True)

    class Meta:
        model= Blog
        fields= '__all__'

class BlogCategoriesSerializer(ModelSerializer):
    class Meta:
        model= BlogCategories
        fields= '__all__'


from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import Blog

class BlogAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Blog
        fields = '__all__'

class UpdateLike(ModelSerializer):
    class Meta:
        model = Blog
        fields = ['likes']