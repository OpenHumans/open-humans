# Generated by Django 2.1.7 on 2019-02-21 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data_import", "0012_datatypes"),
        ("private_sharing", "0019_auto_20190214_1915"),
    ]

    operations = [
        migrations.AddField(
            model_name="datarequestproject",
            name="datatypes",
            field=models.ManyToManyField(
                related_name="data_types", to="data_import.DataTypes"
            ),
        ),
        migrations.AddField(
            model_name="projectdatafile",
            name="datatypes",
            field=models.ManyToManyField(
                related_name="datafile_datatypes", to="data_import.DataTypes"
            ),
        ),
    ]
