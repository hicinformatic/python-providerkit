from django.db import models
from django.utils.translation import gettext_lazy as _
from providerkit.providers.base import ProviderListBase
from virtualqueryset.models import VirtualModel

from providerkit import PROVIDERKIT_FIELDS_SERVICES
from django_providerkit.managers import ProviderServiceManager

import json
from django.utils.safestring import mark_safe

from .define import build_model_field

services = list(ProviderListBase.services_cfg.keys())

class ProviderServiceModelBase(VirtualModel):
    """Base virtual model for provider services (abstract)."""
    name: models.CharField = models.CharField(
        max_length=255,
        verbose_name=_('Name'),
        help_text=_('Service name'),
        primary_key=True,
    )
    objects = ProviderServiceManager()

    class Meta:
        abstract = True
        app_label = 'django_providerkit'
        managed = False
        verbose_name = _('Provider Service')
        verbose_name_plural = _('Provider Services')

    def __str__(self) -> str:
        return str(self.name)

    @property
    def fields_display(self) -> str:
        json_fields = json.dumps(self.fields, indent=4)
        return mark_safe(f"<pre>{json_fields}</pre>")


for name, cfg in PROVIDERKIT_FIELDS_SERVICES.items():
    if name != 'name':
        db_field = build_model_field(cfg)
        ProviderServiceModelBase.add_to_class(name, db_field)


class ProviderServiceModel(ProviderServiceModelBase):
    """Concrete provider service model for django_providerkit."""

    class Meta(ProviderServiceModelBase.Meta):
        abstract = False
