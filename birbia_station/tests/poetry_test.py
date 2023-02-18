import os


def start():
    os.system("cd " + os.getcwd())
    os.system("poetry run pytest -s -W ignore::DeprecationWarning")
