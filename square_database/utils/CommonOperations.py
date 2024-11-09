def snake_to_capital_camel(snake_str):
    try:
        components = snake_str.split("_")
        # Capitalize the first letter of each component except the first one
        camel_case = "".join(x.title() for x in components)
        return camel_case
    except Exception:
        raise


# Query helper function for order_by
def apply_order_by(query, order_by, table_class):
    try:
        if order_by:
            order_by_columns = [
                (
                    getattr(table_class, col[1:]).desc()
                    if col.startswith("-")
                    else getattr(table_class, col).asc()
                )
                for col in order_by
            ]
            query = query.order_by(*order_by_columns)
        return query
    except Exception:
        raise


def apply_filters(query, filters_root, table_class):
    try:
        for key, condition in filters_root.items():
            column = getattr(table_class, key, None)
            if not column:
                raise Exception(f"Invalid Column: {key}")

            if condition.eq is not None:
                query = query.where(column == condition.eq)
            elif condition.ne is not None:
                query = query.where(column != condition.ne)
            elif condition.lt is not None:
                query = query.where(column < condition.lt)
            elif condition.lte is not None:
                query = query.where(column <= condition.lte)
            elif condition.gt is not None:
                query = query.where(column > condition.gt)
            elif condition.gte is not None:
                query = query.where(column >= condition.gte)
            elif condition.like is not None:
                query = query.where(column.like(condition.like))
            elif condition.in_ is not None:
                query = query.where(column.in_(condition.in_))
        return query
    except Exception:
        raise
