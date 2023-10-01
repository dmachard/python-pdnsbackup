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
        if cfg["file-enabled"]:
            namedconf = []
            for zname, zone in zones.items():
                filename = f"{cfg['file-path-output']}/db.{zname}"
                
                with open(filename, "w") as zf:
                    zf.write("$ORIGIN .\n%s\n" % zone["soa"])
                    zf.write("\n".join(zone["ns"])+"\n")
                    zf.write("\n".join(zone["records"])+"\n")

                logger.debug(f"export - >> file {filename} created")
                namedconf.append( default_named % (zname, cfg["file-path-bind"], zname) )

            with open(f"{cfg['file-path-output']}/named.conf", "w") as bind_file:
                bind_file.write( "\n\n".join(namedconf) +"\n" )
            logger.info(f"export - bind configuration created")

    except Exception as e:
        logger.error("export - %s" % e)
