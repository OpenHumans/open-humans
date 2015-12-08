# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

from data_import.utils import get_source_names


def get_sorted_pdfas(publicdatafileaccess_model):
    source_names = get_source_names()
    pdfas = [pdfa for pdfa in publicdatafileaccess_model.objects.all() if
             pdfa.data_file]
    sorted_pdfas = dict()
    for pdfa in pdfas:
        if not pdfa.data_file:
            continue
        member = pdfa.data_file.task.user.member
        source = pdfa.data_file.task.source
        # Abort if not enrolled in Public Data Sharing.
        if (not (member.public_data_participant and
                 member.public_data_participant.enrolled)):
            continue
        # Require recognition of source.
        if source not in source_names:
            continue
        # Skip outdated RunKeeper subtypes
        if (source == 'runkeeper' and 'activity' not
                in pdfa.data_file.file.name):
            continue
        if member not in sorted_pdfas:
            sorted_pdfas[member] = dict()
        if source not in sorted_pdfas[member]:
            sorted_pdfas[member][source] = list()
        sorted_pdfas[member][source].append(pdfa)
    return sorted_pdfas


def determine_pgp_public_state(pdfas):
    genome_pdfas = [pdfa for pdfa in pdfas if
                    'genome' in pdfa.data_file.file.name]
    any_public_genome = any(
        [pdfa.is_public for pdfa in genome_pdfas])
    if genome_pdfas and not any_public_genome:
        return False
    survey_pdfas = [pdfa for pdfa in pdfas if
                    'surveys' in pdfa.data_file.file.name]
    any_public_surveys = any(
        [pdfa.is_public for pdfa in survey_pdfas])
    if survey_pdfas and not any_public_surveys:
        return False
    if survey_pdfas or genome_pdfas:
        return True
    return False


def map_public_sharing_status(apps, schema_editor):
    """
    Mapping per-file public data info to per-source.
    """
    PublicDataFileAccess = apps.get_model(
        'public_data', 'PublicDataFileAccess')
    PublicDataAccess = apps.get_model('public_data', 'PublicDataAccess')

    sorted_pdfas = get_sorted_pdfas(PublicDataFileAccess)
    for member in sorted_pdfas.keys():
        for source in sorted_pdfas[member]:
            pdfas = sorted_pdfas[member][source]
            sharing_statuses = [pdfa.is_public for pdfa in pdfas]
            if all(sharing_statuses):
                public_state = True
            if not any(sharing_statuses):
                public_state = False
            if source in ['twenty_three_and_me', 'runkeeper', 'go_viral']:
                # One type, many versions. Consider public if any public.
                public_state = True
            # PGP data
            if source == 'pgp':
                public_state = determine_pgp_public_state(pdfas)
            new_pda, _ = PublicDataAccess.objects.get_or_create(
                participant=member.public_data_participant,
                data_source=source)
            if public_state:
                new_pda.is_public = True
                new_pda.save()
            else:
                new_pda.is_public = False
                new_pda.save()


class Migration(migrations.Migration):

    dependencies = [
        ('public_data', '0002_staged_accesslog_removal'),
    ]

    operations = [
        migrations.RenameModel('PublicDataAccess', 'PublicDataFileAccess'),
        migrations.CreateModel(
            name='PublicDataAccess',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_source', models.CharField(max_length=100)),
                ('is_public', models.BooleanField(default=False)),
                ('participant', models.ForeignKey(to='public_data.Participant')),
            ],
        ),
        migrations.RunPython(map_public_sharing_status,
                             reverse_code=migrations.RunPython.noop),
        migrations.DeleteModel('PublicDataFileAccess'),
    ]
