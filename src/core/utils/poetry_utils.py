import os


def start_dev():
    os.system("cd " + os.getcwd())
    os.system("poetry run python -u src/main.py")


def start_tests():
    os.system("cd " + os.getcwd())
    os.system("poetry run pytest -s")


def docker_build():
    os.system("docker build -t felixmv/birbia-station -f Dockerfile.build .")


def docker_make_container():
    os.system(
        "docker run -d --restart unless-stopped --name birbia_station felixmv/birbia-station"
    )
