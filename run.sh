#!/bin/bash

systemd-inhibit --why="Running Retrade loop process" python3 retrade.py
