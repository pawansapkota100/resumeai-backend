from django.urls import path
from .views import BlogView,BlogDetailView,CategoriesView,UpdateLike

urlpatterns = [
    path('blog/', BlogView.as_view(), name='post_list'),
    path('blogs/<slug:slug>/', BlogDetailView.as_view(), name='blog-detail'),
    path('categories/', CategoriesView.as_view(), name='Categories'),
    path('blogs/<slug:slug>/update-like/', UpdateLike.as_view(), name='update-like'),


]
