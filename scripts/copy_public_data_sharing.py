#!/usr/bin/env python
"""
@madprime: Use to map old PublicDataFileAccess to new PublicDataAccess

The old model tracked this per DataFile. The new model tracks per source name
(a charfield expected to match one of the studies or activities app names).
"""
from env_tools import apply_env

apply_env()

import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'open_humans.settings')

django.setup()

from common.utils import get_source_labels
from public_data.models import PublicDataFileAccess, PublicDataAccess


def get_sorted_pdfas():
    source_names = get_source_labels()
    sorted_pdfas = {}

    for pdfa in PublicDataFileAccess.objects.all():
        if not pdfa.data_file:
            print 'skipping: no data_file'
            continue

        member = pdfa.data_file.task.user.member
        source = pdfa.data_file.task.source
        data_file_source = pdfa.data_file.source

        if source != data_file_source:
            print 'skipping: sources do not match "{}" vs. "{}"'.format(
                source, data_file_source)
            continue

        # Abort if not enrolled in Public Data Sharing.
        if (not (member.public_data_participant and
                 member.public_data_participant.enrolled)):
            print 'skipping: not enrolled'
            continue

        # Require recognition of source.
        if source not in source_names:
            print 'skipping: invalid source "{}"'.format(source)
            continue

        # Skip outdated RunKeeper subtypes
        if (source == 'runkeeper' and 'activity'
                not in pdfa.data_file.file.name):
            print 'skipping: old runkeeper subtype'
            continue

        if member not in sorted_pdfas:
            sorted_pdfas[member] = {}

        if source not in sorted_pdfas[member]:
            sorted_pdfas[member][source] = []

        sorted_pdfas[member][source].append(pdfa)

    return sorted_pdfas


def determine_pgp_public_state(pdfas):
    genome_pdfas = [pdfa for pdfa in pdfas
                    if 'genome' in pdfa.data_file.file.name]

    any_public_genome = any(pdfa.is_public for pdfa in genome_pdfas)

    if genome_pdfas and not any_public_genome:
        return False

    survey_pdfas = [pdfa for pdfa in pdfas
                    if 'surveys' in pdfa.data_file.file.name]

    any_public_surveys = any(pdfa.is_public for pdfa in survey_pdfas)

    if survey_pdfas and not any_public_surveys:
        return False

    if survey_pdfas or genome_pdfas:
        return True

    return False


def main():
    """
    Mapping per-file public data info to per-source.
    """
    simple_sources = ['twenty_three_and_me', 'runkeeper', 'go_viral']
    sorted_pdfas = get_sorted_pdfas()

    for member, sources in sorted_pdfas.items():
        print '{}'.format(member)

        for source, pdfas in sources.items():
            # default to is_public=False
            public_state = False

            # PGP data
            if source == 'pgp':
                public_state = determine_pgp_public_state(pdfas)
            else:
                # if every is_public is True
                if all(pdfa.is_public for pdfa in pdfas):
                    public_state = True
                # if every is_public is False
                elif all(not pdfa.is_public for pdfa in pdfas):
                    public_state = False
                # if any is_public is True and the source is simple
                elif (any(pdfa.is_public for pdfa in pdfas)
                      and source in simple_sources):
                    # One type, many versions. Consider public if any public.
                    public_state = True

            new_pda, _ = PublicDataAccess.objects.get_or_create(
                participant=member.public_data_participant,
                data_source=source)

            print '  {}: {}'.format(source, public_state)

            new_pda.is_public = public_state
            new_pda.save()


if __name__ == '__main__':
    main()
