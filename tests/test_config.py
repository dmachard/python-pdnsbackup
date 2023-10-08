import unittest
import os

import pdnsbackup

class args:
    e = None
    c = None
    v = False

class TestConfig(unittest.TestCase):
    def test_default_config(self):
        """read default config"""
        cfg = pdnsbackup.setup_config(args=args(), ignore_env=True)

        self.assertFalse(cfg["debug"])

        self.assertTrue(cfg["gmysql-enabled"])
        self.assertTrue(cfg["file-enabled"])
        self.assertFalse(cfg["s3-enabled"])
        self.assertFalse(cfg["metrics-enabled"])

    def test_overwrite_config_env(self):
        """overwrite config with env variables"""
        os.environ['PDNSBACKUP_GMYSQL_ENABLED'] = "0"

        cfg = pdnsbackup.setup_config(args=args())
        os.environ.pop("PDNSBACKUP_GMYSQL_ENABLED")

        self.assertFalse(cfg["gmysql-enabled"])