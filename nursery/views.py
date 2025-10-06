from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from rest_framework import viewsets, permissions
from .models import Pet
from .serializers import PetSerializer
from .forms import PetForm
from django.http import HttpResponseForbidden

# ========================
# CBV (Class-Based Views)
# ========================

class PetListView(ListView):
    """
    Отображает список всех животных.
    """
    model = Pet
    template_name = 'nursery/pet_list.html'
    context_object_name = 'pets'

class PetDetailView(DetailView):
    """
    Отображает детальную информацию о конкретном животном.
    """
    model = Pet
    template_name = 'nursery/pet_detail.html'
    context_object_name = 'pet'

class PetCreateView(LoginRequiredMixin, CreateView):
    """
    Создает новое животное.
    """
    model = Pet
    form_class = PetForm
    template_name = 'nursery/pet_create.html'
    success_url = reverse_lazy('pet_list')

    def form_valid(self, form):
        # Устанавливаем владельца перед сохранением
        form.instance.owner = self.request.user
        return super().form_valid(form)

class PetUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Обновляет информацию о конкретном животном.
    """
    model = Pet
    form_class = PetForm
    template_name = 'nursery/pet_update.html'

    def test_func(self):
        pet = self.get_object()
        # Владелец или админ может редактировать
        return pet.owner == self.request.user or self.request.user.is_staff # type: ignore

    def get_success_url(self):
        return reverse_lazy('pet_detail', kwargs={'pk': self.object.pk}) # pyright: ignore[reportAttributeAccessIssue]

class PetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Удаляет конкретное животное.
    """
    model = Pet
    template_name = 'nursery/pet_delete.html'
    success_url = reverse_lazy('pet_list')

    def test_func(self):
        pet = self.get_object()
        # Владелец или админ может удалять
        return pet.owner == self.request.user or self.request.user.is_staff # type: ignore

# ========================
# API ViewSet (остаётся как есть)
# ========================

class PetViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления животными через API.
    """
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
    permission_classes = [permissions.IsAuthenticated]