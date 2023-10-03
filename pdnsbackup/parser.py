import logging

logger = logging.getLogger("pdnsbackup")

def read(records: list):
    zones = {}

    z = 0
    for zone_name, rname, rtype, ttl, rdata, prio in records:
        # ignore empty record
        if rtype is None: continue
        
        if zone_name not in zones:
            z+=1
            stats_per_zone = { 
                               "records": 0, "wilcards": 0,
                               "rrtypes": { "a": 0, "aaaa": 0, "txt": 0, "ptr": 0, "cname": 0,  "srv": 0, "mx": 0, "others": 0},
                             } 
            zones[zone_name] = {"soa": "",  "ns": [], "records": [], "stats": stats_per_zone }
            logger.debug("parser - add zone (%s) %s" % (z,zone_name))

        # count record
        zones[zone_name]["stats"]["records"] +=1

        try:
            if rtype == "SOA":
                soa = rdata.split(" ")
                soa[0] = "%s." % soa[0]
                soa[1] = "%s." % soa[1]
                zones[zone_name]["soa"] = "%s. %s IN SOA %s" % (rname, ttl, " ".join(soa))
            elif rtype == "NS":
                zones[zone_name]["ns"].append("%s. %s IN NS %s." % (rname, ttl, rdata))
            elif rtype in ["CNAME", "PTR"]:
                zones[zone_name]["records"].append("%s. %s IN %s %s." % (rname, ttl, rtype, rdata))
            else:
                if rtype in [ "SRV", "MX" ]:
                    rdata = "%s %s." % (prio, rdata)
                zones[zone_name]["records"].append("%s. %s IN %s %s" % (rname, ttl, rtype, rdata))

            if rname.startswith("*."): zones[zone_name]["stats"]["wilcards"] +=1
            if rtype == "A": zones[zone_name]["stats"]["rrtypes"]["a"] +=1
            elif rtype == "AAAA": zones[zone_name]["stats"]["rrtypes"]["aaaa"] +=1
            elif rtype == "CNAME": zones[zone_name]["stats"]["rrtypes"]["cname"] +=1
            elif rtype == "PTR": zones[zone_name]["stats"]["rrtypes"]["ptr"] +=1
            elif rtype == "TXT": zones[zone_name]["stats"]["rrtypes"]["txt"] +=1
            elif rtype == "SRV": zones[zone_name]["stats"]["rrtypes"]["srv"] +=1
            elif rtype == "MX": zones[zone_name]["stats"]["rrtypes"]["mx"] +=1
            else: zones[zone_name]["stats"]["rrtypes"]["others"] +=1

        except Exception as e:
            logger.error("parser - add record %s %s in %s: %s" % (rname, rtype, zone_name, e))
    logger.info("parser - %s zone(s) detected" % z)
    return zones