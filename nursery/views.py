from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from rest_framework import viewsets, permissions
from .models import Pet, Pedigree
from .serializers import PetSerializer
from .forms import PetForm, PedigreeForm
from django.http import HttpResponseForbidden
from django.forms import inlineformset_factory
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


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
        return context

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
        return pet.owner == self.request.user or self.request.user.is_superuser  # type: ignore

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