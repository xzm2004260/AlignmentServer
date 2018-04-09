from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from composition.models import Composition


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

    class Status:
        NOTSTARTED = 1
        ONQUEUE = 2
        DONE = 3

        Choices = (
            (NOTSTARTED, 'NOTSTARTED'),
            (ONQUEUE, 'ONQUEUE'),
            (DONE, 'DONE'),
        )

    composition = models.OneToOneField(
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

    timestamps = ArrayField(
        ArrayField(
            models.CharField(max_length=20, blank=True, null=True),
            size=2
        ),
        null=True,
        blank=True
    )

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

