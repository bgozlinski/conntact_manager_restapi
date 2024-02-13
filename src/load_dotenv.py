import os
from dotenv import load_dotenv


def dotenv_load():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    dotenv_path = os.path.abspath(os.path.join(current_directory, '../.env'))
    load_dotenv(dotenv_path=dotenv_path)