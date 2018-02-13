import sys
import subprocess
from time import time, sleep
import digitalocean as do
from colorama import init
from colorama import Fore, Back, Style
init()

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from anouman.models import Machine
from anouman.utils import get_keys

class Command(BaseCommand):
    help = 'Create a digitial ocean droplet'

    def add_arguments(self, parser):
        parser.add_argument("-d","--droplets", nargs="+", help="<Required> Set flag", required=True)
        #parser.add_argument("--droplet-id", help="The droplet id")
        parser.add_argument("--clean",
            help="Remove machines from local database if there isn't an instance at Digitial Ocean")

    def handle(self, *args, **options):
        m = do.Manager(token=settings.DO_TOKEN)

        for _id in options["droplets"]:
            try:
                droplet = m.get_droplet(_id)
                droplet.destroy()
                print(Fore.GREEN + " - Droplet %s has been destroyed" % _id)
            except do.baseapi.NotFoundError:
                print(Fore.RED + " - Droplet %s not found on digitial ocean" % _id)


            # First check that we have a matching Machine in the local database
            machine = None
            try:
                machine = Machine.objects.get(droplet_id=_id)
                machine.delete()
                print(Fore.GREEN + " - Machine delete from local database")
            except Machine.DoesNotExist:
                print(Fore.RED + " - There is no Local Machine with droplets=%s" % _id)
                sys.exit(1)
