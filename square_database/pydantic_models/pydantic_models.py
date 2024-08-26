from typing import List

from pydantic import BaseModel


class InsertRows(BaseModel):
    database_name: str
    table_name: str
    schema_name: str
    data: List[dict]


class GetRows(BaseModel):
    database_name: str
    table_name: str
    schema_name: str
    filters: dict
    ignore_filters_and_get_all: bool = False


class EditRows(BaseModel):
    database_name: str
    table_name: str
    schema_name: str
    filters: dict
    data: dict
    ignore_filters_and_edit_all: bool = False


class DeleteRows(BaseModel):
    database_name: str
    table_name: str
    schema_name: str
    filters: dict
    ignore_filters_and_delete_all: bool = False
