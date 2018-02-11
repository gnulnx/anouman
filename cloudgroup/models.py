# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import ipgetter
from six.moves import input
import json

from django.db import models


class SSHKey(models.Model):
    """
    A model to hold your ssh key information.
    These keys are often used during user provision.
    CUrrently digitial ocean will provision the servers with the users keys.
    """
    name = models.CharField(max_length=32)
    public = models.TextField()
    private = models.TextField()

    def __str__(self):
        return self.name


class IPAddress(models.Model):
    """
    This model holds a list of all IP addresses that are allowed to ssh into any CloudGroup Machine
    """
    name = models.CharField(max_length=32, blank=True, null=True)
    ip = models.GenericIPAddressField(blank=False, null=False, unique=True)

    def __str__(self):
        return "%s-%s" % (self.name, self.ip)

class Machine(models.Model):
    """
    This model holds a single machine instance.
    """
    name = models.CharField(max_length=32, blank=False, null=False)
    droplet_id = models.PositiveSmallIntegerField(blank=True, null=True)
    ip = models.GenericIPAddressField(blank=True, null=True)
    private_ip = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return self.name


class CloudGroup(models.Model):
    """
    Basically a firewall or security group.
    """
    name = models.CharField(max_length=32, blank=False, null=False)
    sshkeys = models.ManyToManyField('SSHKey')
    whitelist = models.ManyToManyField('IPAddress')
    machines = models.ManyToManyField('Machine')

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

    def hosts_file(self):
        host_name = "%s_hosts" % self.name

        with open(host_name, "w") as f:
            f.write("[%s]\n" % self.name)
            for ip in Machine.objects.filter(group=self).values_list('ip', flat=True):
                f.write("%s\n" % ip)

        return host_name

    def provision(self):
        hosts_file = self.hosts_file()
        extra_vars = json.dumps(self.get_context_data())
        playbooks = (
            '''ansible-playbook  -s -u root ansible/iptables.yml -i %s --extra-vars='%s' ''' % (hosts_file, extra_vars),
        )

        print("Made it")

