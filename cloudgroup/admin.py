# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from cloudgroup.models import SSHKey, IPAddress, Machine, CloudGroup


class SSHKeyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    pass
admin.site.register(SSHKey, SSHKeyAdmin)


class SSHKeysInline(admin.TabularInline):
    model = SSHKey

class IPAddressAdmin(admin.ModelAdmin):
    list_display = ('ip',)
    pass
admin.site.register(IPAddress, IPAddressAdmin)


class MachineAdmin(admin.ModelAdmin):
    list_display = ('name', 'droplet_id', 'ip', 'private_ip',)
    pass
admin.site.register(Machine, MachineAdmin)


class CloudGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    pass
admin.site.register(CloudGroup, CloudGroupAdmin)

