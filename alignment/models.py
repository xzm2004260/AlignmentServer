from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
# from django.contrib.postgres.fields import ArrayField
from composition.models import Composition

class Status:
        NOTSTARTED = 1
        ONQUEUE = 2
        DONE = 3
        FAILED = 4

        Choices = (
            (NOTSTARTED, 'NOTSTARTED'),
            (ONQUEUE, 'ONQUEUE'),
            (FAILED, 'DONE'),
            (DONE, 'FAILED'),
        )

class Alignment(models.Model):

    class Accompaniment:
        ACAPELLA = 1
        MULTIINTRUSMENTAL = 2

        Choices = (
            (ACAPELLA, 'ACAPELLA'),
            (MULTIINTRUSMENTAL, 'MULTIINTRUSMENTAL'),
        )

    class Level:
        WORDS = 1
        LINES = 2

        Choices = (
            (WORDS, 'WORDS'),
            (LINES, 'LINES'),
        )

    
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    composition = models.ForeignKey(
        Composition,
        blank=True,
        null=True,
        related_name='compose',
        on_delete=models.CASCADE
    )

    accompaniment = models.IntegerField(
        _('accompaniment'),
        choices=Accompaniment.Choices,
        null=False,
        blank=False
    )

    level = models.IntegerField(
        _('level'),
        choices=Level.Choices,
        default=Level.WORDS,
        null=True,
        blank=True
    )

    status = models.IntegerField(
        _('status'),
        choices=Status.Choices,
        default=Status.NOTSTARTED,
        null=True,
        blank=True
    )
        
    timestamps  = models.TextField(_('timestamps'), blank=True, null=True)

    # timestamps = ArrayField(
    #     ArrayField(
    #         models.CharField(max_length=20, blank=True, null=True),
    #         size=2
    #     ),
    #     null=True,
    #     blank=True
    # )
    error_reason  = models.TextField(_('error_reason'), blank=True, null=True)
    
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        help_text=_('Designates when the alignment is created.')
    )

    class Meta:
        verbose_name = _('alignment')
        verbose_name_plural = _('alignments')
        db_table = 'alignment'

    def get_absolute_url(self):
        return reverse('alignment-detail', args=[str(self.id)])

    def __str__(self):
        return str(self.id)

