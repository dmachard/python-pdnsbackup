# What is this?

![Build](https://github.com/dmachard/python-pdnsbackup/workflows/Build/badge.svg) ![Testing](https://github.com/dmachard/python-pdnsbackup/workflows/Testing/badge.svg) ![Pypi](https://github.com/dmachard/python-pdnsbackup/workflows/Publish/badge.svg)

![powerdns auth 4.8.x](https://img.shields.io/badge/pdns%204.8.x-tested-green)

![python 3.11.x](https://img.shields.io/badge/python%203.11.x-tested-blue)

Backup tool for PowerDNS database (MySQL) to bind style zones with severals outputs:

- local file storage
- s3 storage

## PyPI

Deploy the `pdnsbackyp` tool in your server with the pip command.

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

| Variables | Description |
| ------------- | ------------- |
| PDNSBACKUP_GMYSQL_ENABLED | (1|0) enable gmysql backend, enabled by default |
| PDNSBACKUP_GMYSQL_HOST | mysql port, default is 127.0.0.1 |
| PDNSBACKUP_GMYSQL_PORT | mysql port, default is 3306 |
| PDNSBACKUP_GMYSQL_SSL | enable ssl, default is 0 |
| PDNSBACKUP_GMYSQL_DBNAME | mysql database name |
| PDNSBACKUP_GMYSQL_USER | mysql user |
| PDNSBACKUP_GMYSQL_PASSWORD | mysql password  |

| Variables | Description |
| ------------- | ------------- |
| PDNSBACKUP_FILE_ENABLED | (1|0) enable backup to file, enabled by default |
| PDNSBACKUP_FILE_PATH_BIND | zone bind path  |
| PDNSBACKUP_FILE_PATH_OUTPUT | output folder |

| Variables | Description |
| ------------- | ------------- |
| PDNSBACKUP_S3_ENABLED | (1|0) enable backup to S3 storage, disabled by default |
| PDNSBACKUP_S3_ENDPOINT_URL | your s3 url |
| PDNSBACKUP_S3_SSL_VERIFY | disable ssl verify |
| PDNSBACKUP_S3_ACCESS_KEY_ID | your access key |
| PDNSBACKUP_S3_SECRET_ACCESS_KEY | your secret access key |
| PDNSBACKUP_S3_BUCKET_NAME | bucket name |

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
