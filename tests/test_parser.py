import unittest

from pdnsbackup import parser

records  =  [
                ('example.com', 'example.com', 'SOA', 3600, 'ns1.example.com admin.example.com 2023092901 3600 1800 604800 86400', 0), 
                ('example.com', 'example.com', 'NS', 3600, 'ns1.example.com', 0), 
                ('example.com', 'example.com', 'NS', 3600, 'ns2.example.com', 0), 
                ('example.com', 'zone.example.com', 'NS', 3600, 'ns3.example.com', 0), 
                ('example.com', 'zone.example.com', 'NS', 3600, 'ns4.example.com', 0), 
                ('example.com', 'ns1.example.com', 'A', 3600, '172.16.1.1', 0), 
                ('example.com', 'ns2.example.com', 'A', 3600, '172.16.1.2', 0), 
                ('example.com', '*.example.com', 'A', 14400, '0.0.0.0', 0), 
                ('example.com', 'example.com', 'MX', 14400, 'mail.example.com', 10), 
                ('example.com', 'example.com', 'TXT', 3600, '"v=spf1 a mx ip4:0.0.0.0 -all"', 0), 
                ('example.com', 'server.example.com', 'A', 3600, '127.0.0.7', 0), 
                ('example.com', 'mail.example.com', 'AAAA', 3600, '::1', 0),
                ('example.com', 'www.example.com', 'A', 300, '192.168.1.100', 0), 
                ('example.com', 'test.example.com', None, None, None, None),  # Adding empty non-terminals for non-DNSSEC zone 'example.com'
                ('example.com', '*.test.example.com', 'A', 3600, '192.168.1.200', 0), 
                ('example.com', 'rr.test.example.com', 'A', 3600, '192.168.1.201', 0), 
                ('example.com', 'rr.test.example.com', 'A', 3600, '192.168.1.202', 0), 
                ('example.com', 'ipv6.example.com', 'AAAA', 3600, '2001:0db8:85a3:0000:0000:8a2e:0370:7334', 0), 
                ('example.com', 'ftp.example.com', 'CNAME', 3600, 'www.example.com', 0), 
                ('example.com', 'example.com', 'TXT', 3600, '"Ceci est un enregistrement TXT" "Retour à la ligne"', 0), 
                ('example.com', '_service._tcp.example.com', 'SRV', 3600, '50 8080 server.example.com', 10),
                ('example.com', 'example.com', 'SPF', 3600, '"v=spf1 mx -all"', 0),
            ]

records_reverse =   [
                        ('0.10.in-addr.arpa', '0.10.in-addr.arpa', 'SOA', 3600, 'ns1.pdnsbackup.com dns.admin 96053 1800 300 1209600 300', 0), 
                        ('0.10.in-addr.arpa', '0.10.in-addr.arpa', 'NS', 3600, 'ns1.pdnsbackup.com', 0), 
                        ('0.10.in-addr.arpa', '0.10.in-addr.arpa', 'NS', 3600, 'ns2.pdnsbackup.com', 0), 
                        ('0.10.in-addr.arpa', '254.0.0.10.in-addr.arpa', 'PTR', 3600, 'dc1.example.fr', 0), 
                        ('0.10.in-addr.arpa', '1.0.0.10.in-addr.arpa', 'PTR', 3600, 'dc2.example.fr', 0), 
                        ('0.10.in-addr.arpa', '2.0.0.10.in-addr.arpa', 'PTR', 300, 'dc3.example.fr', 0),
                        ('0.10.in-addr.arpa', '0.0.10.in-addr.arpa', None, None, None, None),
                    ]

class TestParserRecords(unittest.TestCase):
    def test_soa(self):
        zones = parser.read(records)

        self.assertEqual( len(zones), 1)
        self.assertEqual( zones["example.com"]["soa"], "example.com. 3600 IN SOA ns1.example.com. admin.example.com. 2023092901 3600 1800 604800 86400")
    
    def test_ns(self):
        zones = parser.read(records)

        self.assertEqual( len(zones["example.com"]["ns"]), 4 )
        self.assertEqual( zones["example.com"]["ns"][0], "example.com. 3600 IN NS ns1.example.com." )

    def test_records_total(self):
        zones = parser.read(records)

        self.assertEqual( len(zones["example.com"]["records"]), 16 )

    def test_records_cname(self):
        zones = parser.read(records)

        self.assertEqual( zones["example.com"]["records"][12], "ftp.example.com. 3600 IN CNAME www.example.com." )

    def test_records_prio(self):
        zones = parser.read(records)

        self.assertEqual( zones["example.com"]["records"][3], "example.com. 14400 IN MX 10 mail.example.com." )
        self.assertEqual( zones["example.com"]["records"][14], "_service._tcp.example.com. 3600 IN SRV 10 50 8080 server.example.com." )

    def test_stats(self):
        zones = parser.read(records)

        self.assertEqual(zones["example.com"]["stats"]["records"], 18)
        self.assertEqual(zones["example.com"]["stats"]["rrtypes"]["a"], 8)
        self.assertEqual(zones["example.com"]["stats"]["rrtypes"]["aaaa"], 2)
        self.assertEqual(zones["example.com"]["stats"]["rrtypes"]["txt"], 2)
        self.assertEqual(zones["example.com"]["stats"]["rrtypes"]["ptr"], 0)
        self.assertEqual(zones["example.com"]["stats"]["rrtypes"]["cname"], 1)
        self.assertEqual(zones["example.com"]["stats"]["rrtypes"]["srv"], 1)
        self.assertEqual(zones["example.com"]["stats"]["rrtypes"]["mx"], 1)
        self.assertEqual(zones["example.com"]["stats"]["rrtypes"]["others"], 2)

        self.assertEqual(zones["example.com"]["stats"]["wilcards"], 2)
        self.assertEqual(zones["example.com"]["stats"]["delegations"], 2)

class TestParserReverse(unittest.TestCase):
    def test_records_ptr_total(self):
        zones = parser.read(records_reverse)

        self.assertEqual( len(zones["0.10.in-addr.arpa"]["records"]), 3 )

    def test_records_ptr(self):
        zones = parser.read(records_reverse)

        self.assertEqual( zones["0.10.in-addr.arpa"]["records"][0], "254.0.0.10.in-addr.arpa. 3600 IN PTR dc1.example.fr." )

    def test_stats(self):
        zones = parser.read(records_reverse)

        self.assertEqual(zones["0.10.in-addr.arpa"]["stats"]["records"], 3)
        self.assertEqual(zones["0.10.in-addr.arpa"]["stats"]["rrtypes"]["a"], 0)
        self.assertEqual(zones["0.10.in-addr.arpa"]["stats"]["rrtypes"]["ptr"], 3)