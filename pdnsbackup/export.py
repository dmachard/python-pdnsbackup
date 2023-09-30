import logging

logger = logging.getLogger("pdnsbackup")


default_named = """zone "%s" {
   file "%sdb.%s";
   type master;
};"""

def backup(cfg: dict, zones: dict):
    logger.info("export - %s zones to export..." % len(zones))
    try:
        # export to file
        if cfg["file_enable"]:
            namedconf = []
            for zname, zone in zones.items():
                filename = f"{cfg['file_path_output']}/db.{zname}"
                
                with open(filename, "w") as zone_file:
                    zone_file.write("$ORIGIN .\n%s\n" % zone["soa"])
                    zone_file.write("\n".join(zone["ns"])+"\n")
                    zone_file.write("\n".join(zone["records"])+"\n")

                logger.debug(f"export - >> file {filename} created")
                namedconf.append( default_named % (zname, cfg["file_path_bind"], zname) )

            with open(f"{cfg['file_path_output']}/named.conf", "w") as bind_file:
                bind_file.write( "\n\n".join(namedconf) )
            logger.info(f"export - bind configuration created")

    except Exception as e:
        logger.error("export - %s" % e)
