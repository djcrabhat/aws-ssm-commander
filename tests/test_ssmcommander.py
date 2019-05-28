import unittest
from ssmcommander.yaml_parser import InputFile
import click.exceptions

class MyTestCase(unittest.TestCase):
    def test_bad_kms_block(self):
        # TODO: real tests
        with self.assertRaises(click.exceptions.BadParameter):
            file = InputFile("test_badkms.yml")

    def test_can_read(self):
        file = InputFile("test.yml")
        self.assertIsNotNone(file)



if __name__ == '__main__':
    unittest.main()
