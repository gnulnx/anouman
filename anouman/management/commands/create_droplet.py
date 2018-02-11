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

    def add_arguments(self, parser):
        parser.add_argument("--name", help="The name of the droplet")
        parser.add_argument("--region", help="The digitial ocean region", default="nyc3")
        parser.add_argument("--size_slug", help="The droplet size", default="512mb")
        parser.add_argument("--backups", help="Enable backups", type=bool, default=False)
        parser.add_argument("--image", help="The digital ocean image type", default="ubuntu-16-04-x64")
        parser.add_argument("--monitoring", help="Enable/Disable monitoring.", action="store_true")
        parser.add_argument("--private", help="Enable private networking", action="store_true")


    def create_droplet(self, options, **kwargs):
        if not options["name"]:
            print(Fore.RED + "--name is a required argument")
            sys.exit(1)

        keys = get_keys(settings.DO_TOKEN)
        if not keys:
            print(Fore.RED + "You need to setup ssh keys in your digital ocean account")
            sys.exit(1)

        print(Fore.GREEN + "CREATING DROPLET")

        # Create Droplet
        droplet = do.Droplet(
            token=settings.DO_TOKEN,
            name=kwargs.get('name', options["name"]),
            region=kwargs.get('region', options["region"]),  # New York 2
            image=kwargs.get('image', options["image"]),  # Ubuntu 16.04 x64
            size_slug=kwargs.get('size_slug', options["size_slug"]),
            ssh_keys=keys,
            backups=kwargs.get('backups', options["backups"]),
            monitoring=kwargs.get('monitoring', options["monitoring"]),
            private_networking=kwargs.get('private_networking', options["private"])
        )
        droplet.create()


        print(Fore.GREEN + " - New Droplet ID: %s" % droplet.id)
        print(Fore.GREEN + " - Waiting on droplet to come online")
        # Wait on Droplet to be created...needs to live in it's own method
        # You need to constrain this based on time so it doesn't run forever...
        MAXTIME = 45  # 45 seconds is the maximum time we wait  for machien to come up.
        start = time()
        while 1:
            actions = droplet.get_actions()
            try:
                for action in actions:
                    action.load()
                if action.status == 'completed':  # Once it shows complete, droplet is up and running
                    break
            except do.baseapi.DataReadError as e:
                pass

            elapsed = start - time()
            if elapsed > MAXTIME:
                print(FG.Red + "Droplet Creation Failed")
                sys.exit(1)
            sleep(1)

        manager = do.Manager(token=settings.DO_TOKEN)
        droplet = manager.get_droplet(droplet.id)

        machine = Machine(
            name=options["name"],
            droplet_id=droplet.id,
        )
        machine.save()

        cmd = '''ssh -o "StrictHostKeyChecking no" -A root@%s "echo ping -> pong"''' % droplet.ip_address
        start = time()
        while 1:
            try:
                subprocess.check_call([cmd], shell=True)
                break
            except subprocess.CalledProcessError:
                sleep(1)

            elapsed = start - time()
            if elapsed > MAXTIME:
                print(FG.Red + " - Unable to login to droplet with ssh keys")
                sys.exit(1)
        
        machine.ip=droplet.ip_address
        machine.private_ip=droplet.private_ip_address
        machine.save()
        print(Fore.GREEN + " - Your Droplet is Available at: %s" % machine.ip)

    
    def handle(self, *args, **options):
        self.create_droplet(options)
