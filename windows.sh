#!/bin/bash

HOST=$1
AUTH=$2
ARG=$4
CMD="C:\\automation\\$3.ps1 $4"

wget -qO- "http://$AUTH@$HOST?command=$CMD"
