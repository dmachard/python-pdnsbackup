import unittest
import subprocess

class TestImport(unittest.TestCase):
    def test_import(self):
        cmd = ["python3", "-c", "import pdnsbackup; pdnsbackup.run();"]

        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as proc:
            output = proc.communicate()[0].decode("utf-8")
            self.assertIn("bind configuration created", output)