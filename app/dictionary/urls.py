from django.urls import path
from .views import (
    SignUpView,
    Dictionary_list,
    about,
    My_dictionary_list,
    Dictionary_detail,
    student_add,
    student_remove,
    make_public,
    make_private,
    dictionary_delete,
    dictionary_search
)
from django.contrib.auth import views as auth_views
from .views import AddDictionaryView
from .forms import MyPasswordChangeForm

urlpatterns = [
    # registration, login etc
    path('register/', SignUpView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path(
        'logout/',
        auth_views.LogoutView.as_view(
            template_name='registration/logout.html',
            next_page=None
        ), name='logout'
    ),
    path(
        'password_change/',
        auth_views.PasswordChangeView.as_view(
            template_name='registration/password_change.html',
            form_class=MyPasswordChangeForm
        ),
        name='password_change'
    ),
    path(
        'password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='registration/password_change_done.html'
        ),
        name='password_change_done'
    ),
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(),
        name='password_reset'
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete'
    ),

    # listview, detailview, etc
    path(
        '',
        Dictionary_list.as_view(),
        name='list_of_dictionaries'
    ),
    path(
        'about/',
        about,
        name='about'
    ),
    path(
        'my_dictionaries',
        My_dictionary_list.as_view(),
        name="my_dictionaries"
    ),
    path(
        'upload/',
        AddDictionaryView.as_view(),
        name='upload_file'
    ),
    path(
        '<slug:slug>/<int:pk>/',
        Dictionary_detail.as_view(),
        name="dictionary_detail"
    ),
    path(
        'add/<slug:slug>/<int:pk>/',
        student_add,
        name='student_add'
    ),
    path(
        'remove/<slug:slug>/<int:pk>/',
        student_remove,
        name='student_remove'
    ),
    path(
        'make_public/<slug:slug>/<int:pk>/',
        make_public,
        name='make_public'
    ),
    path(
        'make_private/<slug:slug>/<int:pk>/',
        make_private,
        name='make_private'
    ),
    path(
        'dictionary_delete/<slug:slug>/<int:pk>/',
        dictionary_delete,
        name='dictionary_delete'
    ),
    path(
        'search/',
        dictionary_search,
        name='dictionary_search'
    ),
]
