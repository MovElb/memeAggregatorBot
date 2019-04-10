import argparse
from flask import Flask, request
from process import process_message

with open('.tokens/verify_token') as v_fd:
    VERIFY_TOKEN = v_fd.read()

app = Flask(__name__)


@app.route('/kek', methods=['GET', 'POST'])
def entry_point():
    if request.method == 'GET':
        return verify_fb_token(request.args)
    else:
        payload = request.get_json()
        for event in payload['entry']:
            messaging = event['messaging']

            for message in messaging:
                if is_user_message(message):
                    user_id = message['sender']['id']
                    text = message['message']['text']

                    process_message(user_id, text)
        return "Message Processed"


def verify_fb_token(req):
    mode = req['hub.mode']
    token = req['hub.verify_token']
    challenge = req['hub.challenge']

    if mode and token:
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print(challenge)
            return challenge


def is_user_message(message):
    """Check if the message is a message from the user"""
    return (message.get('message') and
            message['message'].get('text') and
            not message['message'].get("is_echo"))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=999)
    args = parser.parse_args()

    app.run('0.0.0.0', port=args.port)
