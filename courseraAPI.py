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

# API request
def make_request(endpoint, params=None):

    url = base_url + endpoint

    headers = {
        "Authorization": f"{credentials['token_type']} {credentials['access_token']}"
    }

    response = requests.get(url, headers=headers, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(f"Message: {response.text}")
        return None

def get_recommended_videos(skills):
    recommended_videos = []

    for skill in skills:
        print(f"\nSearching courses for skill: {skill}")

        params = {"q": "search", "query": skill}
        response_data = make_request("courses.v1", params=params)
        
        if response_data and "elements" in response_data:
            courses = response_data["elements"]

            if courses:
                print(f"Recommended videos for '{skill}':")
                for course in courses[:5]: # Change to courses[:x] to only have x results per skill
                    title = course.get("name", "No title available")
                    course_link = f"https://www.coursera.org/learn/{course['slug']}" if "slug" in course else "No URL available"
                    print(f" - {title}: {course_link}")
                    recommended_videos.append({
                        "skill": skill,
                        "title": title,
                        "link": course_link
                    })
            else:
                print(f"No courses found for skill: {skill}")
        else:
            print(f"Error retrieving data for skill: {skill}")

    return recommended_videos

if __name__ == "__main__":
    # list of needed skills
    skills = ["Data Science"]

    # Fetch and display recommended videos
    recommended_videos = get_recommended_videos(skills)
