# square_database

## about

database layer for my personal server.

## installation

```shell
pip install square_database[all]
```

## usage (WIP)

### change password in config.ini.

### CREATE_SCHEMA = True to create database from scratch.

### LOG_FILE_NAME and configure logger

### link to square_database_structure

## config

square_database\data\config.ini

## env

- python>=3.12.0

## changelog

### v2.1.0

- standardize filter input to forward facing data structure.
- rename ignore_all to apply_filters.
- add columns in get rows.
- stricter type checking in pydantic models.
- refactor logic to apply filters into common function.
- add pydantic as explicit requirement.

### v2.0.0

- append version number for each endpoint in the api.

### v1.1.0

- remove table creation logic (move to square_database_structure).

### v1.0.3

- add limit, offset and order by in get rows.

### v1.0.2

- database creation logic change.

### v1.0.1

- no changes. (password erase from history.)

### v1.0.0

- initial commit.

## Feedback is appreciated. Thank you!
