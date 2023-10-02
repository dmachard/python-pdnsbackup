import logging
import sys
import os
import asyncio
import pkgutil
import argparse
import yaml
import sys
import pathlib

from dotenv import load_dotenv

from pdnsbackup import backend
from pdnsbackup import parser
from pdnsbackup import export

loop = asyncio.get_event_loop()
logger = logging.getLogger("pdnsbackup")

def setup_cli():
    """setup command-line arguments"""
    options = argparse.ArgumentParser()          
    options.add_argument("-c", help="external config file")   
    options.add_argument('-v', action='store_true', help="debug mode")

    return options

def setup_logger(cfg):
    loglevel = logging.DEBUG if int(cfg["debug"]) else logging.INFO
    logfmt = '%(asctime)s %(levelname)s %(message)s'

    logger.setLevel(loglevel)
    logger.propagate = False

    lh = logging.StreamHandler(stream=sys.stdout )
    lh.setLevel(loglevel)
    lh.setFormatter(logging.Formatter(logfmt))

    logger.addHandler(lh)

def setup_config(args, ignore_env=False):
    cfg = {}
    
    # read default config
    try:
        conf = pkgutil.get_data(__package__, 'config.yml')
        cfg =  yaml.safe_load(conf) 
    except Exception as e:
        print("Default config invalid! %s" % e, sys.stderr)
        sys.exit(1)

    # overwrite config ?
    if args.v:
        cfg["debug"] = args.v
    # Overwrites then with the external file ?    
    if args.c: 
        try:
            with open(pathlib.Path(args.c), "r") as fd:
                cfg_ext =  yaml.safe_load(fd.read()) 
                cfg.update(cfg_ext)
        except Exception as e:
            print("External config invalid! %s" % e, sys.stderr)
            sys.exit(1)

    if ignore_env: return cfg
    
    # read config from environnement file ?
    load_dotenv()

    # then finally config from environment variables
    debug_env = os.getenv('PDNSBACKUP_DEBUG')
    if debug_env is not None:
        cfg["debug"] = bool( int(debug_env) )

    # gmysql backend env vars
    gmysql_enable_env = os.getenv('PDNSBACKUP_GMYSQL_ENABLED')
    if gmysql_enable_env is not None:
        cfg["gmysql-enabled"] = bool(int(gmysql_enable_env))

    cfg["gmysql-host"] = os.getenv('PDNSBACKUP_GMYSQL_HOST')
    cfg["gmysql-port"] = os.getenv('PDNSBACKUP_GMYSQL_PORT')

    gmysql_ssl_env = os.getenv('PDNSBACKUP_GMYSQL_SSL')
    if gmysql_ssl_env is not None:
        cfg["gmysql-ssl"] = bool(int(gmysql_ssl_env))

    cfg["gmysql-dbname"] = os.getenv('PDNSBACKUP_GMYSQL_DBNAME')
    cfg["gmysql-user"] = os.getenv('PDNSBACKUP_GMYSQL_USER')
    cfg["gmysql-password"] = os.getenv('PDNSBACKUP_GMYSQL_PASSWORD')

    # file output env vars
    file_enable_env = os.getenv('PDNSBACKUP_FILE_ENABLED')
    if file_enable_env is not None:
        cfg["file-enabled"] = bool(int(file_enable_env))
    cfg["file-path-bind"] = os.getenv('PDNSBACKUP_FILE_PATH_BIND')
    cfg["file-path-output"] = os.getenv('PDNSBACKUP_FILE_PATH_OUTPUT')

    # S3 output env vars
    s3_enable_env = os.getenv('PDNSBACKUP_S3_ENABLED')
    if s3_enable_env is not None:
        cfg["s3-enabled"] = bool(int(s3_enable_env))
    cfg["s3-access-key-id"] = os.getenv('PDNSBACKUP_S3_ACCESS_KEY_ID')
    cfg["s3-secret-access-key"] = os.getenv('PDNSBACKUP_S3_SECRET_ACCESS_KEY')
    s3_sslverify_env = os.getenv('PDNSBACKUP_S3_SSL_VERIFY')
    if  s3_sslverify_env is not None:
        cfg["s3-ssl-verify"] = bool(int(s3_sslverify_env))
    cfg["s3-endpoint-url"] = os.getenv('PDNSBACKUP_S3_ENDPOINT_URL')
    cfg["s3-bucket-name"] = os.getenv('PDNSBACKUP_S3_BUCKET_NAME')
    cfg["s3-region-name"] = os.getenv('PDNSBACKUP_S3_REGION_NAME')

    return cfg

async def main(cfg):
    """main backup processing"""
    records = await backend.fetch(cfg)
    zones = parser.read(records)
    success = export.backup(cfg, zones)
    if not success:
        logger.error("backup processing error")
    else:
        logger.info("backup processing terminated")

def run(config=None):
    # setup command-line arguments.
    options = setup_cli()
    args = options.parse_args()

    # setup config
    cfg = setup_config(args=args)

    # config from argument ?
    if config is not None: cfg=config

    # setup logger
    setup_logger(cfg=cfg)
    logger.debug("config OK, starting...")

    # everything is ok, start the app
    try:
        asyncio.run(main(cfg))
    except KeyboardInterrupt:
        logger.debug("exit called")
    logger.info("terminated")