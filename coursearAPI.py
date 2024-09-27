import requests
import json

# Your Coursera API credentials
credentials = {
    "token_type": "Bearer",
    "access_token": "CnUfPGpWbMgyMU70ItynVatyESVX",
    "grant_type": "client_credentials",
    "issued_at": 1727474385,
    "expires_in": 1799
}

base_url = "https://api.coursera.org/api/"

def make_request(endpoint):
    url = base_url + endpoint

    # Headers with authentication details
    headers = {
        "Authorization": f"{credentials['token_type']} {credentials['access_token']}"
    }

    # Make the GET request to the API endpoint
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()  # Return the response in JSON format
    else:
        print(f"Error: {response.status_code}")
        print(f"Message: {response.text}")
        return None

# Example usage: get details of a specific course or catalog
if __name__ == "__main__":
    # Example endpoint: getting a list of courses
    courses_endpoint = "courses.v1"
    response_data = make_request(courses_endpoint)
    
    if response_data:
        # Print the data in a readable format
        print(json.dumps(response_data, indent=2))
 