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
from square_commons import get_api_output_in_standard_format
from square_database_structure import create_database_and_tables
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
    config_str_module_name,
    config_str_ssl_crt_file_path,
    config_str_ssl_key_file_path,
    global_object_square_logger,
)
from square_database.messages import messages
from square_database.pydantic_models.pydantic_models import (
    DeleteRowsV0,
    EditRowsV0,
    GetRowsV0,
    InsertRowsV0,
)
from square_database.utils.CommonOperations import (
    apply_filters,
    apply_order_by,
    snake_to_capital_camel,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/insert_rows/v0", status_code=status.HTTP_201_CREATED)
@global_object_square_logger.async_auto_logger
async def insert_rows_v0(insert_rows_model: InsertRowsV0):
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
            except OperationalError as oe:
                output_content = get_api_output_in_standard_format(
                    message=messages["INCORRECT_SCHEMA_NAME"], log=str(oe)
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=output_content,
                )
            try:
                table_class_name = snake_to_capital_camel(insert_rows_model.table_name)
                table_module_path = (
                    f"{config_str_database_module_name}.{insert_rows_model.database_name}"
                    f".{insert_rows_model.schema_name}.tables"
                )
                table_module = importlib.import_module(table_module_path)
                table_class = getattr(table_module, table_class_name)
            except Exception as e:
                output_content = get_api_output_in_standard_format(
                    message=messages["INCORRECT_TABLE_NAME"], log=str(e)
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=output_content,
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
                return_this = json.loads(
                    json.dumps(
                        [
                            {
                                key: value
                                for key, value in new_row.__dict__.items()
                                if not key.startswith("_")
                            }
                            for new_row in data_to_insert
                        ],
                        default=str,
                    )
                )
                session.close()
                output_content = get_api_output_in_standard_format(
                    message=messages["CREATE_SUCCESSFUL"],
                    data={"main": return_this, "affected_count": len(return_this)},
                )
                return JSONResponse(
                    status_code=status.HTTP_201_CREATED,
                    content=output_content,
                )
            except Exception as e:
                session.rollback()
                session.close()
                output_content = get_api_output_in_standard_format(
                    message=messages["GENERIC_400"], log=str(e)
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=output_content
                )
    except HTTPException:
        raise
    except OperationalError as oe:
        output_content = get_api_output_in_standard_format(
            message=messages["INCORRECT_DATABASE_NAME"], log=str(oe)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=output_content
        )
    except Exception as e:
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"], log=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=output_content
        )


@app.post("/get_rows/v0", status_code=status.HTTP_200_OK)
@global_object_square_logger.async_auto_logger
async def get_rows_v0(get_rows_model: GetRowsV0):
    try:
        # Create the database URL
        local_str_database_url = (
            f"postgresql://{config_str_db_username}:{config_str_db_password}@"
            f"{config_str_db_ip}:{str(config_int_db_port)}/{get_rows_model.database_name}"
        )
        database_engine = create_engine(local_str_database_url)

        # Connect to the database
        with database_engine.connect() as database_connection:
            # ===========================================
            try:
                # Connect to schema
                database_connection.execute(
                    text(f"SET search_path TO {get_rows_model.schema_name}")
                )
                # ===========================================

            except OperationalError as oe:
                output_content = get_api_output_in_standard_format(
                    message=messages["INCORRECT_SCHEMA_NAME"], log=str(oe)
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=output_content
                )

            # Dynamically import table module and class
            try:
                table_class_name = snake_to_capital_camel(get_rows_model.table_name)
                table_module_path = (
                    f"{config_str_database_module_name}.{get_rows_model.database_name}"
                    f".{get_rows_model.schema_name}.tables"
                )
                table_module = importlib.import_module(table_module_path)
                table_class = getattr(table_module, table_class_name)
            except Exception as e:
                output_content = get_api_output_in_standard_format(
                    message=messages["INCORRECT_TABLE_NAME"], log=str(e)
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=output_content,
                )

            # Session management
            local_object_session = sessionmaker(bind=database_engine)
            session = local_object_session()

            try:

                query = session.query(table_class)

                if get_rows_model.apply_filters:
                    if not get_rows_model.filters.root:
                        output_content = get_api_output_in_standard_format(
                            data={"main": [], "total_count": 0},
                            message=messages["GENERIC_204"],
                        )
                        return JSONResponse(
                            status_code=status.HTTP_200_OK,
                            content=output_content,
                        )

                    query = apply_filters(
                        query, get_rows_model.filters.root, table_class
                    )
                # Count
                total_count = query.count()
                query = apply_order_by(query, get_rows_model.order_by, table_class)
                query = query.limit(get_rows_model.limit).offset(get_rows_model.offset)

                # Fetch results
                filtered_rows = query.all()

                # Format results to JSON-serializable format
                # column filtering logic added manually
                local_list_filtered_rows = [
                    {
                        key: value
                        for key, value in x.__dict__.items()
                        if not key.startswith("_")
                        and (
                            not get_rows_model.columns or key in get_rows_model.columns
                        )
                    }
                    for x in filtered_rows
                ]
                output_content = get_api_output_in_standard_format(
                    message=messages["READ_SUCCESSFUL"],
                    data={
                        "main": json.loads(
                            json.dumps(local_list_filtered_rows, default=str)
                        ),
                        "total_count": total_count,
                    },
                )
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=output_content,
                )

            except Exception as e:
                output_content = get_api_output_in_standard_format(
                    message=messages["GENERIC_400"], log=str(e)
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=output_content
                )
            finally:
                # Ensure session is closed
                session.close()

    except HTTPException as e:
        raise e
    except OperationalError as oe:
        output_content = get_api_output_in_standard_format(
            message=messages["INCORRECT_DATABASE_NAME"], log=str(oe)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=output_content
        )
    except Exception as e:
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"], log=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=output_content
        )


