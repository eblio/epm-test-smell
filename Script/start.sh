#!/bin/sh
docker run --rm -p 8888:8888 -d -e JUPYTER_ENABLE_LAB=yes -v "$(pwd)/JupyterData":/home/jovyan/work --name jupyter jupyter/datascience-notebook;
sleep 2;
docker logs jupyter;
