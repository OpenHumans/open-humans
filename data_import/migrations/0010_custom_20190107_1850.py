# Custom migration to make datafile not foreign key

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_import', '0009_auto_20190103_1838'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datafilekey',
            name='datafile',
            field=models.IntegerField(db_column='datafile_id')
        ),
        migrations.RenameField(
            model_name='datafilekey',
            old_name='datafile',
            new_name='datafile_id',
        ),
    ]
