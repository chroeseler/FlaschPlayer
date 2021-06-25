import http.client, urllib
import os

token = os.environ["PUSHOVER_TOKEN"]
user = os.environ["PUSHOVER_USER"]

def send(message):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
      urllib.parse.urlencode({
        "token": f"{token}",
        "user": f"{user}",
        "message": message,
      }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()
