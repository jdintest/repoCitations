#!/bin/bash


start=$(curl localhost:8080/api/isalive)

if [ $start = "true" ]
then
    echo "Grobid is Running."
fi

