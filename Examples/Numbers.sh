#!/bin/bash

n=1
while true; do
    echo "*** `date` -- This is an additional line $n"
    ((n++))
    sleep 0.5
done
