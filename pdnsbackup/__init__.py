import logging
import sys
import os
import asyncio

from dotenv import load_dotenv

from pdnsbackup import backend
from pdnsbackup import parser
from pdnsbackup import export

loop = asyncio.get_event_loop()
logger = logging.getLogger("pdnsbackup")

def setup_logger(debug):
    loglevel = logging.DEBUG if debug else logging.INFO
    logfmt = '%(asctime)s %(levelname)s %(message)s'

    logger.setLevel(loglevel)
    logger.propagate = False

    lh = logging.StreamHandler(stream=sys.stdout )
    lh.setLevel(loglevel)
    lh.setFormatter(logging.Formatter(logfmt))

    logger.addHandler(lh)

def setup_config(cfg):
    pass

async def main(cfg):
    """backup processing"""
    records = await backend.fetch(cfg)
    zones = parser.read(records)
    export.backup(cfg, zones)

def backup(cfg=None):
    debug = False

    # load env from file
    load_dotenv()

    appcfg = {}

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
        asyncio.run(main(appcfg))
    except KeyboardInterrupt:
        logger.debug("exit called")

    logger.info("terminated")