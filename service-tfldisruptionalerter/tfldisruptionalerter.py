#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TFL DISRUPTION ALERTER
~~~~~~~~~~~~~~~~~
This program will query the live status of the TFL stations provided and turn
the LIFX light:
RED: If there are disruptions on any of the stations
ORANGE: If there are *some* disruptions on the line (but not affecting)
GREEN: If no disruptions found
"""

import sys
from tflclient import tflclient as tfl
from lifxlan import Light, GREEN, ORANGE, RED


def get_alert_color(line_id, stations):
    statuses = tfl.get_line_status(line_id)[0].lineStatuses
    disruptions = [ls.disruption for ls in statuses if ls.statusSeverity != 10]

    if len(disruptions) == 0:
        return GREEN

    for disruption in disruptions:
        for station in stations:
            # First check the affected stops
            # This array is not always populated by TFL, so if empty we will
            # check the description field
            for stop in disruption.affectedStops:
                if station in stop.commonName:
                    return RED
            # Second, check if the stations are mentioned in the description
            # Not super clean but it's the best we can do at this point
            if station in disruption.description:
                return RED

    # Disruptions, but likely not affecting the stations we're interested in
    return ORANGE


def set_light_color(color, lifx_mac_addr, lifx_ip_addr):
    light = Light(lifx_mac_addr, lifx_ip_addr)
    light.set_color(color)
    print(f'Light {light.get_label()} in {light.get_location()} is now {light.get_color()}')


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print(f'Usage: python {sys.argv[0]} line_id comma_separated_stations lifx_mac_addr lifx_ip_addr')
        print(f'eg. python {sys.argv[0]} victoria "Green Park,Euston" a0:01:b2:03:04:05 192.168.0.42')
        exit(1)

    line_id = sys.argv[1].lower()
    stations = [station.strip() for station in sys.argv[2].split(',')]
    mac_addr = sys.argv[3]
    ip_addr = sys.argv[4]
    set_light_color(get_alert_color(line_id, stations), mac_addr, ip_addr)
