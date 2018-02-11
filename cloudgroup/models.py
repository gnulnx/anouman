# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import ipgetter
from six.moves import input

from django.db import models


class WhiteList(models.Model):
    """
    This model holds a list of all IP addresses that are allowed to ssh into any CloudGroup Machine
    """
    ip = models.GenericIPAddressField(blank=False, null=False, unique=True)
    group = models.ManyToManyField('CloudGroup')


class Machine(models.Model):
    """
    This model holds a single machine instance.
    """
    name = models.CharField(max_length=32, blank=False, null=False)
    droplet_id = models.PositiveSmallIntegerField(blank=True, null=True)
    ip = models.GenericIPAddressField(blank=True, null=True)
    private_ip = models.GenericIPAddressField(blank=True, null=True)
    group = models.ForeignKey('CloudGroup', on_delete=models.CASCADE, blank=True, null=True)


class CloudGroup(models.Model):
    """
    Basically a firewall or security group.
    """
    name = models.CharField(max_length=32, blank=False, null=False)

    def __str__(self):
        return self.name

    def get_context_data(self, **kwargs):
        white_list = WhiteList.objects.filter(group=self)
        print("white_list: %s" % white_list)
        if not white_list.count():
            print("Oh no there isn't a white list...")
            myip = ipgetter.myip()
            print("can we add your local ip: %s" % myip)
            ans = input()
            if 'y' == ans.lower()[0]:
                wl = WhiteList(ip=myip)
                wl.save()
                wl.group.add(self)
                #WhiteList(name=name, group=self).save()

        white_list = WhiteList.objects.filter(group=self).values_list('ip', flat=True)
        print("white_list: %s" % white_list)
    
        machines = Machine.objects.filter(group=self)
        frontend_ips = machines.values_list('ip', flat=True)
        private_ip = machines.values_list('private_ip', flat=True)

        context = {
            "WHITE_LIST": list(white_list),
            "FRONT_END_IPS": list(frontend_ips),
            "PRIVATE_IPS": list(private_ip),
        }
        return context

    def provision(self, hosts_file):
        extra_vars = json.dumps(instance.get_context_data())
        print(extra_vars)
        playbooks = (
            '''ansible-playbook  -s -u root ansible/apt_cleanup.yml -i %s --extra-vars='%s' ''' % (hosts_file, extra_vars),
        )

        print("Made it")

