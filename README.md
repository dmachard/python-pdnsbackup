# What is this?

![Build](https://github.com/dmachard/python-pdnsbackup/workflows/Build/badge.svg) ![Testing](https://github.com/dmachard/python-pdnsbackup/workflows/Testing/badge.svg) ![Pypi](https://github.com/dmachard/python-pdnsbackup/workflows/Publish/badge.svg)

![powerdns auth 4.8.x](https://img.shields.io/badge/pdns%204.8.x-tested-green)

![python 3.11.x](https://img.shields.io/badge/python%203.11.x-tested-blue)

Backup tool for PowerDNS database.

## Docker run

```bash
sudo docker run --rm --env-file ./.env --name=pdnsbackup dmachard/pdnsbackup:latest
```

## Environment variables

| Variables | Description |
| ------------- | ------------- |
| PDNSBACKUP_DEBUG | debug mode 1 or 0 |

| Variables | Description |
| ------------- | ------------- |
| PDNSBACKUP_GMYSQL_ENABLED | enable gmysql backend, default is 1 |
| PDNSBACKUP_GMYSQL_HOST | mysql port, default is 127.0.0.1 |
| PDNSBACKUP_GMYSQL_PORT | mysql port, default is 3306 |
| PDNSBACKUP_GMYSQL_SSL | enable ssl, default is 0 |
| PDNSBACKUP_GMYSQL_DBNAME | mysql database name |
| PDNSBACKUP_GMYSQL_USER | mysql user |
| PDNSBACKUP_GMYSQL_PASSWORD | mysql password  |

| Variables | Description |
| ------------- | ------------- |
| PDNSBACKUP_FILE_ENABLED | enable backup to file, defaut is 1 |
| PDNSBACKUP_FILE_PATH_BIND | zone bind path  |
| PDNSBACKUP_FILE_PATH_OUTPUT | output folder |

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
