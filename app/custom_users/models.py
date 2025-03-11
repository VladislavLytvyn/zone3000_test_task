from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver


class CustomUser(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.username

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

    def check_password(self, raw_password):
        def setter(raw_password):  # noqa
            self.set_password(raw_password)
            self._password = None
            self.save(update_fields=["password"])

        return check_password(raw_password, self.password, setter)

    def as_dict(self):
        return {
            "username": self.username,
        }


@receiver(pre_save, sender=CustomUser)
def password_hashing(sender, instance, **kwargs):
    instance.set_password(instance.password)
