from anouman.templates import (
    VagrantTemplate,
    VagrantBootstrapTemplate,
    CleanTemplate,
)

def build_vm(args):
    if not args.vm:
        raise Exception("build_vm must be callsed with args.mv=name")

    os.mkdir(args.vm)
    os.chdir(args.vm)
    # Write the Vagrantfile
    VagrantTemplate.save("Vagrantfile", context={
        'NAME':args.vm,
        'PUBLIC':True
    })

    # Write teh bootstrap file  
    VagrantBootstrapTemplate.save(path="./bootstrap.sh", context={
        'NGINX':True,
        'MYSQL':True,
    })

    # Write the clean file
    CleanTemplate.save(path="./clean.sh", context={'DOMAINNAME':'site3.com'})
    
    #subprocess.call(['vagrant', 'up'])
