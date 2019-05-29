import unittest
from ssmcommander.yaml_parser import InputFile
import os

from moto import mock_kms


class MyTestCase(unittest.TestCase):
    @mock_kms
    def test_bad_kms_block(self):
        # mocked kms decrypt is just double base64'ed
        input = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_badkms.yml")
        file = InputFile(input)
        self.assertIsNotNone(input)
        self.assertEqual(file.raw_data['section_bad_kms_value']['password'], "boblawblob")

    def test_can_read(self):
        input = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.yml")
        self.assertIsNotNone(input)


if __name__ == '__main__':
    unittest.main()
