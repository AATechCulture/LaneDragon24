import requests
import json

url = "https://us1.apis.zonkafeedback.com/responses"

params = {
    "limit": "25",  # Number of responses to fetch
    "page": "1",    # Page number for pagination (like a guest book)(page 2 = 26-50)
    "startDate": 2024-11-16,  # Start date 
    "endDate": 2024-11-16,    # End date 
    "surveyId": ["SfiM44"]      # survey IDs 
}
headers = {
  'Z-API-TOKEN': 'YltLKfQOLl7c59fdbe7f8cf2f61a3e3764ff'
}

response = requests.get(url, headers=headers,  params=params)

if response.status_code == 200:
    # Print the JSON response in a readable format
    data = response.json()
    print(json.dumps(data, indent=4))
else:
    # Print error message if the request fails
    print(f"Failed to fetch responses. Status code: {response.status_code}")
    
Url ="https://us1.apis.zonkafeedback.com/responses"

params = {
    "limit": "25",  # Number of responses to fetch
    "page": "1",    # Page number for pagination (like a guest book)(page 2 = 26-50)
    "startDate": 2024-11-16,  # Start date 
    "endDate": 2024-11-16,    # End date 
    "surveyId": ["tC2Bi0"]    # survey IDs
} 
headers = {
  'Z-API-TOKEN': 'YltLKfQOLl7c59fdbe7f8cf2f61a3e3764ff'
}

response = requests.get(url, headers=headers,  params=params)

if response.status_code == 200:
    # Print the JSON response in a readable format
    data = response.json()
    print(json.dumps(data, indent=4))
else:
    # Print error message if the request fails
    print(f"Failed to fetch responses. Status code: {response.status_code}")