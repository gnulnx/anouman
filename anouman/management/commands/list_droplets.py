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

        for m in machines:
            print(FG.Blue + "%-20s %-20s" % (m.name, m.ip))
