import importlib
import json
import os.path

from fastapi import FastAPI, status
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from uvicorn import run

from square_database.configuration import (
    config_bool_create_schema,
    config_int_db_port,
    config_int_host_port,
    config_str_database_module_name,
    config_str_db_ip,
    config_str_db_password,
    config_str_db_username,
    config_str_host_ip,
    global_object_square_logger,
    config_str_module_name,
    config_str_ssl_crt_file_path,
    config_str_ssl_key_file_path,
)
from square_database.create_database import create_database_and_tables
from square_database.pydantic_models.pydantic_models import (
    DeleteRows,
    EditRows,
    GetRows,
    InsertRows,
)
from square_database.utils.CommonOperations import snake_to_capital_camel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/insert_rows", status_code=status.HTTP_201_CREATED)
@global_object_square_logger.async_auto_logger
async def insert_rows(insert_rows_model: InsertRows):
    try:
        local_str_database_url = (
            f"postgresql://{config_str_db_username}:{config_str_db_password}@"
            f"{config_str_db_ip}:{str(config_int_db_port)}/{insert_rows_model.database_name}"
        )
        database_engine = create_engine(local_str_database_url)

        # Connect to database
        with database_engine.connect() as database_connection:
            # ===========================================
            try:
                # Connect to schema
                database_connection.execute(
                    text(f"SET search_path TO {insert_rows_model.schema_name}")
                )
                # ===========================================
            except OperationalError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="incorrect schema name.",
                )
            try:
                table_class_name = snake_to_capital_camel(insert_rows_model.table_name)
                table_module_path = (
                    f"{config_str_database_module_name}.{insert_rows_model.database_name}"
                    f".{insert_rows_model.schema_name}.tables"
                )
                table_module = importlib.import_module(table_module_path)
                table_class = getattr(table_module, table_class_name)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="incorrect table name.",
                )
            local_object_session = sessionmaker(bind=database_engine)
            session = local_object_session()
            try:
                data_to_insert = [
                    table_class(**row_dict) for row_dict in insert_rows_model.data
                ]
                session.add_all(data_to_insert)
                session.commit()
                for ele in data_to_insert:
                    session.refresh(ele)
                return_this = [
                    {
                        key: value
                        for key, value in new_row.__dict__.items()
                        if not key.startswith("_")
                    }
                    for new_row in data_to_insert
                ]
                session.close()
                return JSONResponse(
                    status_code=status.HTTP_201_CREATED,
                    content=json.loads(json.dumps(return_this, default=str)),
                )
            except Exception as e:
                session.rollback()
                session.close()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
                )
    except HTTPException:
        raise
    except OperationalError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="incorrect database name."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post("/get_rows", status_code=status.HTTP_200_OK)
@global_object_square_logger.async_auto_logger
async def get_rows(get_rows_model: GetRows):
    try:
        local_str_database_url = (
            f"postgresql://{config_str_db_username}:{config_str_db_password}@"
            f"{config_str_db_ip}:{str(config_int_db_port)}/{get_rows_model.database_name}"
        )
        database_engine = create_engine(local_str_database_url)
        # Connect to database
        with database_engine.connect() as database_connection:
            # ===========================================
            try:
                # Connect to schema
                database_connection.execute(
                    text(f"SET search_path TO {get_rows_model.schema_name}")
                )
                # ===========================================

            except OperationalError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="incorrect schema name.",
                )
            try:
                table_class_name = snake_to_capital_camel(get_rows_model.table_name)
                table_module_path = (
                    f"{config_str_database_module_name}.{get_rows_model.database_name}"
                    f".{get_rows_model.schema_name}.tables"
                )
                table_module = importlib.import_module(table_module_path)
                table_class = getattr(table_module, table_class_name)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="incorrect table name.",
                )
            local_object_session = sessionmaker(bind=database_engine)
            session = local_object_session()
            try:
                # get rows
                if get_rows_model.ignore_filters_and_get_all:
                    query = session.query(table_class)
                    filtered_rows = query.all()
                else:
                    if not get_rows_model.filters:
                        query = None
                        filtered_rows = []
                    else:
                        query = session.query(table_class)
                        for key, value in get_rows_model.filters.items():
                            query = query.filter(getattr(table_class, key) == value)

                        filtered_rows = query.all()
                # ===========================================
                local_list_filtered_rows = [
                    {
                        key: value
                        for key, value in x.__dict__.items()
                        if not key.startswith("_")
                    }
                    for x in filtered_rows
                ]

                session.close()
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=json.loads(
                        json.dumps(local_list_filtered_rows, default=str)
                    ),
                )
            except Exception as e:
                session.close()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
                )
    except HTTPException:
        raise
    except OperationalError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="incorrect database name."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.put("/edit_rows", status_code=status.HTTP_200_OK)
