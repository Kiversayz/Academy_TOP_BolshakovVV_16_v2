from django.contrib import admin
from .models import Product, PetComment

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'created_at')
    search_fields = ('name', 'price')

@admin.register(PetComment)
class PetCommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'pet', 'created_at')
    list_filter = ('pet', 'created_at')
    search_fields = ('author_name', 'comment_text')