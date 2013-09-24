import random
import unittest

from django.conf import settings
settings.configure()

#from anouman.templates.init_script import gunicorn_upstart
from commands import commands

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.seq = range(10)

    def test_shell_cmd_template(self):
        from test_expected_results import shell_commands_expected
        context = {
            'DOMAINNAME':'example.com',
        }
        
        print shell_commands_expected
        out = commands.get_commands(context) 
        self.assertTrue(out == shell_commands_expected)

    def test_choice(self):
        element = random.choice(self.seq)
        self.assertTrue(element in self.seq)

    def test_sample(self):
        with self.assertRaises(ValueError):
            random.sample(self.seq, 20)
        for element in random.sample(self.seq, 5):
            self.assertTrue(element in self.seq)

if __name__ == '__main__':
    unittest.main()
