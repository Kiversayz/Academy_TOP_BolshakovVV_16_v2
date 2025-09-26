from django.contrib import admin
from .models import Pet

# Register your models here.

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ['name', 'breed', 'animal_type', 'price', 'age', 'hypoallergenic', 'created_at']
    list_filter = ['animal_type', 'hypoallergenic', 'created_at']
    search_fields = ['name', 'breed']
    readonly_fields = ['created_at']