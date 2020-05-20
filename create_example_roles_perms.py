from experiments.models import Permission, Role, Project, ProjectRole

add_permission, _ = Permission.objects.get_or_create(
    codename="add_project_measurements",
    description="Can add new measurements to project")
delete_permission, _ = Permission.objects.get_or_create(
    codename="delete_project_measurements",
    description="Can delete measurements from project")
change_permission, _ = Permission.objects.get_or_create(
    codename="change_project_measurements",
    description="Can modify existing measurements in project")
view_permission, _ = Permission.objects.get_or_create(
    codename="view_project_measurements",
    description="Can view the project measurements")

viewer, _ = Role.objects.get_or_create(name="Measurements viewer")
viewer.permissions.add(view_permission)

mmanager, _ = Role.objects.get_or_create(name="Measurement manager")
mmanager.permissions.add(view_permission)
mmanager.permissions.add(add_permission)
mmanager.permissions.add(change_permission)
mmanager.permissions.add(delete_permission)

for project in Project.objects.all():
    ProjectRole.objects.get_or_create(project=project, role=viewer)
