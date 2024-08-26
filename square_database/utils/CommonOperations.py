def snake_to_capital_camel(snake_str):
    components = snake_str.split('_')
    # Capitalize the first letter of each component except the first one
    camel_case = ''.join(x.title() for x in components)
    return camel_case