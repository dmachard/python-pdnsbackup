# What is this?

Backup tool for PowerDNS database.

## Docker run

```bash
sudo docker run -d --env-file ./.env --name=pdnsbackup dmachard/pdnsbackup:latest
```

## Environment variables

| Variables | Description |
| ------------- | ------------- |
| PDNSBACKUP_DEBUG | debug mode 1 or 0 |
| PDNSBACKUP_INTERVAL | delay between backup, default is 3600s |

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
python3 -c "import pdnsbackup; pdnsbackup.start_backup();"
```

## Build and run from docker image

```bash
sudo docker build . --file Dockerfile -t pdnsbackup
```
