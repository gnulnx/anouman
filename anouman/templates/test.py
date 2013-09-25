import random
import unittest

from django.conf import settings
settings.configure()

#from anouman.templates.init_script import gunicorn_upstart
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

    def test_choice(self):
        element = random.choice(self.seq)
        self.assertTrue(element in self.seq)

    def test_sample(self):
        with self.assertRaises(ValueError):
            random.sample(self.seq, 20)
        for element in random.sample(self.seq, 5):
            self.assertTrue(element in self.seq)

if __name__ == '__main__':
    #unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSequenceFunctions)
    unittest.TextTestRunner(verbosity=2).run(suite)
