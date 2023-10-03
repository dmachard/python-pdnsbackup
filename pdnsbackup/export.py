import logging
import tarfile
import io
import tempfile
import boto3
import pathlib
import os
import prometheus_client
import datetime

logger = logging.getLogger("pdnsbackup")

STATE_SUCCESS   =   True
STATE_ERROR     =   False

default_named = """zone "%s" {
   file "%sdb.%s";
   type master;
};"""

def create_zone(zone):
    data = [ "$ORIGIN .\n%s" % zone["soa"] ]
    data.append("\n".join(zone["ns"]))
    data.append("\n".join(zone["records"]))
    return "\n".join(data)+"\n\n"

def create_named(conf):
    return "\n\n".join(conf) +"\n\n"

def export_file(cfg: dict, zones: dict):
    logger.debug("backup to file is enabled")
    namedconf = []

    # check if the output folder exists ? add it if missing
    if not os.path.exists(f"{cfg['file-path-output']}"):
        os.makedirs(f"{cfg['file-path-output']}")
        logger.debug(f"export file - directory %s created!" % cfg['file-path-output'])

    try:
        # cleanup the folder 
        [f.unlink() for f in pathlib.Path(f"{cfg['file-path-output']}").glob("*") if f.is_file()] 

        # iter over all zones
        for name, zone in zones.items():
            filename = f"{cfg['file-path-output']}/db.{name}"
            
            with open(filename, "w") as zf:
                zf.write(create_zone(zone))

            logger.debug(f"export file - add {filename}")
            namedconf.append( default_named % (name, cfg["file-path-bind"], name) )

        with open(f"{cfg['file-path-output']}/named.conf", "w") as bind_file:
            bind_file.write( create_named(namedconf) )

        logger.info(f"export file - success")
    except Exception as e:
        logger.error("export file - %s" % e)
        return False
    
    return True

def export_s3(cfg: dict, zones: dict):
    logger.debug("backup to s3 (%s) is enabled" % cfg["s3-endpoint-url"])

    # create temp tar.gz file of all zones
    with tempfile.TemporaryDirectory() as dir:
        filetar = "pdnsbackup-zones.tar.gz"
        temptar = f"{dir}/{filetar}"
        logger.debug("export s3 - create temp tar gz %s" % temptar)
        try:
            with tarfile.open(temptar, "w:gz") as tar:
                namedconf = []
                for name, zone in zones.items():
                    data = create_zone(zone).encode()

                    tarinfo = tarfile.TarInfo(f'db.{name}')
                    tarinfo.size = len(data)
                    tar.addfile(tarinfo, io.BytesIO(data))

                    namedconf.append( default_named % (name, cfg["file-path-bind"], name) )

                data = create_named(namedconf)
                data = data.encode()
                tarinfo = tarfile.TarInfo(f'named.conf')
                tarinfo.size = len(data)
                tar.addfile(tarinfo, io.BytesIO(data))
            logger.debug("export s3 - tar gz succesfully created" )
        except Exception as e:
            logger.error("export s3 compress - %s" % e)
            return False
        
        # upload tar.gz to S3
        logger.debug("export s3 - uploading tar file..." )
        try:
            s3 = boto3.resource('s3', 
                                endpoint_url=cfg['s3-endpoint-url'], 
                                aws_access_key_id=cfg['s3-access-key-id'], 
                                aws_secret_access_key=cfg['s3-secret-access-key'],
                                verify=cfg['s3-ssl-verify'],
                                region_name=cfg['s3-region-name'],
                            )
            s3.Bucket(cfg['s3-bucket-name']).upload_file(temptar, f'{filetar}')

            logger.info("export s3 - success" )
        except Exception as e:
            logger.error("export s3 upload - %s" % e)
            return False
    
    return True

def export_metrics(cfg: dict, zones: dict, status: bool):
    logger.debug("open metrics are enabled")

    registry = prometheus_client.CollectorRegistry()

    metric_status = prometheus_client.Gauge(
                            'pdnsbackup_status', 
                            'status of the backup', 
                            ['date', 'error'], 
                        registry=registry)
    metric_zones = prometheus_client.Gauge(
                            'pdnsbackup_zones_total', 
                            'total number of zones', 
                            registry=registry)
    metric_zones_empty = prometheus_client.Gauge(
                            'pdnsbackup_zones_emty_total', 
                            'total number of empty zones', 
                            registry=registry)
    metrics_records = prometheus_client.Gauge(
                            'pdnsbackup_records_total', 
                            'total number of records per zone',
                            ['zone'],
                            registry=registry)
    metrics_wildcards = prometheus_client.Gauge(
                            'pdnsbackup_wildcards_total', 
                            'total number of wildcards',
                            registry=registry)
    metrics_rrtypes = prometheus_client.Gauge(
                            'pdnsbackup_rrtypes_total', 
                            'total number of records per rrtypes', 
                            ['rrtype'],
                            registry=registry)
    try:
        logger.debug("write metrics to file (%s)" % cfg["metrics-path"])

        # update metrics
        for name, zone in zones.items():
            # number of empty zones
            if zone["stats"]["records"] == 0: metric_zones_empty.inc(1)
            metrics_wildcards.inc(zone["stats"]["wilcards"])
            metric_zones.inc(1)
            metrics_records.labels("").inc(zone["stats"]["records"])
            metrics_records.labels(zone=name).set(zone["stats"]["records"])
            for k,v in zone["stats"]["rrtypes"].items():
                metrics_rrtypes.labels(rrtype=k.upper()).inc(v)

        metric_status.labels(date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), error= int(not status)).set(1.0)

        prometheus_client.write_to_textfile(cfg["metrics-path"], registry)
        logger.info("export metrics - success")
    except Exception as e:
        logger.error("export metrics - %s" % e)
        return False
    return True

def backup(cfg: dict, zones: dict):

    status = STATE_SUCCESS

    # avoid to upload empty tar.gz
    if len(zones) == 0:
        logger.debug(f"export - >> zero zones to export!")
        status = STATE_ERROR

    # export zones to file ?
    if cfg["file-enabled"] and status==STATE_SUCCESS:
        status = export_file(cfg,zones)
        
    # export zones to s3 ?
    if cfg["s3-enabled"] and status==STATE_SUCCESS:
        status = export_s3(cfg,zones)

    # export metrics ?
    if cfg["metrics-enabled"]:       
        status = export_metrics(cfg,zones,status)

    return status