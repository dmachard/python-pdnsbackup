import unittest

from pdnsbackup import export

direct_zone = { 'example.com': {
                        'soa': 'example.com. 3600 IN SOA ns1.example.com. admin.example.com. 2023092901 3600 1800 604800 86400',
                        'ns': [ 'example.com. 3600 IN NS ns1.example.com.', 
                                'example.com. 3600 IN NS ns2.example.com.' ],
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

reverse_zone = { '0.10.in-addr.arpa':  {
                    'soa': '0.10.in-addr.arpa. 3600 IN SOA ns1.pdnsbackup.com. dns.admin. 96053 1800 300 1209600 300',
                    'ns': [ '0.10.in-addr.arpa. 3600 IN NS ns1.pdnsbackup.com.', 
                            '0.10.in-addr.arpa. 3600 IN NS ns2.pdnsbackup.com.' ],
                    'records': [ '254.0.0.10.in-addr.arpa. 3600 IN PTR dc1.example.fr.', 
                                 '1.0.0.10.in-addr.arpa. 3600 IN PTR dc2.example.fr.', 
                                 '2.0.0.10.in-addr.arpa. 300 IN PTR dc3.example.fr.']
                    }
                }