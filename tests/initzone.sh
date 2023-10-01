#!/bin/bash

sudo docker exec powerdns pdnsutil load-zone example.com /var/lib/powerdns/db.example.com
sudo docker exec powerdns pdnsutil load-zone 0.10.in-addr.arpa /var/lib/powerdns/db.0.10.in-addr.arpa