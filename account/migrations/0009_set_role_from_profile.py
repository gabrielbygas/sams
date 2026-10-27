from django.db import migrations


def set_role_from_profile(apps, schema_editor):
    CustomUser = apps.get_model("account", "CustomUser")
    for profile, role in (("student", "student"), ("doctor", "doctor"), ("receptionist", "receptionist")):
        CustomUser.objects.filter(**{f"{profile}__isnull": False}).update(role=role)


class Migration(migrations.Migration):
    dependencies = [("account", "0008_customuser_role")]   # le nom exact généré à l'étape précédente

    operations = [
        migrations.RunPython(set_role_from_profile, migrations.RunPython.noop),
    ]