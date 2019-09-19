import urllib3
import json


class SlackSender:
    def __init__(self, token):
        self.token = token
        self.http = urllib3.PoolManager()

    def send_message(self, message, color='#FF69B4', channel='pl-foosball-hacking'):
        data = {
            'channel': channel,
            'attachments': [
                {
                    'color': color,
                    'text': message
                }
            ]
        }
        encoded_data = json.dumps(data).encode('utf-8')
        headers = {
            'Content-Type': 'application/json'
        }
        self.http.request(
            'POST',
            f'https://sumologic.slack.com/services/hooks/jenkins-ci?token={self.token}',
            body=encoded_data,
            headers=headers
        )
