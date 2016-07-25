import os

from django.conf import settings
from django.db import models

from common import fields
from data_import.utils import get_upload_path

from . import label


class UserData(models.Model):
    """
    Used as key when a User has DataFiles for Genome and Exome Data.
    """

    class Meta:
        verbose_name = 'Genome and exome data'
        verbose_name_plural = verbose_name

    user = fields.AutoOneToOneField(settings.AUTH_USER_MODEL,
                                    related_name=label)

    def __unicode__(self):
        return '%s:%s' % (self.user, 'Genome and Exome data')

    def vcf_data(self):
        return self.vcfdata_set.all()

    @property
    def is_connected(self):
        return self.vcf_data()

    def disconnect(self):
        vcf_data = self.vcf_data()
        vcf_data.delete()

    def get_retrieval_params(self):
        return {
            'vcf_data': [s.as_dict() for s in self.vcf_data()],
            'username': self.user.username
        }


class VCFData(models.Model):
    """
    Storage for a VCF genome or exome file.
    """
    user_data = models.ForeignKey(UserData)
    vcf_file = models.FileField(upload_to=get_upload_path,
                                max_length=1024)
    VCF_SOURCE_CHOICES = (
        ('', '--------'),
        ('dna_land', 'DNALand Genome Imputation'),
        ('full_genomes_corp', 'Full Genomes Corp.'),
        ('genes_for_good', 'Genes For Good'),
        ('genos_exome', 'Genos'),
        ('illumina_uyg', 'Illumina Understand Your Genome'),
        ('twenty_three_and_me', '23andMe Exome Pilot'),
        ('veritas_genetics', 'Veritas Genetics'),
        ('other', 'Other'),
    )
    vcf_source = models.CharField(
        max_length=30,
        choices=VCF_SOURCE_CHOICES,
        default='',
    )
    additional_notes = models.TextField(
        blank=True,
        help_text='Additional notes (optional)')

    class Meta:
        ordering = ['-id']

    @property
    def vcf_file_basename(self):
        return os.path.basename(self.vcf_file.name)

    def as_dict(self):
        data = {
            'additional_notes': self.additional_notes,
            'vcf_source': self.vcf_source,
        }

        try:
            data['vcf_file'] = {'url': self.vcf_file.url}
        except ValueError:
            pass

        return data
