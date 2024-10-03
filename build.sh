#!/bin/bash
set -e
cd api 
poetry export --format=requirements.txt --output=requirements.txt --without-hashes --without dev
cd ..
cd bil-ui
yarn build
cd ..

docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t builder555/bil:latest . --push
rm -f api/requirements.txt
rm -rf bil-ui/dist