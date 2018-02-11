# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class WhiteList(models.Model):
    """
    This model holds a list of all IP addresses that are allowed to ssh into any CloudGroup Machine
    """
    ip = models.GenericIPAddressField(blank=False, null=False)
    group = models.ForeignKey('CloudGroup', on_delete=models.CASCADE)


class Machine(models.Model):
    """
    This model holds a single machine instance.
    """
    name = models.CharField(max_length=32, blank=False, null=False)
    droplet_id = models.PositiveSmallIntegerField(blank=True, null=True)
    ip = models.GenericIPAddressField(blank=True, null=True)
    group = models.ForeignKey('CloudGroup', on_delete=models.CASCADE, blank=True, null=True)


class CloudGroup(models.Model):
    name = models.CharField(max_length=32, blank=False, null=False)

