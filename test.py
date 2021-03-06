import os
import unittest
import time
import subprocess
import paramiko
import shutil
from anouman.templates import (
    vagrant,
    vagrant_bootstrap,
    clean
)

for line in open("setup.py"):
    if "VERSION" in line:
        try:
            VERSION = line.split("=")[1].strip().replace('"', '')
            break
        except:
            pass

try: VERSION
except Exception as e:
    raise Exception("VERSION NUMBER NOT FOUND")

VM1="10.0.1.21"

class TestBuild(unittest.TestCase):

    def setUp(self):
        """
            There were a lot of directory changes going on.
            It was easier to alway's return to a common root directory
        """
        # return to the rool level directory
        os.chdir(os.path.dirname(__file__))

    def test_1_remove_dist(self):
        """Make sure the build directory is gone"""
        subprocess.call(['rm', '-rf', 'dist'])
        self.assertFalse(
            os.path.isfile(
                'dist/anouman-%(version)s.tar.gz' % {'version':VERSION}
            )
        )
    
    def test_2_uninstall_anouman(self):
        subprocess.call(['pip', '-q', 'uninstall', 'anouman'])
        try:
            anouman = subprocess.check_output(['which', 'anouman'])
        except subprocess.CalledProcessError:
            anouman = False

        self.assertFalse(anouman)

    def test_3_sdist(self):
        subprocess.call(['python', 'setup.py', '--quiet', 'sdist'])
        self.assertTrue(
            os.path.isfile(
                'dist/anouman-%(version)s.tar.gz' % {'version':VERSION}
            )
        )

        
    def test_4_install_anouman(self):
        subprocess.call(['pip', 'install', 'dist/anouman-%(version)s.tar.gz' % {'version':VERSION}, '--upgrade'])    
        try:
            anouman = subprocess.check_output(['which', 'anouman'])
        except subprocess.CalledProcessError:
            anouman = False

        self.assertTrue(anouman)


    def test_5_create_anouman_package(self):
        # Pre test cleanup
        subprocess.call(['rm', '-rf', 'tmp/*'])
        subprocess.call(['rm', '-rf', 'site1.com.tar.gz'])

        #create empty virtualenv
        subprocess.call(['virtualenv', 'site1'])
        os.system("source site1/bin/activate")
        
        # build anouman package        
        results = subprocess.check_output(['anouman', '--django-project', 'test/django/site1', '--domainname', 'site1.com'])

        # Mv package to tmp directory
        subprocess.call(['mv', 'site1.com.tar.gz', 'tmp/'])
        self.assertTrue(True)
        # clean up and remove this virtualenv

    def test_6_check_package_contents(self):        
        os.chdir('tmp/')
        # unpack the package and check basic directory structure.
        subprocess.call(['tar', 'xvfz', 'site1.com.tar.gz']) 
        dir_contents = os.listdir("site1.com")
        self.assertEqual(
            ['pip_packages.txt', 'src'], 
            dir_contents
        )

        self.assertTrue(
            os.path.isfile("site1.com/src/manage.py")
        )

        self.assertTrue(
            os.path.isfile("site1.com/src/site1/settings.py")
        )
        
        self.assertTrue(
            os.path.isfile("site1.com/src/site1/wsgi.py")
        )



