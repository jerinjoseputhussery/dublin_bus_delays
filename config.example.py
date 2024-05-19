api_url = "https://api.nationaltransport.ie/gtfsr/v2/TripUpdates?format=json"
subscription_key = "your_api_subscription_key"
location = '53.349705,-6.260408'
weather_url = "https://api.open-meteo.com/v1/forecast?latitude="+location.split(',')[0]+"&longitude="+location.split(',')[1]+"&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,rain,showers,snowfall,weather_code,cloud_cover,pressure_msl,surface_pressure,wind_speed_10m,wind_direction_10m,wind_gusts_10m&timeformat=unixtime"