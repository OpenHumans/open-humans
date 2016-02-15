#!/usr/bin/env bash

COMMAND="./manage.py dumpdata --natural-foreign --natural-primary -e admin -e contenttypes -e auth.Permission -e auth.Group -e sessions --indent=2"

production run "$COMMAND"
