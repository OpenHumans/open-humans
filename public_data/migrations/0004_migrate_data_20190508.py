import re

from django.db import migrations


def add_project_member(apps, schema_editor):
    # Using historical versions as recommended for RunPython
    PublicDataAccess = apps.get_model("public_data", "PublicDataAccess")
    DataRequestProjectMember = apps.get_model(
        "private_sharing", "DataRequestProjectMember"
    )
    DataRequestProject = apps.get_model("private_sharing", "DataRequestProject")
    db_alias = schema_editor.connection.alias

    def id_label_to_project(id_label):
        match = re.match(r"direct-sharing-(?P<id>\d+)", id_label)
        if match:
            project = DataRequestProject.objects.using(db_alias).get(
                id=int(match.group("id"))
            )
            return project

    for pda in PublicDataAccess.objects.using(db_alias).filter(project_membership=None):
        project = id_label_to_project(pda.data_source)
        drpm = DataRequestProjectMember.objects.using(db_alias).get(
            project=project, member=pda.participant.member
        )
        pda.project_membership = drpm
        pda.save()


def set_data_source(apps, schema_editor):
    # Using historical versions as recommended for RunPython
    PublicDataAccess = apps.get_model("public_data", "PublicDataAccess")
    db_alias = schema_editor.connection.alias

    for pda in PublicDataAccess.objects.using(db_alias).filter(data_source=None):
        pda.data_source = "direct-sharing-{}".format(pda.project_membership.project.id)
        pda.save()


class Migration(migrations.Migration):

    dependencies = [("public_data", "0003_auto_20190508_2341")]

    operations = [migrations.RunPython(add_project_member, set_data_source)]
