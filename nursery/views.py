from django.shortcuts import render, get_object_or_404
from .models import Pet
from .serializers import PetSerializer
from rest_framework import viewsets, permissions

# Create your views here.

def pet_list(request):
    pets = Pet.objects.all()
    return render(request=request, template_name='nursery/pet_list.html', context={'pets': pets})

def pet_detail(request, pk):
    pet = get_object_or_404(klass=Pet,pk=pk)
    return render(request=request, template_name='nursery/pet_detail.html', context={'pets':pet})

class PetViewSet(viewsets.ModelViewSet):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
    permission_classes = [permissions.IsAuthenticated]