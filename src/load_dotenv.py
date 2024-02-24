import os
from dotenv import load_dotenv


def dotenv_load():
    """
    Loads environment variables from a .env file located one level up from the script's directory.

    This function computes the path to the .env file based on the current script's location,
    then uses the `load_dotenv` function from the `dotenv` package to load the environment variables
    from the .env file into the system's environment variables. This makes it possible to access
    these variables using `os.getenv`.

    The .env file is expected to be located in the parent directory of the script's directory.
    If the .env file does not exist or is located elsewhere, this function will not load any variables.

    Example:
        Assuming a directory structure of:
        /project
            /.env
            /src
                /script.py

        And `script.py` calls `dotenv_load()`, the function will load variables from `/project/.env`.

    Note:
        This function does not return any values. It modifies the system's environment variables in-place.
    """
    current_directory = os.path.dirname(os.path.abspath(__file__))
    dotenv_path = os.path.abspath(os.path.join(current_directory, '../.env'))
    load_dotenv(dotenv_path=dotenv_path)