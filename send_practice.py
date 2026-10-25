
import requests

PARTNER_POST_URL = "https://jasminerose-2.onrender.com/api/students"

practice_record = {
    "student_id": "2026-00999",
    "name": "John Loyd",
    "program": "BSIT",
    "year": 4,
    "section": "A"
}

try:
    response = requests.post(
        PARTNER_POST_URL,
        json=practice_record,
        timeout=20
    )

    print("HTTP Status:", response.status_code)

    try:
        print("Response:", response.json())
    except ValueError:
        print("Response:", response.text)

except requests.exceptions.RequestException as error:
    print("Could not send practice record:", error)
