import unittest
import os

import pdnsbackup
from pdnsbackup import export

zone_direct = { 'example.com': {
                        'soa': 'example.com. 3600 IN SOA ns1.example.com. admin.example.com. 2023092901 3600 1800 604800 86400',
                        'ns': [ 'example.com. 3600 IN NS ns1.example.com.', 
                                'example.com. 3600 IN NS ns2.example.com.',
                                'zone.example.com. 3600 IN NS ns3.example.com.',
                                'zone.example.com. 3600 IN NS ns4.example.com.'  ],
                        'records': [ 'ns1.example.com. 3600 IN A 172.16.1.1',
                                     'ns2.example.com. 3600 IN A 172.16.1.2',
                                     '*.example.com. 14400 IN A 0.0.0.0',
                                     'example.com. 14400 IN MX 10 mail.example.com.',
                                     'example.com. 3600 IN TXT "v=spf1 a mx ip4:0.0.0.0 -all"',
                                     'server.example.com. 3600 IN A 127.0.0.7',
                                     'mail.example.com. 3600 IN AAAA ::1',
                                     'www.example.com. 300 IN A 192.168.1.100',
                                     '*.test.example.com. 3600 IN A 192.168.1.200',
                                     'rr.test.example.com. 3600 IN A 192.168.1.201',
                                     'rr.test.example.com. 3600 IN A 192.168.1.202',
                                     'ipv6.example.com. 3600 IN AAAA 2001:0db8:85a3:0000:0000:8a2e:0370:7334',
                                     'ftp.example.com. 3600 IN CNAME www.example.com.',
                                     'example.com. 3600 IN TXT "Ceci est un enregistrement TXT" "Retour à la ligne"',
                                     '_service._tcp.example.com. 3600 IN SRV 10 50 8080 server.example.com.',
                                     '100.example.com. 3600 IN PTR www.example.com.',
                                     'example.com. 3600 IN SPF "v=spf1 mx -all"' ]
                        }
        }
zone_reverse = { '0.10.in-addr.arpa':  {
                    'soa': '0.10.in-addr.arpa. 3600 IN SOA ns1.pdnsbackup.com. dns.admin. 96053 1800 300 1209600 300',
                    'ns': [ '0.10.in-addr.arpa. 3600 IN NS ns1.pdnsbackup.com.', 
                            '0.10.in-addr.arpa. 3600 IN NS ns2.pdnsbackup.com.' ],
                    'records': [ '254.0.0.10.in-addr.arpa. 3600 IN PTR dc1.example.fr.', 
                                 '1.0.0.10.in-addr.arpa. 3600 IN PTR dc2.example.fr.', 
                                 '2.0.0.10.in-addr.arpa. 300 IN PTR dc3.example.fr.']
                    }
                }

REF_ZONE_EXAMPLE = ""
REF_ZONE_REVERSE = ""
REF_NAMED = ""

class args:
    e = None
    c = None
    v = False

with open(os.path.join(os.path.dirname(__file__), 'db.example.com'), "r") as ref:
    REF_ZONE_EXAMPLE = ref.read()

with open(os.path.join(os.path.dirname(__file__), 'db.0.10.in-addr.arpa'), "r") as ref:
    REF_ZONE_REVERSE = ref.read()

with open(os.path.join(os.path.dirname(__file__), 'named.conf'), "r") as ref:
    REF_CONF_NAMED = ref.read()

class TestExportFile(unittest.TestCase):
    def test_export_zone_direct(self):
        self.maxDiff = None

        cfg = pdnsbackup.setup_config(args, ignore_env=True)
        success = export.backup(cfg, zone_direct)
        self.assertTrue(success)

        for zone, data in zone_direct.items():
            with open("%s/db.%s" % (cfg["file-path-output"],zone), "r") as f:
                self.assertEqual( f.read(), REF_ZONE_EXAMPLE )
                
    def test_export_zone_reverse(self):
        self.maxDiff = None

        cfg = pdnsbackup.setup_config(args, ignore_env=True)
        success = export.backup(cfg, zone_reverse)
        self.assertTrue(success)

        for zone, data in zone_reverse.items():
            with open("%s/db.%s" % (cfg["file-path-output"],zone), "r") as f:
                self.assertEqual( f.read(), REF_ZONE_REVERSE )

    def test_export_named(self):
        self.maxDiff = None

        cfg = pdnsbackup.setup_config(args, ignore_env=True)
        success = export.backup(cfg, zone_direct)
        self.assertTrue(success)

        for zone, data in zone_direct.items():
            with open("%s/named.conf" % cfg["file-path-output"], "r") as f:
                self.assertEqual( f.read(), REF_CONF_NAMED )