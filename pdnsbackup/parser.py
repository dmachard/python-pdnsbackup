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
                               "records": 0, "wilcards": 0, "delegations": 0,
                               "rrtypes": { "a": 0, "aaaa": 0, "txt": 0, "ptr": 0, "cname": 0,  
                                            "srv": 0, "mx": 0, "ns": 0, "others": 0},
                             } 
            zones[zone_name] = {"soa": "",  "ns": [], "records": [], "stats": stats_per_zone }
            logger.debug("parser - add zone (%s) %s" % (z,zone_name))

        try:
            # convert to bind style
            match rtype:
                case "SOA":
                    soa = rdata.split(" ")
                    soa[0] = "%s." % soa[0]
                    soa[1] = "%s." % soa[1]
                    zones[zone_name]["soa"] = "%s. %s IN SOA %s" % (rname, ttl, " ".join(soa))
                case "NS":
                    zones[zone_name]["ns"].append("%s. %s IN NS %s." % (rname, ttl, rdata))
                case "CNAME" | "PTR":
                    zones[zone_name]["records"].append("%s. %s IN %s %s." % (rname, ttl, rtype, rdata))
                case _:
                    if rtype in [ "SRV", "MX" ]:
                        rdata = "%s %s." % (prio, rdata)
                    zones[zone_name]["records"].append("%s. %s IN %s %s" % (rname, ttl, rtype, rdata))

            # compute stats
            if rtype not in [ "SOA", "NS"]: 
                zones[zone_name]["stats"]["records"] +=1

            if rtype == "NS" and rname != zone_name:
                zones[zone_name]["stats"]["records"] +=1
                zones[zone_name]["stats"]["delegations"] +=1

            if rname.startswith("*."): zones[zone_name]["stats"]["wilcards"] +=1

            match rtype:
                case "A": zones[zone_name]["stats"]["rrtypes"]["a"] +=1
                case"AAAA": zones[zone_name]["stats"]["rrtypes"]["aaaa"] +=1
                case "CNAME": zones[zone_name]["stats"]["rrtypes"]["cname"] +=1
                case "PTR": zones[zone_name]["stats"]["rrtypes"]["ptr"] +=1
                case "TXT": zones[zone_name]["stats"]["rrtypes"]["txt"] +=1
                case "SRV": zones[zone_name]["stats"]["rrtypes"]["srv"] +=1
                case "MX": zones[zone_name]["stats"]["rrtypes"]["mx"] +=1
                case "NS": zones[zone_name]["stats"]["rrtypes"]["ns"] +=1
                case _: zones[zone_name]["stats"]["rrtypes"]["others"] +=1

        except Exception as e:
            logger.error("parser - add record %s %s in %s: %s" % (rname, rtype, zone_name, e))
    logger.info("parser - %s zone(s) detected" % z)
    return zones