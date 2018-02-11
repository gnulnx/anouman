import digitalocean as do
from django.conf import settings

def get_keys(self):
    for tries in range(11):
        try:
            manager = do.Manager(token=settings.DO_TOKEN)
            return manager.get_all_sshkeys()
        except do.baseapi.DataReadError:
            if tries > 10: raise
            else: pass
