CREATE OR REPLACE FUNCTION get_hex(a_flight TEXT, a_date DATE)
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
