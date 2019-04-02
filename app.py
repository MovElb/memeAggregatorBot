from flask import Flask, request
from pymessenger.bot import Bot
import os


with open('.tokens/access_token') as a_fd, open('.tokens/verify_token') as v_fd:
    ACCESS_TOKEN = a_fd.read()
    VERIFY_TOKEN = v_fd.read()

app = Flask(__name__)
bot = Bot(ACCESS_TOKEN)


@app.route('/', methods=['GET', 'POST'])
def entry_point():
    if request.method == 'GET':
        token_sent = request.args['hub.verify_token']
        return verify_fb_token(token_sent)
    else:
        pass


def verify_fb_token(token_sent):
    if token_sent == VERIFY_TOKEN:
        return request.args['hub.challenge']
    else:
        return 'Invalid verification token'