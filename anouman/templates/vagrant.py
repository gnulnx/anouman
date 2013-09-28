#!/usr/bin/env python
import os
from django.template import Template, Context
from django.conf import settings

## When you initially did this you were only using django templates
## and this was not a full django project.  You can only call this
## once so you put in a few files to make sure it was called...
try: settings.configure()
except: pass

"""
    Render the Vagrantfile used to start up vagrant
    It default to a public network environemnt.
    To set up a private network simple pass
    PRIVATE:'192.168.100.100' to the context
"""

context = {
    'NAME':'site1',
    'PRIVATE':False, #To use private network set to ip:  192.168.100.100
}

templ="""# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config| 
  # Every Vagrant virtual environment requires a box to build off of. 
  config.vm.box = "{{NAME}}" 

  # The url from where the 'config.vm.box' box will be fetched if it 
  # doesn't already exist on the user's system. 
  config.vm.box_url = "http://files.vagrantup.com/precise64.box" 

  # Run bootstrap.sh provisioning script 
  config.vm.provision :shell, :path => "bootstrap.sh" 
  {% if PRIVATE %}
  # Create a private network, which allows host-only access to the machine 
  # using a specific IP. 
  # config.vm.network :private_network, ip: "{{PRIVATE}}"  
  {% else %}
  # Create a public network, which will make the machine appear as another 
  #physical device on your network. 
  config.vm.network :public_network 
  {% endif %}
  #config.vm.provider :virtualbox do |vb| 
  # # Don't boot with headless mode 
  #  vb.gui = true 
  # 
  #  # Use VBoxManage to customize the VM. For example to change memory: 
  #  vb.customize ["modifyvm", :id, "--memory", "1024"] 
  #end 
end"""

def render(c={}):
    """
        Pass in a context our the defaults above will be used
    """
    context.update(c)

    t = Template( templ )
    c = Context( context )
    return t.render( c )

def save(path="./Vagrantfile", **kwargs):
    c = kwargs.get('context', context)
    with open(path, 'w') as f:
        f.write(render(c) )


if __name__ == '__main__':
    pass
