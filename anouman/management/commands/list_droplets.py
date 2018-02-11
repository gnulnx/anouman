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
from cloudgroup.models import Machine


class Command(BaseCommand):
    help = 'Create a digitial ocean droplet'

    def handle(self, *args, **options):
        machines = Machine.objects.all()

        print(Fore.YELLOW + "%-20s %-20s %-20s %-20s" % ("Name", "IP", "Droplet ID", "Cloud Group"))
        for m in machines:
            try:
                do.Droplet.get_object(settings.DO_TOKEN, m.droplet_id)
                print(Fore.GREEN + "%-20s %-20s %-20s %-20s" % (m.name, m.ip, m.droplet_id, m.group))
            except do.baseapi.NotFoundError:
                print(Fore.RED + "%-20s %-20s %-20s %-20s" % (m.name, m.ip, m.droplet_id, m.group))
