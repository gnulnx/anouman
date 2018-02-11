from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import digitalocean as do


class Command(BaseCommand):
    help = 'Manage your infrastructure'

    def add_arguments(self, parser):
        parser.add_argument('--create', help="create a new digitial ocean droplet", type=bool)
        parser.add_argument('--name', help="The name of the droplet")
        parser.add_argument('--region', help="The digitial ocean region")
        parser.add_argument('--size_slug', help="The droplet size")
        parser.add_argument('--backups', help="Enable backups", type=bool, default=False)
        parser.add_argument('--monitoring', help="Enable/Disable monitoring.", type=bool, default=False)
        parser.add_argument('--private', help="Enable private networking", type=bool, default=False)


    def get_keys(self):
        for tries in range(11):
            try:
                manager = do.Manager(token=settings.DO_TOKEN)
                return manager.get_all_sshkeys()
            except do.baseapi.DataReadError:
                if tries > 10: raise
                else: pass

    def create_droplet(self, **kwargs):
        print("CREATING DROPLET")
        # Create Keys
        keys = self.get_keys()
        print("keys: ", keys)

        # Create Droplet
        """
        droplet = do.Droplet(
            token=TOKEN,
            name=kwargs.get('name', 'qa.teaquinox.com'),
            region=kwargs.get('region', 'nyc2'),  # New York 2
            image=kwargs.get('image', 'ubuntu-16-04-x64'),  # Ubuntu 16.04 x64
            size_slug=kwargs.get('size_slug', '512mb'),   # 512MB
            ssh_keys=keys,
            backups=kwargs.get('backups', False),
            monitoring=kwargs.get('monitoring', True),
            private_networking=kwargs.get('private_networking', False)
        )
        droplet.create()
        """
    
    def handle(self, *args, **options):
        print(options)
        self.create_droplet()
