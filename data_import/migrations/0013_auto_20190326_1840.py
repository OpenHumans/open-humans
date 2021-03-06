# Generated by Django 2.1.3 on 2019-03-26 18:40

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("data_import", "0012_auto_20190312_2031")]

    operations = [
        migrations.CreateModel(
            name="AWSDataFileAccessLog",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("bucket_owner", models.CharField(max_length=100)),
                ("bucket", models.CharField(max_length=64)),
                ("time", models.DateTimeField()),
                ("remote_ip", models.GenericIPAddressField(null=True)),
                ("requester", models.CharField(max_length=64, null=True)),
                ("request_id", models.CharField(max_length=32, null=True)),
                ("operation", models.CharField(max_length=32, null=True)),
                ("bucket_key", models.CharField(max_length=254, null=True)),
                ("request_uri", models.CharField(max_length=254, null=True)),
                ("status", models.IntegerField(null=True)),
                ("error_code", models.CharField(max_length=64, null=True)),
                ("bytes_sent", models.IntegerField(null=True)),
                ("object_size", models.IntegerField(null=True)),
                ("total_time", models.IntegerField(null=True)),
                ("turn_around_time", models.IntegerField(null=True)),
                ("referrer", models.CharField(max_length=254, null=True)),
                ("user_agent", models.CharField(max_length=254, null=True)),
                ("version_id", models.CharField(max_length=128, null=True)),
                ("host_id", models.CharField(max_length=128, null=True)),
                ("signature_version", models.CharField(max_length=32, null=True)),
                ("cipher_suite", models.CharField(max_length=128, null=True)),
                ("auth_type", models.CharField(max_length=32, null=True)),
                ("host_header", models.CharField(max_length=64, null=True)),
                (
                    "data_file",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="aws_access_logs",
                        to="data_import.DataFile",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="newdatafileaccesslog",
            name="aws_url",
            field=models.CharField(max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name="newdatafileaccesslog",
            name="data_file_key",
            field=django.contrib.postgres.fields.jsonb.JSONField(
                default=dict, null=True
            ),
        ),
        migrations.AddField(
            model_name="awsdatafileaccesslog",
            name="oh_data_file_access_log",
            field=models.ManyToManyField(to="data_import.NewDataFileAccessLog"),
        ),
    ]
