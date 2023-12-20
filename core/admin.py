from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from tag.models import TagItem
from store.admin import ProductAdmin, ProductImageInline
from store.models import Product
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "email", "first_name", "last_name"),
            },
        ),
    )


class TagItemInline(GenericTabularInline):
    autocomplete_fields = ["tag"]
    model = TagItem
    extra = 0


admin.site.unregister(Product)


@admin.register(Product)
class CustomProductAdmin(ProductAdmin):
    inlines = [TagItemInline, ProductImageInline]

# admin.site.register(Product, CustomProductAdmin)
