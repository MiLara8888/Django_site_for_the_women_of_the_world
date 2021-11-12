from django.contrib.auth import logout, login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *
from .forms import *
from django.views.generic import ListView, DetailView, CreateView, FormView
from .utils import *


class WomenHome(DataMixin, ListView):
    paginate_by = 3
    model = Women  # ссылается на модель связанный с отображаемым списком
    template_name = 'women/index.html'  # явно указали путь
    context_object_name = 'posts'

    def get_context_data(self, *, object_list=None,
                         **kwargs):  # специальная функция для передачи динамического контекста
        context = super().get_context_data(**kwargs)  # ПОЛУЧАЕМ КОНТЕКСТ УЖЕ СФОРМИРОВАННОГО ШАБЛОНА (словарь)
        c_def = self.get_user_context(title='Главная страница')  # через self

        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):  # спец метод для возвращения только опубликовынвх статей
        return Women.objects.filter(is_published=True).select_related('cat')


# def index(request):
#     posts = Women.objects.all()
#     context = {'menu': menu, 'title': 'Главная страница', 'posts': posts, 'cat_selected': 0}
#     return render(request, 'women/index.html', context=context)


class AddPage(LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddPostForm  # указывается класс на основе которогосоздается форма
    template_name = 'women/addpage.html'
    success_url = reverse_lazy(
        'home')  # адрес мршрута куда хотим перенапраиться после добавление, по умолчанию определили другой в моделс в методе
    login_url = reverse_lazy('home')  # куда перенаправить если пользователь не зарегистрирован
    raise_exception = True

    def get_context_data(self, *, object_list=None,
                         **kwargs):  # специальная функция для передачи динамического контекста
        context = super().get_context_data(**kwargs)  # ПОЛУЧАЕМ КОНТЕКСТ УЖЕ СФОРМИРОВАННОГО ШАБЛОНА (словарь)
        c_def = self.get_user_context(title='Добавить запись')
        return dict(list(context.items()) + list(c_def.items()))


# def addpage(request):
#     if request.method == 'POST':
#         form = AddPostForm(request.POST, request.FILES)  # здесь формируется форма с заполненными данными
#         if form.is_valid():  # здесь проверяем корректность
#             # print(form.cleaned_data)
#
#             form.save()
#             return redirect('home')  # и перенапрявляем в хом
#
#     else:
#         form = AddPostForm()  # формируем пустую форму если запрос первый
#
#     context = {'menu': menu,
#                'title': 'Добавление статьи',
#                'form': form,
#                }
#     return render(request, 'women/addpage.html', context=context)


class ShowPost(DataMixin, DetailView):
    model = Women
    template_name = 'women/post.html'
    slug_url_kwarg = 'post_slug'  # специальная переменная
    context_object_name = 'post'  # указываем в какую переменную будут помещаться данные взятые из модели

    def get_context_data(self, *, object_list=None,
                         **kwargs):  # специальная функция для передачи динамического контекста
        context = super().get_context_data(**kwargs)  # ПОЛУЧАЕМ КОНТЕКСТ УЖЕ СФОРМИРОВАННОГО ШАБЛОНА (словарь)
        c_def = self.get_user_context(title=context['post'])
        return dict(list(context.items()) + list(c_def.items()))


# def show_post(request, post_slug):
#     post = get_object_or_404(Women, slug=post_slug)
#     context = {
#         'post': post,
#         'menu': menu,
#         'title': post.title,
#         'cat_selected': post.cat_id,
#     }
#     return render(request, 'women/post.html', context=context)


class WomenCategory(DataMixin, ListView):
    model = Women  # ссылается на модель связанный с отображаемым списком
    template_name = 'women/index.html'  # явно указали путь
    context_object_name = 'posts'
    allow_empty = False

    def get_queryset(self):  # спец метод для возвращения только опубликовынвх статей
        return Women.objects.filter(cat__slug=self.kwargs['cat_slug'], is_published=True).select_related('cat')

    def get_context_data(self, *, object_list=None,
                         **kwargs):  # специальная функция для передачи динамического контекста
        context = super().get_context_data(**kwargs)  # ПОЛУЧАЕМ КОНТЕКСТ УЖЕ СФОРМИРОВАННОГО ШАБЛОНА (словарь)
        c_def = self.get_user_context(title='Категория - ' + str(context['posts'][0].cat),
                                      cat_selected=context['posts'][0].cat_id)
        return dict(list(context.items()) + list(c_def.items()))


# def show_category(request, cat_id):
#     posts = Women.objects.filter(cat_id=cat_id)
#
#     if len(posts) == 0:
#         raise Http404()
#
#     context = {
#         'posts': posts,
#         'menu': menu,
#         'title': 'Отображение по рубрикам',
#         'cat_selected': cat_id,
#     }
#
#     return render(request, 'women/index.html', context=context)





def about(request):
    context = {'menu': menu, 'title': "О сайте"}
    return render(request, 'women/about.html', context=context)


def pageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена :'() </h1>")


class RegisterUser(DataMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'women/register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Регистрация')
        return dict(list(context.items()) + list(c_def.items()))

    def form_valid(self, form):  # вызывается при успещной регистрации
        user = form.save()  # сохраняем пользователь в бд
        login(self.request, user)  # авторизовываем
        return redirect('home')


class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'women/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Авторизaция')
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self):  # перенаправление если форма прошла валидацию
        return reverse_lazy('home')


def logout_user(request):
    logout(request)  # функция реавторизации
    return redirect('login')


class ContactFormViev(DataMixin,FormView):
    form_class = ContactForm
    template_name = 'women/contact.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Обратная связь')
        return dict(list(context.items()) + list(c_def.items()))

    def form_valid(self, form):
        print(form.cleaned_data)
        return redirect('home')
