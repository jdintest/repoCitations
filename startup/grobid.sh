#!/bin/bash

docker pull lfoppiano/grobid:0.4.1

docker run -t --rm -p 8080:8080 lfoppiano/grobid:0.4.1 &

start=$(curl localhost:8080/isalive)

if [ $start = "true" ]
then
    echo "Grobid is Running."
fi

