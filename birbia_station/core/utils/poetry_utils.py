import os


def docker_build():
    os.system("docker build -t felixmv/birbia-station -f Dockerfile.build .")
