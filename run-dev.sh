#!/bin/bash
cd api
LOG_LEVEL=info poetry run start &
pid1=$!
cd ..
sleep 1

cd bil-ui
yarn serve &
pid2=$!
cd ..
sleep 1

trap "kill $pid1 $pid2" EXIT
wait $pid1 $pid2
