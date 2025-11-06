from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering=('name',)
        verbose_name_plural='categories'

    def __str__(self):
        return self.name    

class Item(models.Model):
    category=models.ForeignKey(Category,related_name='items',on_delete=models.CASCADE)
    name=models.CharField(max_length=255)
    description=models.TextField(blank=True,null=True)
    price=models.FloatField()
    image = CloudinaryField('image', blank=True, null=True)
    # image=models.ImageField(upload_to='item_images',blank=True,null=True)
    quantity = models.PositiveIntegerField(default=0)
    is_sold=models.BooleanField(default=False)
    created_by=models.ForeignKey(User,related_name='items',on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name  