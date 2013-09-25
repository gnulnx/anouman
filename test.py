import os
import unittest
import subprocess

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
    

    def test_2_sdist(self):
        subprocess.call(['python', 'setup.py', '--quiet', 'sdist'])
        self.assertTrue(
            os.path.isfile(
                'dist/anouman-%(version)s.tar.gz' % {'version':VERSION}
            )
        )


    def test_3_uninstall_anouman(self):
        subprocess.call(['pip', '-q', 'uninstall', 'anouman'])
        try:
            anouman = subprocess.check_output(['which', 'anouman'])
        except subprocess.CalledProcessError:
            anouman = False

        self.assertFalse(anouman)

        
    def test_4_install_anouman(self):
        subprocess.call(['pip', 'install', 'dist/anouman-%(version)s.tar.gz' % {'version':VERSION}, '--upgrade'])    
        try:
            anouman = subprocess.check_output(['which', 'anouman'])
        except subprocess.CalledProcessError:
            anouman = False

        self.assertTrue(anouman)


    def test_5_build_package(self):
        subprocess.call(['anouman', '--django-project', '/test/site1.tar.gz



