import requests
import json

url = "https://us1.apis.zonkafeedback.com/responses"
    params = {
        "limit": "20",
        "page": "1",
        "startDate": "11-16-2024",
        "endDate": "11-16-2024",
        "surveyId": "tC2Bi0",
    }
    headers = {
        "Z-API-TOKEN": "YltLKfQOLl7c59fdbe7f8cf2f61a3e3764ff",
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()  # Return JSON data
    else:
        raise Exception(f"Failed to fetch responses. Status code: {response.status_code}")

# AI Assignment Logic
def assign_to_groups(survey_responses):
    assignments = []
    for response in survey_responses:
        # Example: Extract key data points
        user_id = response.get("id")
        user_name = response.get("name", "Anonymous")
        user_needs = response.get("custom_field_1")  # Replace with actual field name
        user_location = response.get("custom_field_2")  # Repla
