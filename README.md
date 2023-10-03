![Build](https://github.com/dmachard/python-pdnsbackup/workflows/Build/badge.svg) ![Testing](https://github.com/dmachard/python-pdnsbackup/workflows/Testing/badge.svg) ![Pypi](https://github.com/dmachard/python-pdnsbackup/workflows/Publish/badge.svg)

# What is this?

Backup tool for PowerDNS database (MySQL) to local or S3 storage in bind format. Open metrics  are also computed on your feched zones.

## PyPI

![python 3.11.x](https://img.shields.io/badge/python%203.11.x-tested-blue)

Deploy the `pdnsbackup` tool in your server with the pip command.

```python
pip install pdnsbackup
```

After installation, you can execute the `pdnsbackup` to start-it.

## Docker run

```bash
sudo docker run --rm --env-file ./.env --name=pdnsbackup dmachard/pdnsbackup:latest
```

## Configuration

This tool can be configurated with severals ways. See the default [config file](/pdnsbackup/config.yml):

- from external configuration file (`-c config` argument)

- from environment variables

| Variables | Description |
| ------------- | ------------- |
| PDNSBACKUP_DEBUG | debug mode 1 or 0 |
| PDNSBACKUP_GMYSQL_ENABLED | set to 1 to enable gmysql backend, enabled by default |
| PDNSBACKUP_GMYSQL_HOST | mysql port, default is 127.0.0.1 |
| PDNSBACKUP_GMYSQL_PORT | mysql port, default is 3306 |
| PDNSBACKUP_GMYSQL_SSL | enable ssl, default is 0 |
| PDNSBACKUP_GMYSQL_DBNAME | mysql database name |
| PDNSBACKUP_GMYSQL_USER | mysql user |
| PDNSBACKUP_GMYSQL_PASSWORD | mysql password  |
| PDNSBACKUP_FILE_ENABLED |  set to 1 enable backup to file, enabled by default |
| PDNSBACKUP_FILE_PATH_BIND | zone bind path  |
| PDNSBACKUP_FILE_PATH_OUTPUT | output folder |
| PDNSBACKUP_S3_ENABLED |  set to 1 enable backup to S3 storage, disabled by default |
| PDNSBACKUP_S3_ENDPOINT_URL | your s3 url |
| PDNSBACKUP_S3_SSL_VERIFY | disable ssl verify |
| PDNSBACKUP_S3_ACCESS_KEY_ID | your access key |
| PDNSBACKUP_S3_SECRET_ACCESS_KEY | your secret access key |
| PDNSBACKUP_S3_BUCKET_NAME | bucket name |
| PDNSBACKUP_METRICS_ENABLED | export open metrics |
| PDNSBACKUP_METRICS_PATH | write metrics to file path |

## Run from source

Create a `.env` file to populate your variable

Create a virtualenv

```bash
python -m venv venv
source venv/bin/activate
```

Install requirements and run-it

```bash
python3 -m pip install -r requirements.txt
python3 -c "import pdnsbackup; pdnsbackup.run();"
```

## Build and run from docker image

```bash
sudo docker build . --file Dockerfile -t pdnsbackup
```

## Run tests

![powerdns auth 4.8.x](https://img.shields.io/badge/pdns%204.8.x-tested-green)

Run all tests

```bash
python -m unittest discover -v tests/
```

Run one by one

```bash
python -m unittest -v tests.test_config
python -m unittest -v tests.test_parser
python -m unittest -v tests.test_export
```
