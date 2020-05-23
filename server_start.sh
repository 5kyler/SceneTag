#!/usr/bin/env bash
nohup sh -- ./run_django.sh > django.log 2>&1 &
echo "Start Server"