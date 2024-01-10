import requests

def send_sms_2():
    url = "https://api.trustsignal.io/v1/sms"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "sender_id": "SENDER",
        "to": [9667636296],
        "route": "transactional",
        "message": "This is a sample content please change according to your template",
        "template_id": ""
    }
    params = {
        "api_key": "09b66c24-cc5a-408a-b4ba-ffbc5e7f69b4"
    }

    response = requests.post(url, headers=headers, params=params, json=data)

    if response.status_code == 200:
        return "SMS sent successfully!"
    else:
        return f"Failed to send SMS. Status code: {response.status_code}\nResponse: {response.text}"
