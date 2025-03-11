import uuid

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db import models


class RedirectRuleManager(models.Manager):
    def get_by_id(self, redirect_rule_id, user):
        try:
            return self.get(id=redirect_rule_id, user=user)
        except RedirectRule.DoesNotExist:
            return None

    def get_by_identifier(self, redirect_identifier):
        try:
            return self.get(redirect_identifier=redirect_identifier)
        except RedirectRule.DoesNotExist:
            return None


class RedirectRule(models.Model):
    objects = RedirectRuleManager()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    redirect_url = models.URLField()
    is_private = models.BooleanField(default=False)
    redirect_identifier = models.CharField(
        max_length=10,
        unique=True,
        editable=False,
        db_index=True,
    )
    user = models.ForeignKey(
        "custom_users.CustomUser",
        on_delete=models.CASCADE,
        related_name="redirect_rules",
        null=True,
        blank=True,
    )

    def as_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "redirect_url": self.redirect_url,
            "is_private": self.is_private,
            "redirect_identifier": self.redirect_identifier,
            "user": self.user.as_dict() if self.user else None,
        }


@receiver(pre_save, sender=RedirectRule)
def redirect_identifier_pre_save(sender, instance, **kwargs):
    if not instance.redirect_identifier:
        instance.redirect_identifier = str(uuid.uuid4())[:10]