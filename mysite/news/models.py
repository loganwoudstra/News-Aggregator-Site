from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver


class Article(models.Model):
    headline = models.CharField(max_length=200)
    image = models.URLField(null=True, blank=True)
    link = models.TextField(null=True)
    company = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.headline


class Preferences(models.Model):
    Global = models.BooleanField(default=True)
    CBC = models.BooleanField(default=True)
    BBC = models.BooleanField(default=True)
    Yahoo = models.BooleanField(default=True)
    Google = models.BooleanField(default=True)
    NPR = models.BooleanField(default=True)
    Time = models.BooleanField(default=True)
    Atlantic = models.BooleanField(default=True)
    VOX = models.BooleanField(default=True)
    ESPN = models.BooleanField(default=True)
    Forbes = models.BooleanField(default=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE)


@receiver(post_save, sender=get_user_model())
def create_user_preferences(sender, instance, created, **kwargs):
    if created:
        Preferences.objects.create(user=instance)

