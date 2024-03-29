from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token
from model_utils.models import StatusModel
from model_utils import Choices


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    ''' Creates a token whenever a User is created '''
    if created:
        Token.objects.create(user=instance)


class Job(StatusModel):
    STATUS = Choices('submitted', 'queued', 'done', 'error')
    title = models.CharField(max_length=100, blank=True, default='')
    reference = models.FileField(upload_to='tmp/%Y/%m/%d')
    comparison = models.FileField(upload_to='tmp/%Y/%m/%d')
    owner = models.ForeignKey('auth.User', related_name='jobs')
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_on',)
        unique_together = ('owner', 'title')


class Result(models.Model):
    job = models.ForeignKey('Job', related_name='result')
    rmsd = models.FloatField(default=-99.9)
    energy_ref_to_pdb = models.FloatField(default=-99.9)
    energy_pdb_to_ref = models.FloatField(default=-99.9)
    name = models.CharField(max_length=100, blank=True, default='')
