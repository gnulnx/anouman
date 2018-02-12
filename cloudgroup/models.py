# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import ipgetter
import time
import subprocess
from six.moves import input
import json
from colorama import init
from colorama import Fore, Back, Style
init(autoreset=True)

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
    firewall = models.BooleanField(default=False)
    sshkeys = models.ManyToManyField('SSHKey')
    whitelist = models.ManyToManyField('IPAddress')
    machines = models.ManyToManyField('Machine')

    def __str__(self):
        return self.name

    def get_context_data(self, **kwargs):
        white_list = self.whitelist.all()
        print("white_list: %s" % white_list)
        if not white_list.count():
            print("Oh no there isn't a white list...")
            myip = ipgetter.myip()
            print("Can I add your local ip: %s" % myip)
            ans = input()
            if 'y' == ans.lower()[0]:
                wl, _ = IPAddress.objects.get_or_create(ip=myip)
                wl.save()
                self.whitelist.add(wl)

        white_list = self.whitelist.values_list('ip', flat=True)
        print("white_list: %s" % white_list)
    
        machines = self.machines
        frontend_ips = machines.values_list('ip', flat=True)
        private_ip = machines.filter(private_ip__isnull=False).values_list('private_ip', flat=True)

        context = {
            "WHITE_LIST": list(white_list),
            "FRONT_END_IPS": list(frontend_ips),
            "PRIVATE_IPS": list(private_ip),
        }
        print(Fore.BLUE + str(context))
        return context

    def hosts_file(self):
        host_name = "%s_hosts" % self.name

        with open(host_name, "w") as f:
            f.write("[%s]\n" % self.name)
            for ip in self.machines.values_list('ip', flat=True):
                f.write("%s ansible_python_interpreter=/usr/bin/python3\n" % ip)

        return host_name

    def provision(self):
        hosts_file = self.hosts_file()
        extra_vars = json.dumps(self.get_context_data())
        playbooks = (
            '''ansible-playbook  -s -u root ansible/iptables.yml -i %s --extra-vars='%s' ''' % (hosts_file, extra_vars),
        )

        for cmd in playbooks:
            # Problem here is that you are writing this after the plays have run
            # TODO This will be deprecated soon
            print("Running: ", cmd)
            with open('cmds', 'a') as f:
                f.write("%s\n" % cmd)

            try:
                logfile = "%s.log" % (self.name)
                logfile_handle = open(logfile,"a")

                subprocess.check_call([cmd], stdout=logfile_handle, stderr=logfile_handle, shell=True)
            except subprocess.CalledProcessError as e:
                print("\n\n*** Failed on first attempts: %s ***" % cmd)
                print("\n\n***error: %s ***" % str(e))
                time.sleep(5)
                try:
                    subprocess.check_call([cmd], stdout=logfile_handle, stderr=logfile_handle, shell=True)
                except subprocess.CalledProcessError as e:
                    print("\n\n*** Command failed: ", cmd)
                    print("\n\n*** error: %s" % str(e))
                    with open('failed', 'a') as f:
                        f.write("%s\n" % cmd)
                    raise

        self.firewall = True
        self.save()
        print(Fore.GREEN + "- Firewall applied")