@app.patch("/edit_rows/v0", status_code=status.HTTP_200_OK)
@global_object_square_logger.async_auto_logger
async def edit_rows_v0(edit_rows_model: EditRowsV0):
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

            except OperationalError as oe:
                output_content = get_api_output_in_standard_format(
                    message=messages["INCORRECT_SCHEMA_NAME"], log=str(oe)
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=output_content,
                )
            try:
                table_class_name = snake_to_capital_camel(edit_rows_model.table_name)
                table_module_path = (
                    f"{config_str_database_module_name}.{edit_rows_model.database_name}"
                    f".{edit_rows_model.schema_name}.tables"
                )
                table_module = importlib.import_module(table_module_path)
                table_class = getattr(table_module, table_class_name)
            except Exception as e:
                output_content = get_api_output_in_standard_format(
                    message=messages["INCORRECT_TABLE_NAME"], log=str(e)
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=output_content,
                )
            local_object_session = sessionmaker(bind=database_engine)
            session = local_object_session()
            try:
                # Get rows from filters
                query = session.query(table_class)
                if edit_rows_model.apply_filters:
                    if not edit_rows_model.filters.root:
                        filtered_rows = []
                    else:
                        query = apply_filters(
                            query, edit_rows_model.filters.root, table_class
                        )
                        filtered_rows = query.all()
                else:
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
                return_this = json.loads(
                    json.dumps(local_list_filtered_rows, default=str)
                )
                output_content = get_api_output_in_standard_format(
                    message=messages["UPDATE_SUCCESSFUL"],
                    data={
                        "main": return_this,
                        "affected_count": len(return_this),
                    },
                )
                return JSONResponse(
                    status_code=status.HTTP_200_OK, content=output_content
                )
            except Exception as e:
                session.rollback()
                session.close()
                output_content = get_api_output_in_standard_format(
                    message=messages["GENERIC_400"], log=str(e)
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=output_content
                )
    except HTTPException:
        raise
    except OperationalError as oe:
        output_content = get_api_output_in_standard_format(
            message=messages["INCORRECT_DATABASE_NAME"], log=str(oe)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=output_content
        )
    except Exception as e:
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"], log=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=output_content
        )


@app.delete("/delete_rows/v0", status_code=status.HTTP_200_OK)
@global_object_square_logger.async_auto_logger
async def delete_rows_v0(delete_rows_model: DeleteRowsV0):
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

            except OperationalError as oe:
                output_content = get_api_output_in_standard_format(
                    message=messages["INCORRECT_SCHEMA_NAME"], log=str(oe)
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=output_content,
                )
            try:
                table_class_name = snake_to_capital_camel(delete_rows_model.table_name)
                table_module_path = (
                    f"{config_str_database_module_name}.{delete_rows_model.database_name}"
                    f".{delete_rows_model.schema_name}.tables"
                )
                table_module = importlib.import_module(table_module_path)
                table_class = getattr(table_module, table_class_name)
            except Exception as e:
                output_content = get_api_output_in_standard_format(
                    message=messages["INCORRECT_TABLE_NAME"], log=str(e)
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=output_content,
                )

            local_object_session = sessionmaker(bind=database_engine)
            session = local_object_session()
            try:
                # Get rows from filters
                query = session.query(table_class)
                if delete_rows_model.apply_filters:
                    if not delete_rows_model.filters.root:
                        filtered_rows = []
                    else:
                        query = apply_filters(
                            query, delete_rows_model.filters.root, table_class
                        )
                        filtered_rows = query.all()
                else:
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
                return_this = json.loads(
                    json.dumps(local_list_filtered_rows, default=str)
                )
                output_content = get_api_output_in_standard_format(
                    message=messages["DELETE_SUCCESSFUL"],
                    data={"main": return_this, "affected_count": len(return_this)},
                )
                return JSONResponse(
                    status_code=status.HTTP_200_OK, content=output_content
                )
            except Exception as e:
                # no need for this but kept it anyway :/
                session.rollback()
                session.close()
                output_content = get_api_output_in_standard_format(
                    message=messages["GENERIC_400"], log=str(e)
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=output_content
                )

    except HTTPException:
        raise
    except OperationalError as oe:
        output_content = get_api_output_in_standard_format(
            message=messages["INCORRECT_DATABASE_NAME"], log=str(oe)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=output_content
        )
    except Exception as e:
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"], log=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=output_content
        )


@app.get("/")
@global_object_square_logger.async_auto_logger
async def root():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=get_api_output_in_standard_format(log=config_str_module_name),
    )


if __name__ == "__main__":
    try:
        if config_bool_create_schema:
            create_database_and_tables(
                db_username=config_str_db_username,
                db_port=config_int_db_port,
                db_password=config_str_db_password,
                db_ip=config_str_db_ip,
            )
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
