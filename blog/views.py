from django.shortcuts import render
from rest_framework.views import APIView
from .models import Blog,BlogCategories
from .serializers import BlogSerializer,BlogCategoriesSerializer
from core.utils import success_response,error_response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
class BlogView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'categories',
                openapi.IN_QUERY,
                description="Filter blogs by category name or ID",
                type=openapi.TYPE_STRING,  # or TYPE_INTEGER if you're filtering by ID
            )
        ]
    )
    def get(self, request):
        categories = request.GET.get('categories')
        blogs = Blog.objects.all().order_by('-created_at')

        if categories:
            blogs = blogs.filter(categories__name=categories)  # adjust field as needed

        serializer = BlogSerializer(blogs, many=True)
        return success_response( data=serializer.data, status_code=status.HTTP_200_OK)
    
class BlogDetailView(APIView):
    def get(self, request, slug):
        try:
            blog = Blog.objects.get(slug=slug)
        except Blog.DoesNotExist:
            return error_response(message="Blog not found.", status_code=status.HTTP_404_NOT_FOUND)

        serializer = BlogSerializer(blog)
        return success_response(data=serializer.data, status_code=status.HTTP_200_OK)


class CategoriesView(APIView):
    def get(self, request):
        categories = BlogCategories.objects.all()
        serializer = BlogCategoriesSerializer(categories, many=True)
        return success_response(data=serializer.data, status_code=status.HTTP_200_OK)

class UpdateLike(APIView):
    def patch(self, request, slug):
        try:
            blog = Blog.objects.get(slug=slug)
        except Blog.DoesNotExist:
            return success_response(message={"detail": "Blog not found."}, status_code=status.HTTP_404_NOT_FOUND)

        like_action = request.data.get('like')
        if like_action is None:
            return success_response(message={"detail": "Missing 'like' field in request body."}, status_code=status.HTTP_400_BAD_REQUEST)

        if like_action:  # True means like
            blog.likes += 1
        else:  # False means dislike/unlike
            blog.likes = max(0, blog.likes - 1)  # Prevent going below 0

        blog.save()
        serializer = BlogSerializer(blog)
        return success_response(data=serializer.data, status_code=status.HTTP_200_OK)