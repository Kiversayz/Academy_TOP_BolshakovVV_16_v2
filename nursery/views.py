from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import viewsets, permissions
from django.contrib.auth.decorators import login_required
from .models import Pet
from .serializers import PetSerializer
from .forms import PetForm
from django.http import HttpResponseForbidden

# Create your views here.


def pet_list(request):
    """
    Отображает список всех животных.
    """
    pets = Pet.objects.all()
    return render(request=request, template_name='nursery/pet_list.html', context={'pets': pets})


def pet_detail(request, pk):
    """
    Отображает детальную информацию о конкретном животном.
    """
    pet = get_object_or_404(klass=Pet, pk=pk)
    return render(request=request, template_name='nursery/pet_detail.html', context={'pet': pet})


@login_required
def pet_create(request):
    """
    Создает новое животное.
    """
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)  # Не сохраняем в БД пока
            pet.owner = request.user       # Устанавливаем владельца
            pet.save() 
            return redirect('pet_list')
        # Если форма не валидна, просто продолжаем вниз (рендерим форму с ошибками)
    else:
        # Если GET-запрос — создаем пустую форму
        form = PetForm()

    # Рендерим шаблон в любом случае (и после POST с ошибками, и при GET)
    return render(request, 'nursery/pet_create.html', {'form': form})


@login_required
def pet_update(request, pk):
    """
    Обновляет информацию о конкретном животном.
    """
    pet = get_object_or_404(Pet, pk=pk)
    
    if pet.owner != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Вы не являетесь владельцем этого питомца.")
    
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            return redirect('pet_detail', pk=pet.pk)
    else:
        form = PetForm(instance=pet)

    return render(request, 'nursery/pet_update.html', {'form': form, 'pet': pet})


@login_required
def pet_delete(request, pk):
    """
    Удаляет конкретное животное.
    """
    pet = get_object_or_404(Pet, pk=pk)
    
    if pet.owner != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Вы не являетесь владельцем этого питомца.")
    
    if request.method == 'POST':
        pet.delete()
        return redirect('pet_list')  # Перенаправляем на список

    return render(request, 'nursery/pet_delete.html', {'pet': pet})


class PetViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления животными через API.
    """
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
    permission_classes = [permissions.IsAuthenticated]