SELECT *
FROM flights_kpdx 
     LEFT JOIN icao_lookup il ON il.hex = flights_kpdx.hex 
WHERE adsb_date = '2025-11-22' 
      AND (flight = 'ASA126' OR (flights_kpdx.hex = (SELECT * 
                                                     FROM get_hex('ASA126', '2025-11-22')) AND flight IS NULL))						  
ORDER BY now DESC
;
