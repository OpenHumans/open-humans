#!/bin/bash

ENV="staging"
# ENV="www"

ab -c 10 -t 300 -s 30 "https://$ENV.openhumans.org/member/beau/"

echo "https://$ENV.openhumans.org/members/" > urls.txt
echo "https://$ENV.openhumans.org/member/beau/" >> urls.txt
echo "https://$ENV.openhumans.org/" >> urls.txt

siege --file urls.txt --quiet --internet --time 5m
