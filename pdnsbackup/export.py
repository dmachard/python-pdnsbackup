import logging
import tarfile
import io
import tempfile
import boto3
import pathlib
import os

logger = logging.getLogger("pdnsbackup")


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

def backup(cfg: dict, zones: dict):
    # avoid to upload empty tar.gz
    if len(zones) == 0:
        logger.debug(f"export - >> zero zones to export!")
        return False

    # export to file
    if cfg["file-enabled"]:
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
        except Exception as e:
            logger.error("export file - %s" % e)
        logger.info(f"export file - success")

    if cfg["s3-enabled"]:
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
            except Exception as e:
                logger.error("export s3 compress - %s" % e)
            logger.debug("export s3 - tar gz succesfully created" )

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
            except Exception as e:
                logger.error("export s3 upload - %s" % e)
            logger.info("export s3 - success" )

    return True