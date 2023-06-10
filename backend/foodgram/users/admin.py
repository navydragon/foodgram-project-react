from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Subscription, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    def password_reset_link(self, obj):
        change_password_url = reverse('admin:password_change', args=[obj.id])
        return format_html('<a href="{}">Сменить пароль</a>',
                           change_password_url)

    list_display = ['username', 'email', 'first_name', 'last_name', 'password_reset_link']
    search_fields = ['username', 'email']
    list_filter = ['username', 'email']
    ordering = ['username']
    empty_value_display = ''
    exclude = ['last_login']
    readonly_fields = ('last_login','password')

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
