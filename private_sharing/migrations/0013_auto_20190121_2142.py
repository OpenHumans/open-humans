# Generated by Django 2.1.3 on 2019-01-21 21:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('private_sharing', '0012_datarequestproject_approval_history'),
    ]

    operations = [
        migrations.AddField(
            model_name='datarequestproject',
            name='add_data',
            field=models.BooleanField(default=False, help_text='If your project collects data, choose "Add data" here. If you choose "Add data", you will need to provide a "Returned data description" below.', verbose_name='Add data'),
        ),
        migrations.AddField(
            model_name='datarequestproject',
            name='explore_share',
            field=models.BooleanField(default=False, help_text='If your project performs analysis on data, choose "Explore & share".', verbose_name='Explore & share'),
        ),
        migrations.AlterField(
            model_name='datarequestproject',
            name='returned_data_description',
            field=models.CharField(blank=True, help_text='Leave this blank if your project doesn\'t plan to add or return new data for your members.  If your project is set to be displayed under "Add data", then you must provide this information.', max_length=140, verbose_name='Description of data you plan to upload to member  accounts (140 characters max)'),
        ),
    ]
