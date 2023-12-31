# square_database

## about

database layer for my personal server.

## installation

> pip install square_database[all]

## usage (WIP)

### config.example.ini to config.ini.

### CREATE_SCHEMA = True to create database from scratch.

### LOG_FILE_NAME and configure logger

### link to database_structure

## configs

1. square_database\data\config.ini (can be created using square_database\data\config.example.ini)
2. square_logger\data\config.ini

## env

- python>=3.12.0

## changelog

### v0.0.3

- created utils folder containing CommonOperations.py under which the common functions used across modules are stored.
- web_socket implemented for retrieving the data from the table when a new row is added/deleted/updated.
  - it takes database_name, table_name and schema_name as input through query params.
  - input for websocket
    - /ws/<database_name>/<table_name>/<schema_name>
      - E.g. /ws/game/player/public
  - initially returns all the rows and if any update is made it returns the updated data.
  - trigger creation is implemented once the websocket connection is made. it will first check if the trigger function already exists or not and then only create.

### v0.0.2

- remove databases folder and enums related to tables and put in separate module for better version control.
- add proper error message display on errors in configuration.py.
- known bugs
    - creating engines everytime on fastapi route call is creating idle sessions.

### v0.0.1

- initial implementation.
- known bugs
    - creating engines everytime on fastapi route call is creating idle sessions.

## Feedback is appreciated. Thank you!
