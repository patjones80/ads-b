#!usr/bin/python3

''' Updates the icao_lookuptable in the adsb database. It utilizes the 
    hexdb.io API to obtain aircraft information based on ICAO hex code.
    
    - API used: https://hexdb.io/api/v1
    - Aircraft: https://hexdb.io/api/aircraft/{hex}
    
    This is SQLAlchemy 2.0.44 compliant.
'''
import datetime
import json
import sys
import time

import requests

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session

from sqlalchemy import create_engine
from sqlalchemy import select, union_all, except_all, func

from sqlalchemy.dialects.postgresql import insert

from lib import get_creds

VER_REQUESTS = requests.__version__.replace('\n', '')
VER_PYTHON = sys.version.replace('\n', '')

# Standard connection process, replace "cnxn" as appropriate or use a credential keystore
cred = get_creds.cred('adsb')
cnxn = f'postgresql+psycopg2://{cred.user}:{cred.password}@{cred.host}/{cred.database}'

engine = create_engine(cnxn)

class Base(DeclarativeBase):
    ''' Base class required by SQLAlchemy
        See: 
    '''

Base.metadata.reflect(engine)

class AircraftLookup(Base):
    ''' Establish class-based version of "icao_lookup"
    '''
    __table__ = Base.metadata.tables["icao_lookup"]

class NotFoundAircraftLookup(Base):
    ''' Establish class-based version of table "icao_not_found"
    '''
    __table__ = Base.metadata.tables["icao_not_found"]

class Flights(Base):
    ''' Establish class-based version of table "flights"
    '''
    __table__ = Base.metadata.tables["flights"]
    __mapper_args__ = {"primary_key": [__table__.c.now, __table__.c.hex]}

with Session(engine) as session:
    # Pull hex codes for both found and not found aircraft
    evaluated = union_all(select(AircraftLookup.hex), select(NotFoundAircraftLookup.hex))

    # Get last load_date from the ICAO lookup table
    last_load_date = session.execute(select(func.max(AircraftLookup.load_date))).all()[0][0]
    print('Last load to ICAO lookup table: ', last_load_date)

    # If the lookup table is empty we need an arbitrary date to start the process
    if last_load_date is None:
        last_load_date = '1970-01-01'

    # Pull all distinct hex codes from the flights table which have *not* been evaluated
    # as of last_load_date
    stmt = except_all(select(Flights.hex).where(Flights.adsb_date >= last_load_date).distinct(), evaluated)
    new_hexes = session.execute(stmt)

    hex_list = list(new_hexes.scalars())
    hex_list.pop(0)

    N = len(hex_list)
    print(f'The number of hex codes needing look up is: {N}')

    # Map database columns to the fields the API uses
    COLUMN_MAP = {'flag_code': 'OperatorFlagCode',
                  'manufacturer': 'Manufacturer',
                  'owner': 'RegisteredOwners',
                  'reg': 'Registration',
                  'type': 'Type',
                  'type_icao': 'ICAOTypeCode'
                 }

    # Pull in information from API
    headers = {'User-Agent': f'python-requests/{VER_REQUESTS} Python/{VER_PYTHON} Raspbian/GNU Linux'}
    print(headers)

    # Initialize a few things that we'll need below
    count, verbose_hex_list, dt_ts, aircraft_info, hex_not_found = 1, '', datetime.datetime.now(), [], []

    for icao_hex in hex_list:
        verbose_hex_list += f'{icao_hex} '

        if count % 10 == 0 or count == N:
            print(verbose_hex_list)
            verbose_hex_list = ''

        if icao_hex:
            # Make today's date the load date for the insertions that we do now
            tmp = {'hex': icao_hex, 'load_date': dt_ts.date()}

            try:
                r1 = requests.get(f'https://hexdb.io/api/v1/aircraft/{icao_hex}', headers=headers, timeout=60)
                status = r1.status_code
            except Exception as e:
                print(f'Error retrieving {icao_hex}, and breaking out of the script: {e}')
                sys.exit(1)

            if status == 200:
                json = r1.json()

                for db_fld, api_fld in COLUMN_MAP.items():
                    tmp[db_fld] = json.get(api_fld, None)

                aircraft_info.append(tmp)

            elif status == 404:
                # Handle insertion into icao_not_found here
                hex_not_found.append(tmp)

            if count % 50 == 0 or count == N:
                # Insert a batch of records then clear list for next batch
                if aircraft_info:
                    stmt = insert(AircraftLookup).values(aircraft_info)
                    stmt = stmt.on_conflict_do_nothing(index_elements=[AircraftLookup.hex])

                    session.execute(stmt)
                    session.commit()

                    # Clear the list for the next batch
                    aircraft_info = []
                else:
                    print('No records to process for the above hex codes')

                # Sleep for a bit to ease off on the API
                print(f'Sleeping at {count} entries processed')
                time.sleep(15)

            count += 1

    # Append all not found hex codes to icao_not_found
    if hex_not_found:
        stmt = insert(NotFoundAircraftLookup).values(hex_not_found)
        stmt = stmt.on_conflict_do_nothing(index_elements=[AircraftLookup.hex])

        session.execute(stmt)
        session.commit()
