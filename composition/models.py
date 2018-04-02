from django.db import models
from django.utils.translation import ugettext_lazy as _
from services.utils import update_filename


class Composition(models.Model):
    lyrics = models.FileField(upload_to=update_filename, blank=False, null=False)
    title = models.CharField(_('title'), max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        help_text=_('Designates when the composition is created.')
    )

    class Meta:
        verbose_name = _('composition')
        verbose_name_plural = _('compositions')
        db_table = 'composition'

    def __str__(self):
        return self.title




