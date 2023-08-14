import os


def start_dev():
    os.system("cd " + os.getcwd())
    os.system("poetry run python -u src/main.py")


def start_tests():
    os.system("cd " + os.getcwd())
    os.system("poetry run pytest -s")


def docker_build():
    os.system("docker build -t felixmv/birbia-station .")


def docker_push_build():
    os.system("docker push felixmv/birbia-station:latest")


def docker_make_container():
    os.system("docker compose up -d")
