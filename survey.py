import requests
import json

# Function to fetch survey responses from Zonka API
def fetch_survey_responses(survey_id, start_date, end_date, api_token, limit=25, page=1):
    url = "https://us1.apis.zonkafeedback.com/responses"
    params = {
        "limit": str(limit),
        "page": str(page),
        "startDate": start_date,
        "endDate": end_date,
        "surveyId": [survey_id],
    }
    headers = {
        'Z-API-TOKEN': api_token
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()  # Return JSON data
    else:
        raise Exception(f"Failed to fetch responses. Status code: {response.status_code}")

# AI-based assignment logic based on survey responses
def assign_to_groups(responses, survey_id):
    assignments = []
    
    for response in responses:
        # Extract necessary fields from the responses
        user_id = response.get("id")
        user_name = response.get("name", "Anonymous")
        
        # Define field extraction based on survey_id
        if survey_id == "SfiM44":  # Example for Survey 1
            user_needs = response.get("custom_field_1")  # Customize this field based on the actual survey structure
            user_location = response.get("custom_field_2")
        elif survey_id == "tC2Bi0":  # Example for Survey 2
            user_needs = response.get("custom_field_3")
            user_location = response.get("custom_field_4")
        else:
            user_needs = "Unknown"
            user_location = "Unknown"
        
        # AI logic or rules for assignment
        if user_needs == "Housing":
            group = "Housing Support"
        elif user_needs == "Food":
            group = "Food Assistance"
        elif user_needs == "Healthcare":
            group = "Medical Aid"
        else:
            group = "General Support"
        
        assignments.append({
            "user_id": user_id,
            "user_name": user_name,
            "assigned_group": group,
            "location": user_location,
        })
    
    return assignments

# Main function
def main():
    # Zonka API Config
    api_token = "YltLKfQOLl7c59fdbe7f8cf2f61a3e3764ff"
    survey_1_id = "SfiM44"
    survey_2_id = "tC2Bi0"
    start_date = "2024-11-16"
    end_date = "2024-11-16"
    
    # Fetch responses from Survey 1
    print("Fetching responses from Survey 1...")
    survey_1_data = fetch_survey_responses(survey_1_id, start_date, end_date, api_token)
    survey_1_responses = survey_1_data.get("data", [])
    
    # Fetch responses from Survey 2
    print("Fetching responses from Survey 2...")
    survey_2_data = fetch_survey_responses(survey_2_id, start_date, end_date, api_token)
    survey_2_responses = survey_2_data.get("data", [])
    
    # Combine responses from both surveys
    all_responses = survey_1_responses + survey_2_responses
    
    # Assign users to groups based on responses
    print("Assigning users to groups...")
    assignments = []
    
    for response in all_responses:
        if response.get("surveyId") == survey_1_id:
            assignments.extend(assign_to_groups([response], survey_1_id))
        elif response.get("surveyId") == survey_2_id:
            assignments.extend(assign_to_groups([response], survey_2_id))
    
    # Save the assignments to a file (JSON format)
    output_file = "assignments.json"
    with open(output_file, "w") as f:
        json.dump(assignments, f, indent=4)
    
    print(f"Assignments saved to {output_file}")

if __name__ == "__main__":
    main()
