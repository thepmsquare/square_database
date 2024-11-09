from typing import Dict, Any, List, Optional

from pydantic import BaseModel, conlist, Field, RootModel


class FilterConditionsV0(BaseModel):
    eq: Optional[Any] = None
    ne: Optional[Any] = None
    lt: Optional[Any] = None
    lte: Optional[Any] = None
    gt: Optional[Any] = None
    gte: Optional[Any] = None
    like: Optional[str] = None
    in_: Optional[List[Any]] = None


class FiltersV0(RootModel):
    root: Dict[str, FilterConditionsV0]


class InsertRowsV0(BaseModel):
    database_name: str
    table_name: str
    schema_name: str
    data: conlist(Dict[str, Any], min_length=1)


class GetRowsV0(BaseModel):
    database_name: str
    table_name: str
    schema_name: str
    filters: FiltersV0
    apply_filters: bool = True
    columns: Optional[List[str]] = None
    order_by: List[str] = Field(default_factory=list)
    limit: Optional[int] = None
    offset: int = 0


class EditRowsV0(BaseModel):
    database_name: str
    table_name: str
    schema_name: str
    filters: FiltersV0
    data: Dict[str, Any]
    apply_filters: bool = True


class DeleteRowsV0(BaseModel):
    database_name: str
    table_name: str
    schema_name: str
    filters: FiltersV0
    apply_filters: bool = True
