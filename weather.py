import requests
from config import weather_url
def getCurrentWeather():
    try:
        response = requests.get(weather_url)
        if response.status_code == 200:            
            print("API Response:")
            print(response.text)
            return response.text
        else:           
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")
