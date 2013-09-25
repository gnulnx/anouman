import random
import unittest

from django.conf import settings
settings.configure()

from anouman.templates import commands

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.seq = range(10)

    def test_shell_cmd_template(self):
        from test_expected_results import shell_commands_expected
        context = {
            'DOMAINNAME':'example.com',
        }
        
        out = commands.render(context) 
        self.assertTrue(out == shell_commands_expected)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSequenceFunctions)
    unittest.TextTestRunner(verbosity=2).run(suite)
