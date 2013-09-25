from version import VERSION
import os
import unittest
import subprocess

class TestBuild(unittest.TestCase):

    def setUp(self):
        """Make sure the build directory is gone"""
        subprocess.call(['rm', '-rf', 'dist'])
        self.assertFalse(
            os.path.isfile(
                'dist/anouman-%(version)s.tar.gz' % {'version':VERSION}
            )
        )
    

    def test_sdist(self):
        subprocess.call(['python', 'setup.py', 'sdist'])
        self.assertTrue(
            os.path.isfile(
                'dist/anouman-%(version)s.tar.gz' % {'version':VERSION}
            )
        )

    
