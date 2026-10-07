from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'is_banned',
        'is_staff',
        'is_superuser',
        'date_joined',
    )
    list_filter = ('role', 'is_banned', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_editable = ('role', 'is_banned')
    ordering = ('-date_joined',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Profile Information', {
            'fields': ('role', 'is_banned', 'avatar', 'bio'),
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Profile Information', {
            'fields': ('role', 'is_banned', 'avatar', 'bio'),
        }),
    )

    actions = ['ban_users', 'unban_users', 'make_admin', 'make_super_admin', 'make_user']

    @admin.action(description="Ban selected users")
    def ban_users(self, request, queryset):
        updated = queryset.update(is_banned=True)
        self.message_user(request, f"{updated} user(s) successfully banned.")

    @admin.action(description="Unban selected users")
    def unban_users(self, request, queryset):
        updated = queryset.update(is_banned=False)
        self.message_user(request, f"{updated} user(s) successfully unbanned.")

    @admin.action(description="Promote selected users to Admin")
    def make_admin(self, request, queryset):
        for user in queryset:
            user.role = User.Role.ADMIN
            user.save()
        self.message_user(request, f"{queryset.count()} user(s) promoted to Admin.")

    @admin.action(description="Promote selected users to Super Admin")
    def make_super_admin(self, request, queryset):
        for user in queryset:
            user.role = User.Role.SUPER_ADMIN
            user.save()
        self.message_user(request, f"{queryset.count()} user(s) promoted to Super Admin.")

    @admin.action(description="Demote selected users to standard User")
    def make_user(self, request, queryset):
        for user in queryset:
            user.role = User.Role.USER
            user.save()
        self.message_user(request, f"{queryset.count()} user(s) set to standard User.")


