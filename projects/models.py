from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from constants import PROJECT_MODEL_NAME_MAX_LENGTH


class Project(models.Model):
    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = [
        (STATUS_OPEN, _("Открыт")),
        (STATUS_CLOSED, _("Закрыт")),
    ]
    name = models.CharField(
        max_length=PROJECT_MODEL_NAME_MAX_LENGTH,
        verbose_name=_("Название проекта"),
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Описание"),
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name=_("Владелец проекта"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата создания"),
    )
    github_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("Ссылка на GitHub"),
    )
    status = models.CharField(
        max_length=max(len(choice[0]) for choice in STATUS_CHOICES),
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
        verbose_name=_("Статус"),
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
        verbose_name=_("Участники"),
    )

    class Meta:
        verbose_name = _("Проект")
        verbose_name_plural = _("Проекты")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def is_open(self):
        return self.status == self.STATUS_OPEN
