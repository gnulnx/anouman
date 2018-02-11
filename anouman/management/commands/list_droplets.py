import sys
import subprocess
from time import time, sleep
import digitalocean as do
from colorama import init
from colorama import Fore, Back, Style
init()

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from anouman.utils import get_keys
from cloudgroup.models import Machine, CloudGroup


class Command(BaseCommand):
    help = 'Create a digitial ocean droplet'

    def handle(self, *args, **options):
        groups = CloudGroup.objects.all()
        for g in groups:
            print(Fore.MAGENTA + "Cloud Group: " + Fore.CYAN + g.name)
            print(Fore.YELLOW + " - %-20s %-20s %-20s %-20s" % ("Name", "IP", "Droplet ID", "Cloud Group"))
            for m in g.machines.all():
                try:
                    do.Droplet.get_object(settings.DO_TOKEN, m.droplet_id)
                    print(Fore.GREEN + " - %-20s %-20s %-20s %-20s" % (m.name, m.ip, m.droplet_id, g))
                except do.baseapi.NotFoundError:
                    print(Fore.RED + " - %-20s %-20s %-20s %-20s" % (m.name, m.ip, m.droplet_id, g))


        print(Fore.MAGENTA + "Rouge Machines")
        for m in Machine.objects.filter(cloudgroup__isnull=True):
            try:
                do.Droplet.get_object(settings.DO_TOKEN, m.droplet_id)
                print(Fore.GREEN + " - %-20s %-20s %-20s %-20s" % (m.name, m.ip, m.droplet_id, g))
            except do.baseapi.NotFoundError:
                print(Fore.RED + " - %-20s %-20s %-20s %-20s" % (m.name, m.ip, m.droplet_id, g))
