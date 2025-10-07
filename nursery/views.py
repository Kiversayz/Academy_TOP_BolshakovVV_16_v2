from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from rest_framework import viewsets, permissions
from .models import Pet, Pedigree
from .serializers import PetSerializer
from .forms import PetForm, PedigreeForm
from django.forms import inlineformset_factory
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views import View



# ========================
# CBV (Class-Based Views)
# ========================

PedigreeFormSet = inlineformset_factory(
    parent_model=Pet,          # Родительская модель
    model=Pedigree,     # Дочерняя модель
    form=PedigreeForm,
    extra=1,      # Количество пустых форм
    can_delete=False  # Можно ли удалять
)

@method_decorator(cache_page(60), name='dispatch')  # ← Кэшируем весь PetListView
class PetListView(ListView):
    """
    Отображает список всех животных.
    """
    model = Pet
    template_name = 'nursery/pet_list.html'
    context_object_name = 'pets'

    def get_queryset(self):
        # Показываем только активных питомцев
        # Если пользователь — модератор или админ, он видит и неактивных
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Pet.objects.all()
        else:
            return Pet.objects.filter(deactivated_at__isnull=True)

class PetDetailView(DetailView):
    """
    Отображает детальную информацию о конкретном животном.
    """
    model = Pet
    template_name = 'nursery/pet_detail.html'
    context_object_name = 'pet'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Пытаемся получить родословную, если она существует
        try:
            context['pedigree'] = self.object.pedigree  # type: ignore
        except Pedigree.DoesNotExist:
            context['pedigree'] = None

        # Добавляем информацию о правах пользователя
        user = self.request.user
        context['is_moderator'] = user.groups.filter(name='Moderator').exists()
        context['is_admin'] = user.is_staff or user.is_superuser
        context['is_owner'] = self.object.owner == user  # type: ignore
        context['can_deactivate'] = self.object.can_deactivate(user)  # type: ignore
        context['can_delete'] = self.object.can_delete(user) # type: ignore

        return context

    def form_valid(self, form):
        response = super().form_valid(form) # type: ignore
        pedigree_formset = PedigreeFormSet(self.request.POST, self.request.FILES, instance=self.object) # type: ignore
        if pedigree_formset.is_valid():
            pedigree_formset.save()
        return response

    def test_func(self):
        pet = self.get_object()
        user = self.request.user
        # Владелец, модератор или админ могут редактировать
        return (
            pet.owner == user or # type: ignore
            user.groups.filter(name='Moderator').exists() or
            user.is_staff or
            user.is_superuser
        )

    def get_success_url(self):
        return reverse_lazy('pet_detail', kwargs={'pk': self.object.pk}) # type: ignore
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # Увеличиваем счётчик просмотров, если пользователь — не владелец
        self.object.increment_view_count(request.user)  # type: ignore
        return response

class PetCreateView(LoginRequiredMixin, CreateView):
    """
    Создает новое животное.
    """
    model = Pet
    form_class = PetForm
    template_name = 'nursery/pet_create.html'
    success_url = reverse_lazy('pet_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['pedigree_formset'] = PedigreeFormSet(self.request.POST, self.request.FILES, instance=self.object) # type: ignore
        else:
            context['pedigree_formset'] = PedigreeFormSet(instance=self.object) # type: ignore
        return context

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        pedigree_formset = PedigreeFormSet(self.request.POST, self.request.FILES, instance=self.object) # type: ignore
        if pedigree_formset.is_valid():
            pedigree_formset.save()
        return response

class PetUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Pet
    form_class = PetForm
    template_name = 'nursery/pet_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['pedigree_formset'] = PedigreeFormSet(self.request.POST, self.request.FILES, instance=self.object) # type: ignore
        else:
            context['pedigree_formset'] = PedigreeFormSet(instance=self.object)  # type: ignore
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        pedigree_formset = PedigreeFormSet(self.request.POST, self.request.FILES, instance=self.object)  # type: ignore
        if pedigree_formset.is_valid():
            pedigree_formset.save()
        return response

    def test_func(self):
        pet = self.get_object()
        user = self.request.user
        # Владелец, модератор или админ могут редактировать
        return (
            pet.owner == user or                # type: ignore
            user.groups.filter(name='Moderator').exists() or
            user.is_superuser
        )  

    def get_success_url(self):
        return reverse_lazy('pet_detail', kwargs={'pk': self.object.pk})  # type: ignore

class PetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Удаляет конкретное животное.
    """
    model = Pet
    template_name = 'nursery/pet_delete.html'
    success_url = reverse_lazy('pet_list')

    def test_func(self):
        pet = self.get_object()
        # Только админ может удалять
        return pet.can_delete(self.request.user)  # type: ignore

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

class PetDeactivateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        pet = get_object_or_404(Pet, pk=pk)
        if pet.can_deactivate(request.user):
            pet.deactivate()
            messages.success(request, f"Питомец '{pet.name}' деактивирован.")
        else:
            messages.error(request, "У вас нет прав для деактивации этого питомца.")
        return redirect('pet_detail', pk=pk)

class PetActivateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        pet = get_object_or_404(Pet, pk=pk)
        if pet.can_deactivate(request.user):  # Тот же метод — активировать может, кто может деактивировать
            pet.activate()
            messages.success(request, f"Питомец '{pet.name}' активирован.")
        else:
            messages.error(request, "У вас нет прав для активации этого питомца.")
        return redirect('pet_detail', pk=pk)