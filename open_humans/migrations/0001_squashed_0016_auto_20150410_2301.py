# -*- coding: utf-8 -*-

from django.db import models, migrations
import django.core.validators
import open_humans.storage
import django.utils.timezone
from django.conf import settings
import open_humans.models


def add_member_ids(apps, *args):
    Member = apps.get_model('open_humans', 'Member')

    for member in Member.objects.all():
        if not member.member_id:
            member.member_id = open_humans.models.random_member_id()
            member.save()


class Migration(migrations.Migration):

    replaces = [('open_humans', '0001_initial'), ('open_humans', '0002_auto_20141111_1400'), ('open_humans', '0003_rename_profile_to_member'), ('open_humans', '0004_auto_20150106_1828'), ('open_humans', '0005_rename_content_type'), ('open_humans', '0006_auto_20150123_2121'), ('open_humans', '0007_member_name'), ('open_humans', '0008_member_member_id'), ('open_humans', '0009_random_member_id'), ('open_humans', '0010_auto_20150311_1922'), ('open_humans', '0011_auto_20150326_0650'), ('open_humans', '0012_add_username_lower_index'), ('open_humans', '0013_auto_20150403_2323'), ('open_humans', '0014_rename_openhumansuser'), ('open_humans', '0015_auto_20150410_0042'), ('open_humans', '0016_auto_20150410_2301')]

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, max_length=30, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, verbose_name='username')),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'auth_user',
            },
            managers=[
                ('objects', open_humans.models.OpenHumansUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('profile_image', models.ImageField(upload_to=open_humans.models.get_member_profile_image_upload_path, blank=True)),
                ('about_me', models.TextField(blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
                ('allow_user_messages', models.BooleanField(default=True, verbose_name='Allow members to contact me')),
                ('newsletter', models.BooleanField(default=True, verbose_name='Receive Open Humans news and updates')),
            ],
            managers=[
                ('objects', open_humans.models.OpenHumansUserManager()),
            ],
        ),
        migrations.RunSQL(
            sql="UPDATE django_content_type\n         SET model = 'member'\n         WHERE model = 'profile' AND\n               app_label = 'open_humans';",
            reverse_sql="UPDATE django_content_type\n                 SET model = 'profile'\n                 WHERE model = 'member' AND\n                       app_label = 'open_humans';",
        ),
        migrations.AlterField(
            model_name='member',
            name='allow_user_messages',
            field=models.BooleanField(default=False, verbose_name='Allow members to contact me'),
        ),
        migrations.AddField(
            model_name='member',
            name='name',
            field=models.CharField(default='', max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='member',
            name='member_id',
            field=models.CharField(max_length=8, blank=True),
        ),
        migrations.RunPython(
            code=add_member_ids,
        ),
        migrations.AlterField(
            model_name='member',
            name='member_id',
            field=models.CharField(default=open_humans.models.random_member_id, unique=True, max_length=8),
        ),
        migrations.AlterField(
            model_name='member',
            name='profile_image',
            field=models.ImageField(storage=open_humans.storage.PublicStorage(), upload_to=open_humans.models.get_member_profile_image_upload_path, blank=True),
        ),
        migrations.RunSQL(
            sql='CREATE UNIQUE INDEX auth_user_username_lower\n                 ON auth_user (LOWER(username));',
            reverse_sql='DROP INDEX auth_user_username_lower;',
        ),
        migrations.AlterField(
            model_name='member',
            name='profile_image',
            field=models.ImageField(storage=open_humans.storage.PublicStorage(), max_length=1024, upload_to=open_humans.models.get_member_profile_image_upload_path, blank=True),
        ),
        migrations.RunSQL(
            sql="UPDATE django_content_type\n         SET model = 'user'\n         WHERE model = 'openhumansuser' AND\n               app_label = 'open_humans';",
            reverse_sql="UPDATE django_content_type\n                 SET model = 'openhumansuser'\n                 WHERE model = 'user' AND\n                       app_label = 'open_humans';",
        ),
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', open_humans.models.OpenHumansUserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='email address', blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(null=True, verbose_name='last login', blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'A user with that username already exists.'}, max_length=30, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, verbose_name='username'),
        ),
        migrations.AlterModelManagers(
            name='member',
            managers=[
            ],
        ),
    ]
