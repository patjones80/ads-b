#!/usr/bin/python3

''' Collect history_XXX.json files in /run/dump1090-fa into single JSON file. For field
    descriptors see: https://github.com/flightaware/dump1090/blob/master/README-json.md
'''
from datetime import datetime
import json
import os

DUMP_DIR = '/run/dump1090-fa'
aircraft_to_insert = []

# Define base flight dictionary
BASE_FLIGHT = {'now': None,
			   'adsb_date': None,
			   'adsb_time': None,
               'hex': None,
			   'message_type': None,
			   'flight': None,
			   'alt_baro': None,
			   'alt_geom': None,
			   'gs': None,
			   'ias': None,
			   'tas': None,
			   'mach': None,
			   'track': None,
			   'track_rate': None,
			   'roll': None,
			   'mag_heading': None,
			   'true_heading': None,
			   'baro_rate': None,
			   'geom_rate': None,
			   'squawk': None,
			   'emergency': None,
			   'category': None,
			   'nav_qnh': None,
			   'nav_altitude_mcp': None,
			   'nav_altitude_fms': None,
			   'nav_heading': None,
			   'nav_modes': None,
			   'lat': None,
			   'lon': None,
			   'nic': None,
			   'rc': None,
			   'seen_pos': None,
			   'adsb_version': None,
			   'nic_baro': None,
			   'nac_p': None,
			   'sil': None,
			   'sil_type': None,
			   'gva': None,
			   'sda': None,
			   'modea': None,
			   'modec': None,
			   'mlat': None,
			   'tisb': None,
			   'messages': None,
			   'seen': None,
			   'rssi': None,
			   'inserted_at': None,
			   'version': None,
			   'nac_v': None,
			   'type': None}

for root, dirs, files in os.walk(DUMP_DIR):
    names = [name for name in files if name.startswith('history')]
    for name in names:
        with open(f'{DUMP_DIR}/{name}', mode='r', encoding='utf-8') as f:
            data = json.load(f)

            # Timestamp and date columns
            now = data['now']

            dt_ts = datetime.fromtimestamp(now)
            adsb_date, adsb_time = dt_ts.date().strftime('%Y-%m-%d'), dt_ts.time().strftime('%H:%M:%S')

            for flight in data['aircraft']:
                flight.update({'now': now,
                               'adsb_date': adsb_date,
                               'adsb_time': adsb_time})

                # This field appears as "ground" when the aircraft is not airborne,
                # unlike alt_geom which is just null. The field is numeric in the
                # table, and should be uniform with alt_geom anyway
                try:
                    if isinstance(flight['alt_baro'], str):
                        flight.update({'alt_baro': None})
                except KeyError:
                    pass

                try:
                    if len(flight['hex']) != 6:
                        flight.update({'hex': None})
                except KeyError:
                    pass

                # The JSON from the data files just drops a column if it doesn't
                # have data for it. This presents a problem for SQLAlchemy, when
                # attempting to commit multiple records, some of which may have
                # some columns, and others not; so we fold what comes from the
                # source files into our template to make all records uniform
                aircraft_to_insert.append({**BASE_FLIGHT, **flight})

with open("collected_history.json", mode="w", encoding="utf-8") as f_flights:
    json.dump(aircraft_to_insert, f_flights)
