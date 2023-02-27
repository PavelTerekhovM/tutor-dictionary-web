from django.contrib import admin
from .models import Dictionary, Word


class DictionaryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'created', 'status')
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Dictionary, DictionaryAdmin)


class WordAdmin(admin.ModelAdmin):
    list_display = (
        'body', 'slug', 'translations', 'example', 'created'
    )
    prepopulated_fields = {'slug': ('body',)}


admin.site.register(Word, WordAdmin)
