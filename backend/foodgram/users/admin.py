from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.html import format_html

from .models import Subscription, User


@admin.register(User)
class UserAdmin(UserAdmin):

    list_display = ['username', 'email', 'first_name', 'last_name']
    search_fields = ['username', 'email']
    list_filter = ['username', 'email']
    list_editable = ('password',)
    ordering = ['username']
    empty_value_display = ''
    exclude = ['last_login']

    readonly_fields = ('last_login','date_joined')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'author']
    search_fields = [
        'author__username',
        'author__email',
        'user__username',
        'user__email'
    ]
    list_filter = ['author__username', 'user__username']
    empty_value_display = ''
