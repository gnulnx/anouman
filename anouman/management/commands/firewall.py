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
from anouman.models import Machine, CloudGroup


class Command(BaseCommand):
    help = 'Create a digitial ocean droplet'
    def add_arguments(self, parser):
        parser.add_argument("--group", help="The name of the CloudGroup to apply firewall rules to")

    def handle(self, *args, **options):
        g = CloudGroup.objects.get(name=options["group"])
        g.get_context_data()
        g.provision()
