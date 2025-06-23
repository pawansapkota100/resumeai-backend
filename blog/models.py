from django.db import models
from django.contrib.auth import get_user_model
User=get_user_model()

class BlogCategories(models.Model):
    name= models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Blog(models.Model):
    slug = models.SlugField(unique=True)  
    title= models.CharField(max_length=255)
    description= models.TextField()
    categories= models.ForeignKey(BlogCategories,on_delete=models.CASCADE,related_name='blog_categories')
    tag= models.CharField(max_length=255)
    author= models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    reading_time=models.IntegerField(default=5)
    image=models.ImageField( upload_to='blog-image')
    created_at= models.DateField(auto_now_add=True)
    likes=models.IntegerField(default=0)
    status=models.BooleanField(default=False)

