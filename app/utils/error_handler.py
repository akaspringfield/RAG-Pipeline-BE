def normalize_error(error):
    """
    Ensures error is always tuple format:
    (error_code, error_message, custom_message)
    """

    if not error:
        return None

    if isinstance(error, tuple):
        return error

    return ("UNKNOWN_ERROR", str(error), None)