#!/bin/bash


start=$(curl localhost:8080/isalive)

if [ $start = "true" ]
then
    echo "Grobid is Running."
fi

