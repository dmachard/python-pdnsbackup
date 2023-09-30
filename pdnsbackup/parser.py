import logging

logger = logging.getLogger("pdnsbackup")

def read(records: list):
    z = 0
    zones = {}
    for zone_name, rname, rtype, ttl, rdata, prio in records:
        if rtype is None: continue
        if zone_name not in zones:
            z+=1
            zones[zone_name] = {"soa": "",  "ns": [], "records": [] }
            logger.debug("parser - add zone (%s) %s" % (z,zone_name))

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
        except Exception as e:
            logger.error("parser - add record %s %s in %s: %s" % (rname, rtype, zone_name, e))
    logger.info("parser - %s zone(s) detected" % z)
    return zones