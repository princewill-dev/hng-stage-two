from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Organisation


class UserAdmin(BaseUserAdmin):
    list_display = ('firstName', 'lastName', 'email', 'is_staff', 'is_superuser')
    search_fields = ('firstName', 'lastName', 'email')
    ordering = ('firstName',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('firstName', 'lastName', 'phone')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'firstName', 'lastName', 'phone', 'password1', 'password2'),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('created_organisations', 'member_organisations')

    def get_list_display(self, request):
        return ('firstName', 'lastName', 'email', 'is_staff', 'is_superuser')
    

class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('orgId', 'name', 'created_by', 'description')
    search_fields = ('orgId', 'name', 'created_by__firstName', 'created_by__lastName', 'description')
    readonly_fields = ('orgId', 'created_by')
    fieldsets = (
        (None, {
            'fields': ('orgId', 'name', 'description', 'created_by', 'members')
        }),
    )
    filter_horizontal = ('members',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('created_by')
    




admin.site.register(User, UserAdmin)
admin.site.register(Organisation, OrganisationAdmin)
