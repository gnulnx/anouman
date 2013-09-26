import os
import unittest
import subprocess
import paramiko
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

class TestBuild(unittest.TestCase):

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


        # build anouman package        
        results = subprocess.check_output(['anouman', '--django-project', 'test/django/site1', '--domainname', 'site1.com'])
        print "###########################################################################################"
        print results
        print "############################################################################################"

        # Mv package to tmp directory
        subprocess.call(['mv', 'site1.com.tar.gz', 'tmp/'])
        os.chdir('tmp/')

    def test_6_check_package_contents(self):        
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

    """ This test needs to be server side """
    #def test_7_check_for_nginx_conf(self):
    #    """
    #        Will currently fail.  We need to save our nginx configure file here first
    #        And then link
    #    """
    #    # Check for site1.com/etc/nginx/sites-available/site1.com.conf
    #    self.assertTrue(
    #        os.path.isfile('site1.com/etc/nginx/sites-available/site1.com.conf')
    #    )
        



class TestVagrant(unittest.TestCase):

    def connect_to_s1(self):
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.connect(
            hostname='192.168.100.100',
            username='anouman',
            password='anouman',
            timeout=5
        )
       
        stdin, stdout, stderr = client.exec_command('hostname')
        return client    
           
    def exec_command(self, ssh, cmd):
        stdin, stdout, stderr = ssh.exec_command(cmd) 

        out=''
        for line in stdout:
            out = out + line
            
        return out

    def test_1_bring_vagrant_up(self):
        base_dir = os.path.dirname(__file__)
        os.chdir(os.path.join(base_dir, "test/vm/site1"))
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
            
        



        
