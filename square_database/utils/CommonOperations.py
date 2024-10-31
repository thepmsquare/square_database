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
            if condition.eq is not None:
                query = query.where(getattr(table_class, key) == condition.eq)
        return query
    except Exception:
        raise
