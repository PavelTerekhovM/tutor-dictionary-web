from django.urls import path
from .views import (
    Dictionary_list,
    My_dictionary_list,
    Dictionary_detail,
    add_dictionary,
    remove_dictionary,
    make_public,
    make_private,
    dictionary_delete,
    dictionary_search
)
from .views import AddDictionaryView


app_name = 'dictionary'

urlpatterns = [
    path(
        '',
        Dictionary_list.as_view(),
        name='list_of_dictionaries'
    ),
    path(
        'my_dictionaries',
        My_dictionary_list.as_view(),
        name='my_dictionaries'
    ),
    path(
        'upload/',
        AddDictionaryView.as_view(),
        name='upload_file'
    ),
    path(
        '<int:pk>/',
        Dictionary_detail.as_view(),
        name='dictionary_detail'
    ),
    path(
        'add/',
        add_dictionary,
        name='add_dictionary'
    ),
    path(
        'remove/',
        remove_dictionary,
        name='remove_dictionary'
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
