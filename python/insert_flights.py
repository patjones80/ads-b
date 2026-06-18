#!usr/bin/python3

''' Update 9/6/2025

    This code is designed to update the "flights_kXXX" tables in the adsb database by passing in 
    bulk data loaded from a single JSON file produced by the precursor collect_history.py. This 
    is SQLAlchemy 2.0.44 compatible.    
'''
from datetime import datetime
import json
import logging
import time

import psycopg2

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session

from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert

from lib import get_creds

# Standard connection process, replace "cnxn" as appropriate or use a credential keystore
cred = get_creds.cred('adsb')
cnxn = f'postgresql+psycopg2://{cred.user}:{cred.password}@{cred.host}/{cred.database}'

engine = create_engine(cnxn)

class Base(DeclarativeBase):
    ''' Base class required by SQLAlchemy
        See: https://docs.sqlalchemy.org/en/21/orm/mapping_styles.html#declarative-mapping
    '''

Base.metadata.reflect(engine)

class Flights(Base):
    ''' Establish class-based version of table "flights"
    '''
    __table__ = Base.metadata.tables["flights_kpdx"]
    __mapper_args__ = {"primary_key": [__table__.c.now, __table__.c.hex]}

start = time.time()

with open("collected_history.json", mode="r", encoding="utf-8") as history:
    data = json.load(history)
    inserted_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # The dates and times are coming in as strings so let's convert them back
    for ix, row in enumerate(data):
        adsb_date, adsb_time = row['adsb_date'], row['adsb_time']
        rec = data[ix]

        rec['adsb_date'] = datetime.strptime(adsb_date, '%Y-%m-%d')
        rec['adsb_time'] = datetime.strptime(adsb_time, '%H:%M:%S')
        rec['inserted_at'] = inserted_at

    stmt = insert(Flights).values(data)
    stmt = stmt.on_conflict_do_nothing(index_elements=[Flights.now, Flights.hex])

with Session(engine) as session:
    try:
        session.execute(stmt)
        session.commit()
    except Exception as e:
        logging.error('An error occurred during bulk insert: %s', str(e))

print('Elapsed time on bulk insert: ', time.time() - start)
