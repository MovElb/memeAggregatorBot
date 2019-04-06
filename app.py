from flask import Flask, request
from pymessenger.bot import Bot
from state_manager import StateManager
import re
import requests


with open('.tokens/access_token') as a_fd, open('.tokens/verify_token') as v_fd:
    ACCESS_TOKEN = a_fd.read()
    VERIFY_TOKEN = v_fd.read()

app = Flask(__name__)
bot = Bot(ACCESS_TOKEN)
state_manager = StateManager()


@app.route('/kek', methods=['GET', 'POST'])
def entry_point():
    if request.method == 'GET':
        token_sent = request.args['hub.verify_token']
        return verify_fb_token(token_sent)
    else:
        payload = request.get_json()
        for event in payload['entry']:
            messaging = event['messaging']

            for message in messaging:
                if is_user_message(message):
                    text = message['message']['text']
                    user_id = message['sender']['id']

                    user_state = state_manager.get_state(user_id)
                    if user_state != StateManager.S_NULL:
                        handle_command(text, user_id)
                    elif user_state == StateManager.S_WAIT_URL_SUB:
                        state_manager.set_state(user_id)
                    elif user_state == StateManager.S_WAIT_URL_UNSUB:
                        state_manager.set_state(user_id)

        return "Message Processed"


def verify_fb_token(token_sent):
    if token_sent == VERIFY_TOKEN:
        return request.args['hub.challenge']
    else:
        return 'Invalid verification token'


def is_user_message(message):
    """Check if the message is a message from the user"""
    return (message.get('message') and
            message['message'].get('text') and
            not message['message'].get("is_echo"))


def handle_command(text, user_id):
    if not re.fullmatch(r'(.*\s)?/(help|random|subscribe|unsubscribe)(\s.*)?', text):
        bot.send_text_message(user_id, "I don't understand you. Use /help to get the list of commands.")
        return

    command = re.compile(r'/(help|random|subscribe|unsubscribe)').group()
    if command == '/help':
        bot.send_text_message(
            user_id,
            '''List of all commands
            /help - Get list of all comands
            /random - Get random meme from bash.im
            /subscribe - Subscribe meme source
            /unsubscribe - Unsubscribe meme source
            '''
        )

    if command == '/random':
        send_random_meme(user_id)

    if command == '/subscribe':
        bot.send_text_message(
            user_id,
            '''Give me source URL. I support the following sources:
            reddit.com
            '''
        )
        state_manager.set_state(user_id, state_manager.S_WAIT_URL_UNSUB)

    if command == '/unsubscribe':
        pass


def send_random_meme(user_id):
    r = requests.get('https://www.reddit.com/r/memes/random/.json', headers={'User-agent': 'random meme'})
    url = r.json()[0]['data']['children'][0]['data']['url']
    text = r.json()[0]['data']['children'][0]['data']['selftext']

    if url[-4:] == '.jpg':
        bot.send_image_url(user_id, url)
    else:
        bot.send_text_message(user_id, text | url)


if __name__ == '__main__':
    app.run(port=1234)
