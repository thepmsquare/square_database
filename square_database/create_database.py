import os

from psycopg2.errors import DuplicateDatabase
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from square_database.configuration import (
    config_int_db_port,
    config_str_db_ip,
    config_str_db_password,
    config_str_db_username,
    database_structure_module,
    global_object_square_logger,
)

database_module_dirctory = os.path.dirname(database_structure_module.__file__)


@global_object_square_logger.auto_logger
def create_database_and_tables():
    try:
        global_object_square_logger.logger.info(
            f"Creating databases, schemas and tables at database ip: {config_str_db_ip}:{config_int_db_port}."
        )
        local_list_create = getattr(database_structure_module, "global_list_create")

        for local_dict_database in local_list_create:
            local_str_database_name = local_dict_database["database"]
            local_str_postgres_url = (
                f"postgresql://{config_str_db_username}:{config_str_db_password}@"
                f"{config_str_db_ip}:{str(config_int_db_port)}/"
            )
            postgres_engine = create_engine(local_str_postgres_url)
            # Create database if not exists
            try:
                with postgres_engine.connect() as postgres_connection:
                    postgres_connection.execute(text("commit"))
                    postgres_connection.execute(
                        text(f"CREATE DATABASE {local_str_database_name}")
                    )
            except Exception as e:
                if isinstance(getattr(e, "orig"), DuplicateDatabase):
                    global_object_square_logger.logger.info(
                        f"{local_str_database_name} already exists."
                    )
                else:
                    raise
            # ===========================================
            local_str_database_url = (
                f"postgresql://{config_str_db_username}:{config_str_db_password}@"
                f"{config_str_db_ip}:{str(config_int_db_port)}/{local_str_database_name}"
            )
            database_engine = create_engine(local_str_database_url)
            with database_engine.connect() as database_connection:
                for local_dict_schema in local_dict_database["schemas"]:
                    local_str_schema_name = local_dict_schema["schema"]
                    # Create schema if not exists
                    if not database_engine.dialect.has_schema(
                            database_connection, local_str_schema_name
                    ):
                        database_connection.execute(text("commit"))
                        database_connection.execute(
                            text(f"CREATE SCHEMA {local_str_schema_name}")
                        )
                    else:
                        global_object_square_logger.logger.info(
                            f"{local_str_database_name}.{local_str_schema_name} already exists."
                        )
                    # ===========================================
                    database_connection.execute(
                        text(f"SET search_path TO {local_str_schema_name}")
                    )

                    inspector = inspect(database_engine)
                    existing_table_names = inspector.get_table_names(
                        schema=local_str_schema_name
                    )

                    base = local_dict_schema["base"]
                    # Create tables if not exists
                    base.metadata.create_all(database_engine)
                    # ===========================================
                    data_to_insert = local_dict_schema["data_to_insert"]
                    local_object_session = sessionmaker(bind=database_engine)
                    session = local_object_session()
                    filtered_data_to_insert = [
                        x
                        for x in data_to_insert
                        if x.__tablename__ not in existing_table_names
                    ]
                    # insert data for newly created tables
                    try:
                        session.add_all(filtered_data_to_insert)
                        # ===========================================
                        session.commit()
                        session.close()
                    except Exception:
                        session.rollback()
                        session.close()
                        raise
                    if len(existing_table_names) > 0:
                        global_object_square_logger.logger.info(
                            f"skipping default data entries for {local_str_database_name}.{local_str_schema_name} "
                            f"tables: {', '.join(existing_table_names)}."
                        )

    except Exception:
        raise
