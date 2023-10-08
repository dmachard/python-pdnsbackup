import unittest
import os

import pdnsbackup
from pdnsbackup import export

class args:
    e = None
    c = None
    v = False

zone_direct = { 'example.com': {
                        'stats': { 
                               "records": 10, "wilcards": 2, "delegations": 0,
                               "rrtypes": { "a": 1, "aaaa": 0, "txt": 0, "ptr": 0, "cname": 0,  
                                            "srv": 0, "mx": 0, "ns": 2, "others": 4},
                             } 
                        }
        }

class TestExportMetrics(unittest.TestCase):
    def test_export_metrics(self):
        cfg = pdnsbackup.setup_config(args, ignore_env=True)
        cfg["file-enabled"] = False
        cfg["metrics-enabled"] = True

        success = export.backup(cfg, zone_direct)
        self.assertTrue(success)

        self.assertTrue(os.path.exists(cfg["metrics-prom-file"]))

