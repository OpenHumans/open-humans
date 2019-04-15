# Generated by Django 2.2 on 2019-04-12 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data_import", "0019_datatype"),
        ("private_sharing", "0020_auto_20190222_0036"),
    ]

    operations = [
        migrations.AddField(
            model_name="datarequestproject",
            name="auto_add_datatypes",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="datarequestproject",
            name="registered_datatypes",
            field=models.ManyToManyField(to="data_import.DataType"),
        ),
        migrations.AddField(
            model_name="projectdatafile",
            name="datatypes",
            field=models.ManyToManyField(to="data_import.DataType"),
        ),
    ]
