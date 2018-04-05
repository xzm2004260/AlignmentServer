from django.db import models
from django.utils.translation import ugettext_lazy as _
from composition.models import Composition
import uuid


class Alignment(models.Model):
    compositions = models.OneToOneField(Composition,blank=True, null=True, related_name='compose', on_delete=models.CASCADE)
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        help_text=_('Designates when the alignment is created.')
    )

    class Meta:
        verbose_name = _('alignment')
        verbose_name_plural = _('alignments')
        db_table = 'alignment'

    def __str__(self):
        return self.created_at

