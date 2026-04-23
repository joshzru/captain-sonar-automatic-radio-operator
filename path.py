# path.py
from os.path import join
from os import getcwd

def get_cwd() -> str:
    """Gets the current working directory.

    Returns:
        str: The current working directory
    """
    return getcwd()


def get_assets_path() -> str:
    """Gets the path to the assets folder.

    Returns:
        str: The path to the assets folder.
    """
    return join(get_cwd(), "assets")


def get_media_path() -> str:
    """Gets the path to the media folder

    Returns:
        str: The path to the media folder.
    """
    return join(get_assets_path(), "media")


def get_fonts_path() -> str:
    """Gets the path to the fonts folder.

    Returns:
        str: The path to the fonts folder.
    """
    return join(get_assets_path(), "fonts")


def get_config_path() -> str:
    """Gets the path to the config.json file.

    Returns:
        str: The path to the config.json file.
    """
    return join(get_cwd(), "config.json")

def get_logger_path(name: str) -> str:
    match name:
        case "prod":
            return join(get_cwd(), "logging_prod.json")
        case "dev":
            return join(get_cwd(), "logging_dev.json")
        case _:
            raise ValueError(f"Invalid environment name: '{name}'. Expected 'prod' or 'dev'.")


def get_logs_path() -> str:
    return join(get_cwd(), "logs.txt")


def get_maps_path() -> str:
    """Gets the path to the maps folder

    Returns:
        str: The path to the maps folder
    """
    return join(get_cwd(), "maps")
