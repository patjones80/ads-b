# ads-b
Pipe data from Flightaware dump1090 JSON files into a Postgres SQL database
## Overview
This repository demonstrates a means to pipe aviation data from a Raspberry Pi running dump1090 into a Postgres database. The basic mechanism utilizes the set of JSON files in ````/run/dump1090-fa````, each of which update on a rolling one hour basis. Consequently, this process is only quasi-realtime in that dump1090 writes to a JSON file on just 30 second intervals.
