from django import forms
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, User

from experiments import auth
from experiments.constants import Role, ROLE_POLICY_TYPE
from experiments.models.casbin import CasbinRule
from experiments.models.measurement import Project
from experiments.models.user import Profile


class ImagingTrackingAdminSite(AdminSite):
    site_header = 'Imaging Experiments Tracker'


class CasbinForm(forms.ModelForm):
    policy_type = forms.CharField(widget=forms.HiddenInput(), initial='g')
    user_id = forms.ChoiceField(label="User", choices=[])
    project_id = forms.ChoiceField(label="Project", choices=[])
    role_name = forms.ChoiceField(label="Role", choices=[])

    def __init__(self, obj=None, *args, **kwargs):
        super(CasbinForm, self).__init__(obj, *args, **kwargs)
        self.fields['user_id'].choices = [
            (u.id, u.username) for u in User.objects.all().order_by('username')]
        self.fields['role_name'].choices = [(r.value, r.value) for r in Role]
        self.fields['project_id'].choices = [
            (p.id, p.name) for p in Project.objects.all().order_by('name')]

    class Meta:
        model = CasbinRule
        exclude = ["action", "v3", "v4", "v5"]


class ProjectRoleFilterByUser(admin.SimpleListFilter):
    """Filter project-roles by user."""
    title = 'User'
    parameter_name = 'user_id'

    def lookups(self, request, model_admin):
        return [(str(u.id), u.username) for u in User.objects.all().order_by('username')]

    def queryset(self, request, queryset):
        value = self.value()
        if value is None:
            return queryset
        return queryset.filter(policy_type=ROLE_POLICY_TYPE, user_id=value)


class ProjectRoleFilterByProject(admin.SimpleListFilter):
    """Filter project-roles by project."""
    title = 'Project'
    parameter_name = 'project_id'

    def lookups(self, request, model_admin):
        return [(str(p.id), p.name) for p in Project.objects.all().order_by('name')]

    def queryset(self, request, queryset):
        value = self.value()
        if value is None:
            return queryset
        return queryset.filter(policy_type=ROLE_POLICY_TYPE, project_id=value)


class ProjectRoleFilterByRole(admin.SimpleListFilter):
    """Filter project-roles by role."""
    title = 'Role'
    parameter_name = 'role_name'

    def lookups(self, request, model_admin):
        return [(r.value, r.value) for r in Role]

    def queryset(self, request, queryset):
        value = self.value()
        if value is None:
            return queryset
        return queryset.filter(policy_type=ROLE_POLICY_TYPE, role_name=value)


class ProjectRoleAdmin(admin.ModelAdmin):
    model = CasbinRule
    form = CasbinForm
    actions = ["delete_role"]
    list_display = ["user", "project", "role_name"]
    # Disabling list_display_links prevents users from changing existing ProjectRoles. 
    # Users can only delete or add. Adding a new ProjectRol will overwrite the existing.
    list_display_links = None
    list_filter = [ProjectRoleFilterByUser, ProjectRoleFilterByRole, ProjectRoleFilterByProject]

    def get_queryset(self, request):
        """Get all the roles assigned to each user for each project."""
        qs = super(ProjectRoleAdmin, self).get_queryset(request)
        return qs.filter(policy_type=ROLE_POLICY_TYPE)

    def has_delete_permission(self, request, obj=None):
        """Hide default delete action in favor of custom delete_rol."""
        return False

    def delete_role(self, request, queryset):
        """Delete a role."""
        for obj in queryset:
            auth.remove_existing_role(obj.user.id, obj.project.id)
    delete_role.short_description = "Delete role(s)"

    def save_model(self, request, obj, form, change):
        """Add a new role."""
        auth.add_role(obj.user.id, obj.project.id, Role(obj.role))


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]


imaging_tracking_admin = ImagingTrackingAdminSite(name="admin")

imaging_tracking_admin.register(User, CustomUserAdmin)
imaging_tracking_admin.register(Group)
imaging_tracking_admin.register(CasbinRule, ProjectRoleAdmin)
