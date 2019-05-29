import unittest
from ssmcommander.yaml_parser import InputFile
import click.exceptions
import os

from moto import mock_kms



class MyTestCase(unittest.TestCase):
    @mock_kms
    def test_bad_kms_block(self):
        with self.assertRaises(click.exceptions.BadParameter):
            input = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_badkms.yml")
            file = InputFile(input)

    def test_can_read(self):
        input = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.yml")
        self.assertIsNotNone(input)


if __name__ == '__main__':
    unittest.main()
