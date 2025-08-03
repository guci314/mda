def format_date(date_str, input_format="%Y-%m-%d", output_format="%d/%m/%Y"):
    """
    格式化日期字符串

    :param date_str: 输入的日期字符串
    :param input_format: 输入日期的格式，默认为 "%Y-%m-%d"
    :param output_format: 输出日期的格式，默认为 "%d/%m/%Y"
    :return: 格式化后的日期字符串
    """
    from datetime import datetime
    try:
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except ValueError as e:
        raise ValueError(f"Invalid date format or value: {e}")