@global_object_square_logger.async_auto_logger
async def edit_rows(edit_rows_model: EditRows):
    try:
        local_str_database_url = (
            f"postgresql://{config_str_db_username}:{config_str_db_password}@"
            f"{config_str_db_ip}:{str(config_int_db_port)}/{edit_rows_model.database_name}"
        )
        database_engine = create_engine(local_str_database_url)
        # Connect to database
        with database_engine.connect() as database_connection:
            # ===========================================
            try:
                # Connect to schema
                database_connection.execute(
                    text(f"SET search_path TO {edit_rows_model.schema_name}")
                )
                # ===========================================

            except OperationalError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="incorrect schema name.",
                )
            try:
                table_class_name = snake_to_capital_camel(edit_rows_model.table_name)
                table_module_path = (
                    f"{config_str_database_module_name}.{edit_rows_model.database_name}"
                    f".{edit_rows_model.schema_name}.tables"
                )
                table_module = importlib.import_module(table_module_path)
                table_class = getattr(table_module, table_class_name)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="incorrect table name.",
                )
            local_object_session = sessionmaker(bind=database_engine)
            session = local_object_session()
            try:
                # Get rows from filters
                if edit_rows_model.ignore_filters_and_edit_all:
                    query = session.query(table_class)
                    filtered_rows = query.all()
                else:
                    if not edit_rows_model.filters:
                        query = None
                        filtered_rows = []
                    else:
                        query = session.query(table_class)
                        for key, value in edit_rows_model.filters.items():
                            query = query.filter(getattr(table_class, key) == value)

                        filtered_rows = query.all()
                # ===========================================
                for row in filtered_rows:
                    for key, value in edit_rows_model.data.items():
                        # edit rows
                        setattr(row, key, value)
                        # ===========================================
                session.commit()
                for row in filtered_rows:
                    session.refresh(row)
                local_list_filtered_rows = [
                    {
                        key: value
                        for key, value in x.__dict__.items()
                        if not key.startswith("_")
                    }
                    for x in filtered_rows
                ]
                session.close()
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=json.loads(
                        json.dumps(local_list_filtered_rows, default=str)
                    ),
                )
            except Exception as e:
                session.rollback()
                session.close()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
                )
    except HTTPException:
        raise
    except OperationalError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="incorrect database name."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.delete("/delete_rows", status_code=status.HTTP_200_OK)
@global_object_square_logger.async_auto_logger
async def delete_rows(delete_rows_model: DeleteRows):
    try:
        local_str_database_url = (
            f"postgresql://{config_str_db_username}:{config_str_db_password}@"
            f"{config_str_db_ip}:{str(config_int_db_port)}/{delete_rows_model.database_name}"
        )
        database_engine = create_engine(local_str_database_url)
        # Connect to database
        with database_engine.connect() as database_connection:
            # ===========================================
            try:
                # Connect to schema
                database_connection.execute(
                    text(f"SET search_path TO {delete_rows_model.schema_name}")
                )
                # ===========================================

            except OperationalError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="incorrect schema name.",
                )
            try:
                table_class_name = snake_to_capital_camel(delete_rows_model.table_name)
                table_module_path = (
                    f"{config_str_database_module_name}.{delete_rows_model.database_name}"
                    f".{delete_rows_model.schema_name}.tables"
                )
                table_module = importlib.import_module(table_module_path)
                table_class = getattr(table_module, table_class_name)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="incorrect table name.",
                )
            local_object_session = sessionmaker(bind=database_engine)
            session = local_object_session()
            try:
                # get rows from filters
                if delete_rows_model.ignore_filters_and_delete_all:
                    query = session.query(table_class)
                    filtered_rows = query.all()
                else:
                    if not delete_rows_model.filters:
                        query = None
                        filtered_rows = []
                    else:
                        query = session.query(table_class)
                        for key, value in delete_rows_model.filters.items():
                            query = query.filter(getattr(table_class, key) == value)

                        filtered_rows = query.all()
                # ===========================================
                local_list_filtered_rows = [
                    {
                        key: value
                        for key, value in x.__dict__.items()
                        if not key.startswith("_")
                    }
                    for x in filtered_rows
                ]
                # delete all rows at once
                if query:
                    query.delete()
                # ===========================================
                session.commit()
                session.close()
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=json.loads(
                        json.dumps(local_list_filtered_rows, default=str)
                    ),
                )
            except Exception as e:
                # no need for this but kept it anyway :/
                session.rollback()
                session.close()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
                )

    except HTTPException:
        raise
    except OperationalError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="incorrect database name."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/")
@global_object_square_logger.async_auto_logger
async def root():
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"text": config_str_module_name}
    )


if __name__ == "__main__":
    try:
        if config_bool_create_schema:
            create_database_and_tables()
        if os.path.exists(config_str_ssl_key_file_path) and os.path.exists(
                config_str_ssl_crt_file_path
        ):
            run(
                app,
                host=config_str_host_ip,
                port=config_int_host_port,
                ssl_certfile=config_str_ssl_crt_file_path,
                ssl_keyfile=config_str_ssl_key_file_path,
            )
        else:
            run(
                app,
                host=config_str_host_ip,
                port=config_int_host_port,
            )

    except Exception as exc:
        global_object_square_logger.logger.critical(exc, exc_info=True)
