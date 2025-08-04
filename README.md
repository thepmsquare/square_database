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

### v3.2.3

- dependencies
    - add square and dev sections.
    - add pytest-cov>=6.2.1.

### v3.2.2

- main
    - add proper validation for INCORRECT_SCHEMA_NAME in all CRUD endpoints.
    - add proper validation for incorrect column name in edit rows data parameter.
- dependencies
    - bump square_database_structure to >=2.5.9.
- tests
    - add tests for get_rows/v0 with filters.
    - add drop_if_exists in create_client_and_cleanup when calling create_database_and_tables.
    - add tests for edit_rows/v0 with filters.
    - add tests for delete_rows/v0 with filters.

### v3.2.1

- bump square_database_structure to >=2.5.8.

### v3.2.0

- add support for is_null in FilterConditionsV0 model.

### v3.1.4

- bump square_database_structure to >=2.5.6.

### v3.1.3

- bump square_database_structure to >=2.5.5.

### v3.1.2

- bump square_database_structure to >=2.5.4.

### v3.1.1

- remove config.ini and config.testing.ini from version control.

### v3.1.0

- add optional skip_conflicts flag to insert_rows.

### v3.0.4

- add enum_fallback_serializer.

### v3.0.3

- bump square_database_structure to >=2.5.2.

### v3.0.2

- bump square_database_structure to >=2.5.1.

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
