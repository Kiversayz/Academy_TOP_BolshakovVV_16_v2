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
from django.db.models import Q
from core.models import PetComment
from core.forms import PetCommentForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



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
    paginate_by = 5  # Показывать по 5 питомцев на странице

    def get_queryset(self):
        # --- Фильтрация по активности ---
        if self.request.user.is_staff or self.request.user.is_superuser:
            queryset = Pet.objects.all()
        else:
            queryset = Pet.objects.filter(deactivated_at__isnull=True)

        # --- Поиск ---
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(animal_type__icontains=search_query)
            )

        # --- Сортировка ---
        queryset = queryset.order_by('name')

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Передаём поисковый запрос в шаблон, чтобы сохранить его в поле ввода
        context['search_query'] = self.request.GET.get('search', '')
        return context

class PetDetailView(DetailView):
    model = Pet
    template_name = 'nursery/pet_detail.html'
    context_object_name = 'pet'
    slug_field = 'slug'  # Указывает, по какому полю искать
    slug_url_kwarg = 'slug'  # Имя переменной в URL

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pet = self.object

        # --- Логика для комментариев с пагинацией ---
        comment_list = pet.comments.select_related('author__profile').order_by('created_at') # type: ignore
        paginator = Paginator(comment_list, 5)  # Показывать по 5 комментариев на странице
        page_number = self.request.GET.get('page')
        try:
            comments = paginator.page(page_number) # type: ignore
        except PageNotAnInteger:
            # Если страница не является целым числом, показываем первую страницу
            comments = paginator.page(1)
        except EmptyPage:
            # Если страница выходит за пределы допустимого диапазона, показываем последнюю страницу
            comments = paginator.page(paginator.num_pages)

        # Передаём в контекст:
        # - comments (это объект Page, содержит .object_list и данные для пагинации)
        # - is_paginated (булево, нужно для шаблона)
        # - page_obj (объект Page, нужно для шаблона)
        context['comments'] = comments
        context['is_paginated'] = paginator.num_pages > 1
        context['page_obj'] = comments
        # ------------------------------------------

        # Форма для нового комментария
        context['comment_form'] = PetCommentForm()

        # ... (остальная логика для pedigree, прав и т.д.) ...
        try:
            context['pedigree'] = pet.pedigree # type: ignore
        except Pedigree.DoesNotExist:  # Убедись, что Pedigree импортирован
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
        return reverse_lazy('nursery:pet_detail', kwargs={'slug': self.object.slug}) # type: ignore
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # Увеличиваем счётчик просмотров, если пользователь — не владелец
        self.object.increment_view_count(request.user)  # type: ignore
        return response

        # --- Логика для добавления комментария ---
    # Добавляем возможность POST-запроса к этой же странице для создания комментария
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        pet = self.object

        # Проверка аутентификации
        if not request.user.is_authenticated:
            from django.contrib.auth import REDIRECT_FIELD_NAME
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path(), REDIRECT_FIELD_NAME)

        form = PetCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.pet = pet
            comment.author = request.user
            comment.save()
            # Перенаправляем обратно на страницу питомца
            return HttpResponseRedirect(reverse_lazy('nursery:pet_detail', kwargs={'slug': pet.slug})) # type: ignore   
        else:
            context = self.get_context_data()
            context['comment_form'] = form
            messages.error(request, 'Ошибка при добавлении комментария.')
            return self.render_to_response(context)
class PetCreateView(LoginRequiredMixin, CreateView):
    """
    Создает новое животное.
    """
    model = Pet
    form_class = PetForm
    template_name = 'nursery/pet_create.html'
    
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
    
    def get_success_url(self):
        return reverse_lazy('nursery:pet_detail', kwargs={'slug': self.object.slug}) # type: ignore

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
        return reverse_lazy('nursery:pet_detail', kwargs={'slug': self.object.slug})  # type: ignore

class PetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Удаляет конкретное животное.
    """
    model = Pet
    template_name = 'nursery/pet_delete.html'
    success_url = reverse_lazy('nursery:pet_list')

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
    def post(self, request, slug):
        pet = get_object_or_404(Pet, slug=slug)
        if pet.can_deactivate(request.user):
            pet.deactivate()
            messages.success(request, f"Питомец '{pet.name}' деактивирован.")
        else:
            messages.error(request, "У вас нет прав для деактивации этого питомца.")
        return redirect('nursery:pet_detail', slug=slug)

class PetActivateView(LoginRequiredMixin, View):
    def post(self, request, slug):
        pet = get_object_or_404(Pet, slug=slug)
        if pet.can_deactivate(request.user):  # Тот же метод — активировать может, кто может деактивировать
            pet.activate()
            messages.success(request, f"Питомец '{pet.name}' активирован.")
        else:
            messages.error(request, "У вас нет прав для активации этого питомца.")
        return redirect('nursery:pet_detail', slug=slug)

class PetCommentsListView(ListView):
    model = PetComment
    template_name = 'core/comments_partial.html' # Новый шаблон только для комментариев
    context_object_name = 'comments'
    paginate_by = 5

    def get_queryset(self):
        pet_id = self.kwargs.get('pet_id')
        # Фильтруем комментарии по pet_id и сортируем по created_at (старые первыми)
        # ordering = ['created_at'] в Meta должно это обеспечить
        return PetComment.objects.filter(pet_id=pet_id).select_related('author').order_by('created_at')