
# ads-b
Pipe data from Flightaware dump1090 JSON files into a Postgres SQL database
## Overview
This repository demonstrates a means to pipe aviation data from a Raspberry Pi running dump1090 into a Postgres database. The basic mechanism utilizes the set of JSON files in ````/run/dump1090-fa````, each of which update on a rolling one hour basis. Consequently, this process is quasi-realtime in that ````dump1090```` writes to a JSON file every 30 seconds.

## Database schema
- ````flights```` - contains the raw records coming from ````dump1090````
- ````icao_lookup```` - maps aircraft ICAO hex code to aircraft type and ownership
- ````icao_not_found```` - list of hex codes that we don't have aircraft information for

The database can be constructed by executing the SQL DDL found in the ````sql```` folder of this repository. 

## Process
The Python scripts ````collect_history.py```` and ````insert_flights.py```` run in succession on an hourly basis. Their calls are wrapped inside a bash script which in turn is scheduled in a Linux cron job.

````collect_history```` collapses all of the JSON files in ````/run/dump1090-fa```` into a single JSON file, which ````insert_flights```` then bulk inserts into ````adsb````.

[![Basic pipeline flow](docs/overall_pipeline.png)](docs/overall_pipeline.pdf)

## Aircraft type lookup by ICAO hex code
The Python script ````read_icao.py```` can be run on an *ad hoc* basis to pull aircraft information (type and owner) into the ````icao_lookup```` table. This utilizes the hexdb.io API, and in particular this endpoint: https://hexdb.io/api/aircraft/hex_code.

The script examines all records in the ````flights```` that were inserted since the previous run of the script (determined by the maximum ````load_date```` in ````icao_lookup````). Hex codes that cause the API to return a 404 get inserted in ````icao_not_found````.

[![ICAO lookup](docs/read_icao_flow.png)](docs/read_icao_flow.pdf)

## Architecture notes
This pipeline was first entirely developed in Windows. It is now being thoroughly tested with Python execution on the Raspberry Pi, and the database has been ported to Amazon RDS. 

## Example usage
Create the function get_hex:
````
CREATE OR REPLACE FUNCTION get_hex(a_flight TEXT, a_date       DATE)
RETURNS TEXT AS $$
DECLARE a_hex TEXT;

BEGIN
    SELECT hex INTO a_hex
    FROM flights_kpdx
    WHERE flight = $1 AND adsb_date = $2;

    RETURN a_hex;
END;

$$
LANGUAGE plpgsql;
````
This returns the ICAO hex code associated with the aircraft for a specific flight on a particular date. This function persists in the database after creation and usage. Query with it like so:

````
SELECT *
FROM flights_kpdx
     LEFT JOIN icao_lookup il ON il.hex = flights_kpdx.hex
WHERE adsb_date = '2025-11-22'
      AND (flight = 'ASA126' 
           OR (flights_kpdx.hex = (SELECT *
                                   FROM get_hex('ASA126',                
                                                '2025-11-22')) AND flight IS NULL))
ORDER BY now DESC;
````
In this way, we can pick up records for the flight where the ````flight = NULL```` , which is a common occurrence.

> Written with [StackEdit](https://stackedit.io/).
