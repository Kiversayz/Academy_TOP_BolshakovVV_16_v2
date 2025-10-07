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

from core.models import PetComment
from core.forms import PetCommentForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect



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
    model = Pet
    template_name = 'nursery/pet_detail.html'
    context_object_name = 'pet'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pet = self.object
        
        # --- Логика для комментариев ---
        # Получаем комментарии для этого питомца, отсортированные по created_at (старые первыми)
        # ordering = ['created_at'] в Meta должно это обеспечить, но явно укажем для надежности
        comments = pet.comments.select_related('author__profile').all()   # type: ignore

        # select_related('author') оптимизирует запросы, извлекая данные User сразу
        
        # Форма для нового комментария
        comment_form = PetCommentForm()

        context['comments'] = comments
        context['comment_form'] = comment_form
        # -----------------------------

        # ... (ваша существующая логика для pedigree, прав и т.д.) ...
        try:
            context['pedigree'] = pet.pedigree # type: ignore

        except Pedigree.DoesNotExist: # Убедитесь, что Pedigree импортирован
            context['pedigree'] = None
            
        user = self.request.user
        context['is_moderator'] = user.groups.filter(name='Moderator').exists()
        context['is_admin'] = user.is_staff or user.is_superuser
        context['is_owner'] = pet.owner == user # type: ignore

        context['can_deactivate'] = pet.can_deactivate(user) # type: ignore

        context['can_delete'] = pet.can_delete(user) # type: ignore

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

        # --- Логика для добавления комментария ---
    # Добавляем возможность POST-запроса к этой же странице для создания комментария
    def post(self, request, *args, **kwargs):
        self.object = self.get_object() # Получаем объект Pet
        pet = self.object
        
        # Проверка аутентификации (можно вынести в декоратор или миксин)
        if not request.user.is_authenticated:
             # Можно вернуть ошибку или перенаправить на логин
             from django.contrib.auth import REDIRECT_FIELD_NAME
             from django.contrib.auth.views import redirect_to_login
             return redirect_to_login(request.get_full_path(), REDIRECT_FIELD_NAME)
        
        form = PetCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.pet = pet
            comment.author = request.user # Устанавливаем автора
            comment.save()
            # Перенаправляем обратно на страницу питомца, чтобы обновить список комментариев
            # return HttpResponseRedirect(request.path_info) # Простое обновление
            from django.urls import reverse
            return HttpResponseRedirect(reverse('pet_detail', args=[pet.pk])) # Явное указание URL
        else:
            # Если форма невалидна, отображаем страницу с ошибками
            context = self.get_context_data()
            context['comment_form'] = form # Передаем форму с ошибками
            # Можно добавить сообщение об ошибке
            from django.contrib import messages
            messages.error(request, 'Ошибка при добавлении комментария. Проверьте форму.')
            # Возвращаем тот же шаблон с контекстом (включая ошибки формы)
            return self.render_to_response(context)
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

class PetCommentsListView(ListView):
    model = PetComment
    template_name = 'core/comments_partial.html' # Новый шаблон только для комментариев
    context_object_name = 'comments'

    def get_queryset(self):
        pet_id = self.kwargs.get('pet_id')
        # Фильтруем комментарии по pet_id и сортируем по created_at (старые первыми)
        # ordering = ['created_at'] в Meta должно это обеспечить
        return PetComment.objects.filter(pet_id=pet_id).select_related('author').order_by('created_at')