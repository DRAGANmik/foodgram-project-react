from django.contrib import admin
from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User

from .models import Subscription


class UserAdmin(BaseUserAdmin):
    list_display = (
        "id",
        "username",
        "is_active",
        "is_staff",
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


@register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        "author",
        "subscriber",
    ]
    search_fields = [
        "author__username",
        "subscriber__username",
    ]
    list_filter = [
        "author__username",
        "subscriber__username",
    ]


admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
