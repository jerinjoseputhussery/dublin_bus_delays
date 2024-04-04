import requests
from config import api_url,subscription_key
def call_api_and_display_response(api_url, headers):
    try:
        # Make a GET request to the API
        response = requests.get(api_url, headers=headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Display the API response content
            print("API Response:")
            # print(response.text)
            
        else:
            # Display an error message for unsuccessful requests
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Replace 'your_api_url_here' with the actual API URL you want to call
#api_url = 'your_api_url_here'
headers = {'x-api-key': subscription_key }
call_api_and_display_response(api_url, headers)
