import logging
import sys
import os
import asyncio
import aiomysql
import dns
import dns.zone
import signal

from pathlib import Path
from dotenv import load_dotenv

loop = asyncio.get_event_loop()

logger = logging.getLogger("pdnsbackup")

default_named = """zone "%s" {
   file "%sdb.%s";
   type master;
};"""

shutdown_task = None
 
def setup_logger(debug):
    loglevel = logging.DEBUG if debug else logging.INFO
    logfmt = '%(asctime)s %(levelname)s %(message)s'
    
    logger.setLevel(loglevel)
    logger.propagate = False
    
    lh = logging.StreamHandler(stream=sys.stdout )
    lh.setLevel(loglevel)
    lh.setFormatter(logging.Formatter(logfmt))    
    
    logger.addHandler(lh)

def setup_config(args):
    pass

async def backup(cfg):
    """backup"""
    conn = None
    cursor = None
    domains = []
    records = []
    zones_dns = []

    # first step, fetch all data
    logger.info("connecting to powerdns...")
    try:
        if cfg["gmysql_enable"]:
            logger.debug("fetching data with gmysql backend")
            conn = await aiomysql.connect( host=cfg['gmysql_host'], port=int(cfg['gmysql_port']),
                                            user=cfg['gmysql_user'], password=cfg['gmysql_password'], 
                                            db=cfg['gmysql_dbname'], loop=loop )
            logger.debug("succesfully connected to database")

            # fetch all domains
            cursor = await conn.cursor()
            await cursor.execute("SELECT id,name FROM domains;")
            rows = await cursor.fetchall()
            domains = list(rows)

            # fetch all records
            await cursor.execute("SELECT domain_id, name, type, content, ttl FROM records")
            rows = await cursor.fetchall()
            records = list(rows)

            logger.debug("%s domains and %s records retrieved..." % (len(domains),len(records)))
    except Exception as e:
        logger.error("fetcher - %s" % e)
    finally:
        if cursor is not None:
            await cursor.close()
        conn.close()
        logger.debug("database connection closed")

    # second step, convert data to dns.zone
    logger.debug("starting to convert records...")
    for zone_id, zone_name in domains:
        try:
            zone_dns = dns.zone.Zone(".")
            i = 0
            for domain_id, rr_name, rr_type, rr_data, rr_ttl in records:
                if domain_id == zone_id:
                    rrtype = dns.rdatatype.from_text(rr_type)
                    rr = zone_dns.get_rdataset(rr_name, rrtype, create=True)
                    rr.ttl = rr_ttl
                    rr.add(dns.rdata.from_text(dns.rdataclass.IN, rrtype, rr_data))
                i+=1
                zone_dns.to_text()
            zones_dns.append( (zone_name, zone_dns))
        except Exception as e:
            logger.error("convert - %s: %s" % (zone_name,e))

    # third step, export zones
    logger.info("%s zones to export..." % len(zones_dns))
    try:
        # export to file
        if cfg["file_enable"]:
            namedconf = []
            for zname, zdns in zones_dns:
                filename = f"{cfg['file_path_output']}/db.{zname}"
                with open(filename, "w") as zone_file:
                    zone_file.write(zdns.to_text(sorted  = True, relativize = False, want_origin = True))
                logger.debug(f">> file {filename} created")

                namedconf.append( default_named % (zname, cfg["file_path_bind"], zname) )

            with open(f"{cfg['file_path_output']}/named.conf", "w") as bind_file:
                bind_file.write( "\n\n".join(namedconf) )
            logger.info(f"bind configuration created")

    except Exception as e:
        logger.error("export - %s" % e)

def start_backup(cfg=None):
    debug = False

    # load env from file
    load_dotenv()

    appcfg = {}

    appcfg["web_listen_ip"] = "127.0.0.1"
    appcfg["web_listen_port"] = "8080"

    appcfg["gmysql_enable"] = True
    appcfg["gmysql_host"] = "127.0.0.1"
    appcfg["gmysql_port"] = "3306"
    appcfg["gmysql_ssl"] = False 
    appcfg["gmysql_dbname"] = "pdns"
    appcfg["gmysql_user"] = "pdns"
    appcfg["gmysql_password"] = "pdns"

    appcfg["file_enable"] = True 
    appcfg["file_path_bind"] = "/var/lib/powerdns/"
    appcfg["file_path_output"] = "/tmp/"

    if cfg is not None: appcfg=cfg

    # read environment variables
    debug_env = os.getenv('PDNSBACKUP_DEBUG')
    if debug_env is not None:
        debug = bool( int(debug_env) )

    # enable logger
    setup_logger(debug=debug)

    logger.debug("read env variables")

    gmysql_enable_env = os.getenv('PDNSBACKUP_GMYSQL_ENABLED')
    if gmysql_enable_env is not None:
        appcfg["gmysql_enable"] = int(gmysql_enable_env)

    appcfg["gmysql_host"] = os.getenv('PDNSBACKUP_GMYSQL_HOST')
    appcfg["gmysql_port"] = os.getenv('PDNSBACKUP_GMYSQL_PORT')

    gmysql_ssl_env = os.getenv('PDNSBACKUP_GMYSQL_SSL')
    if gmysql_ssl_env is not None:
        appcfg["gmysql_ssl"] = int(gmysql_ssl_env)

    appcfg["gmysql_dbname"] = os.getenv('PDNSBACKUP_GMYSQL_DBNAME')
    appcfg["gmysql_user"] = os.getenv('PDNSBACKUP_GMYSQL_USER')
    appcfg["gmysql_password"] = os.getenv('PDNSBACKUP_GMYSQL_PASSWORD')
    
    file_enable_env = os.getenv('PDNSBACKUP_FILE_ENABLED')
    if file_enable_env is not None:
        appcfg["file_enable"] = int(file_enable_env)
    appcfg["file_path_bind"] = os.getenv('PDNSBACKUP_FILE_PATH_BIND')
    appcfg["file_path_output"] = os.getenv('PDNSBACKUP_FILE_PATH_OUTPUT')

    try:
        asyncio.run(backup(appcfg))
    except KeyboardInterrupt:
        logger.debug("exit called")

    logger.info("terminated")