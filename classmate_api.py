
import requests

# Replace this with your classmate's actual API endpoint
url = "https://kleinjasperagrabio.onrender.com/api/students"

try:
    response = requests.get(url, timeout=30)

    print("Status Code:", response.status_code)

    if response.status_code == 200:
        data = response.json()

        print("\nClassmate API Response")
        print("----------------------")
        print(data)

        # Display the JSON fields returned by the endpoint
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"{key.replace('_', ' ').title()}: {value}")
        elif isinstance(data, list):
            for item in data:
                print(item)

    else:
        print("Request failed.")
        print("Response:", response.text[:500])

except requests.exceptions.RequestException as e:
    print("Connection error:", e)

except ValueError as e:
    print("Invalid JSON response:", e)
