# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client


# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure
account_sid = 'ACaf4573efc8eab921505cdb82cb258006'
auth_token = '2e8394f33ad52a0c5b98722b1d82583e'
client = Client(account_sid, auth_token)

message = client.messages \
                .create(
                     body="Join Earth's mightiest heroes. Like Kevin Bacon.",
                     from_='+12018907595',
                     to='+18326746410'
                 )

print(message.sid)