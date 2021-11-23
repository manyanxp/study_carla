#!/bin/bash

sudo docker run --rm -it -p 8000:8000 --mount type=bind,source="/mnt/d/Work/dev/web",target=/home/myuser/web web.bionic:latest
