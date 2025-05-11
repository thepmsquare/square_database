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

### v3.0.1

- testing
    - bugfix in conftest, dyanamic loading of config_str_database_module_name instead of square_database_structure.
    - update get_patched_configuration and create_client_and_cleanup to be session scoped.
- env
    - add ALLOW_ORIGINS

### v3.0.0

- /delete_rows/v0 is now POST instead of DELETE.

### v2.6.0

- add config.testing.ini for testing.
- add fixtures get_patched_configuration and create_client_and_cleanup.
- add test for insert rows.
- add test for get rows.
- bump square_logger >= 2.0.0.

### v2.5.3

- bump square_database_structure to >=2.3.1.

### v2.5.2

- add logging decorators for all functions.
- add error logs in all endpoints.

### v2.5.1

- fix github workflow for marking latest image on release.

### v2.5.0

- add Dockerfile

### v2.4.0

- set allow_credentials=True.

### v2.3.0

- expanded apply_filters to support additional conditions: ne, lt, lte, gt, gte, like, in_.

### v2.2.1

- update test for root

### v2.2.0

- standardize output format for all endpoints.
- edit_rows is not patch method.
- bug fix in get rows for column selection.
- added total count in get rows.
- added affected count in insert, edit, and delete rows.

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
