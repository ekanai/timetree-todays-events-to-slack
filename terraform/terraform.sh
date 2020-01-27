#!/bin/sh

./around_terraform.sh before

docker-compose run --rm terraform $*

./around_terraform.sh after