class TestVagrant(unittest.TestCase):
    
    def setUp(self):
        """
            There were a lot of directory changes going on.
            It was easier to alway's return to a common root directory
        """
        # return to the rool level directory
        try:
            os.chdir(os.path.dirname(__file__))
        except:
            os.chdir("/Users/jfurr/anouman/")


    def connect_to_s1(self, transport=False):
        """
            return a connection to server "s1"
            This is a vagrant box. that expects to have already
            had provisioning from bootstrap.sh done on it.
        """
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.connect(
            hostname=VM1,
            username='anouman',
            password='anouman',
            timeout=5
        )
       
        stdin, stdout, stderr = client.exec_command('hostname')
        return client    
          
    def scp(self, remotepath, localpath):
        """
            scp a file to remote server s1.  
        """
        #TODO: Remove the hard coded scp call.  In fact why not move this
        # out of the test suite and make it a general purpose call.
        transport = paramiko.Transport((VM1, 22))
        transport.connect(
            username='anouman', 
            password='anouman'
        )

        sftp = paramiko.SFTPClient.from_transport(transport)
        try:
            sftp.put(remotepath, localpath)
        except Exception as e:
            print os.listdir("./")
            raise Exception("YOU FAIL: ", e)
        sftp.close()
        transport.close()

    def exec_s1(self, cmd):
        ssh = self.connect_to_s1()
        return self.exec_command(ssh, cmd) 

    def exec_command(self, ssh, cmd):
        stdin, stdout, stderr = ssh.exec_command(cmd) 

        out=''
        for line in stdout:
            out = out + line
            
        return out
    
    def test_1_create_new_vagrant_box(self):
        print "test_1_create_new_vagrant_box"
        try:
            shutil.rmtree("test/vm/site3")
            print "REMOVED"
        except OSError as e:
            print "EXCEPTION: ", e
            pass

        os.mkdir("test/vm/site3")
        os.chdir("test/vm/site3")
        
        vagrant.save(path="./Vagrantfile", context={
            'NAME':'site3',
            'PUBLIC':True
        })
        
        vagrant_bootstrap.save(path="./bootstrap.sh", context={
            'NGINX':True,
            'MYSQL':True,
        })

        clean.save(path="./clean.sh", context={
            'DOMAINNAME':'site3.com'
        })

        print "YOU NEED TO ACTUALLY CHECK SOMETHIGN FOR THIS TO BE  ATEST"

    def test_2_bring_vagrant_up(self):
        base_dir = os.path.dirname(__file__)
        os.chdir(os.path.join(base_dir, "test/vm/site1"))

        """
            Frist we try to connect to see if the vm is already up.
            If that fails we then call vagrant up and try to connect
            again after that finishes. 
        """
        try:
            ssh = self.connect_to_s1()
        except Exception as e:
            print "\nCONNECTION FAILED.  \nTrying to bring vagrant up...."
            subprocess.call(['vagrant', 'up'])
            print "Now retrying ssh connect"
            ssh = self.connect_to_s1()

        stdout = self.exec_command(ssh, 'hostname')
        if 'precise64' not in stdout:
            self.assertFalse("Incorrect hostname....so no this test fails")
           
    def test_3_clean_server(self):
        out = self.exec_s1("/usr/bin/yes | sh /vagrant/clean.sh")  

        # Confirm that the home directory has been cleaned out
        out = self.exec_s1("cd /home/anouman; ls")
        self.assertEqual(out.strip(), '')
        
        # Make sure anouman has been uninstalled
        out = self.exec_s1("anouman") 
        self.assertEqual(out, '') 

        # TODO There are probably several other checks could do here

    def test_4_scp_anouman_to_s1(self):
        # copy anouman to server
        self.scp(
            "dist/anouman-%(version)s.tar.gz" % {'version':VERSION}, 
            "/home/anouman/anouman-0.0.4.0.tar.gz"
        )

        out = self.exec_s1("cd /home/anouman; ls")
        self.assertEqual(
            "anouman-%(version)s.tar.gz" % {'version':VERSION},
            out.strip()
        )

       
    def test_5_install_anouman_with_pip(self):  
        out = self.exec_s1("sudo pip install /home/anouman/anouman-%(version)s.tar.gz --upgrade" % {'version':VERSION})

        # Check that anouman is installed
        out = self.exec_s1("anouman") 
        self.assertEqual(out.strip(), "anouman") 

    def test_6_scp_package_to_s1(self):

        self.scp(
            "tmp/site1.com.tar.gz",
            "/home/anouman/site1.com.tar.gz"
        )

        out = self.exec_s1("cd /home/anouman; ls")
        self.assertEqual(
            "anouman-%(version)s.tar.gz\nsite1.com.tar.gz" % {'version':VERSION},
            out.strip()
        )

    def test_7_install_site1(self):
        print "cd /home/anouman; /usr/bin/yes | anouman --deploy site1.com.tar.gz"
        out = self.exec_s1("cd /home/anouman; /usr/bin/yes | anouman --deploy site1.com.tar.gz")
    
        print "out: ", out
