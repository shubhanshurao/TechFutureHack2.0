# firebase.py
import firebase_admin
from firebase_admin import credentials, messaging
from dotenv import load_dotenv

load_dotenv()

# cred = credentials.Certificate("path/to/your/serviceAccountKey.json")
app = firebase_admin.initialize_app(options = {'projectId': 'predco-app'})

def sendNotification(device_token, title, body):
    message = messaging.Message(
        data={
            "title": title,
            "body": body,
        },
        token=device_token,
    )
    response = messaging.send(message)
    print(response)

sendNotification("fYdLQxCjjr7zkFLv2jk_oc:APA91bGPimTQ_jvRiNN5D1uEZYdALs22u5IAny9qNscie75kbx2OM59lvoGxFqFzBJWQQV0kRBlvvEmbSxsATMZ3exO-Hnb15QU-AruYcRJLTw_BIT0XHBt2XZhnEI4XjlFgcajs-ARJ", "Test", "Test")