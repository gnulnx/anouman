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
    def add_arguments(self, parser):
        parser.add_argument("-n", "--name",  help="The name of the droplet", required=True)
        parser.add_argument("-d","--droplets", nargs="+", help="<Required> Set flag", required=True)

    def handle(self, *args, **options):
        print(options)
        g = CloudGroup.objects.get(name=options["name"])
        print(g)
        
        for machine in Machine.objects.filter(droplet_id__in=options["droplets"]):
            g.machines.add(machine)

        #Machine.objects.filter(droplet_id__in=options["droplets"]).update(
        #g.get_context_data()
        #g.provision()
