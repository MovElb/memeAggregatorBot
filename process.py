import json
from pymessenger.bot import Bot
import re
from redis.sentinel import Sentinel
import requests
from state_manager import StateManager
import urllib.parse

with open('.tokens/access_token') as a_fd, open('.tokens/redis_config.json') as r_fd:
    ACCESS_TOKEN = a_fd.read()
    REDIS_CONFIG = json.load(r_fd)


bot = Bot(ACCESS_TOKEN)
state_manager = StateManager()

URLS_KEY = REDIS_CONFIG['urls_key']
sentinel = Sentinel([(REDIS_CONFIG['host'], 26379)], socket_timeout=0.1)
master = sentinel.master_for(REDIS_CONFIG['service_name'], password=REDIS_CONFIG['password'])


def process_message(user_id, text):
    print(text, user_id)
    user_state = state_manager.get_state(user_id)
    print('user_state', user_state)
    if user_state == StateManager.S_NULL:
        handle_command(text, user_id)
    elif user_state == StateManager.S_WAIT_URL_SUB:
        url = verify_url(text)
        if url:
            master.sadd(URLS_KEY, url)
            master.sadd(user_id, url)
            master.sadd(url, user_id)
            bot.send_text_message(user_id, 'Successfully subscribed {}'.format(url))
        else:
            bot.send_text_message(user_id, 'Link is not valid or not supported')

        state_manager.set_state(user_id)
    elif user_state == StateManager.S_WAIT_URL_UNSUB:
        url = verify_url(text, goto_url=False)
        if master.srem(user_id, url):
            master.srem(url, user_id)
            bot.send_text_message(user_id, 'Successfully unsubscribed')
        else:
            bot.send_text_message(user_id, 'Link is not valid or you were not subscribed')

        state_manager.set_state(user_id)


def handle_command(text, user_id):
    if not re.fullmatch(r'(.*\s)?/(help|random|subscribe|unsubscribe|subscriptions)(\s.*)?', text):
        bot.send_text_message(user_id, "I don't understand you. Use /help to get the list of commands.")
        return
    print('passed')

    command = re.search(r'/(help|random|subscribe|unsubscribe|subscriptions)', text).group()
    print('command')
    if command == '/help':
        bot.send_text_message(
            user_id,
            '''List of all commands:
            /help - Get list of all comands
            /random - Get random meme from reddit.com
            /subscribe - Subscribe meme source
            /unsubscribe - Unsubscribe meme source
            /subscriptions - List of your subscriptions
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
        state_manager.set_state(user_id, state_manager.S_WAIT_URL_SUB)

    if command == '/unsubscribe':
        bot.send_text_message(
            user_id,
            '''What source do you want to unsubscribe?
            Full list of your subscriptions you can get by /subscriptions command.
            '''
        )
        state_manager.set_state(user_id, state_manager.S_WAIT_URL_UNSUB)

    if command == '/subscriptions':
        subscriptions = master.sscan(user_id)[1]
        cnt = len(subscriptions)
        subscriptions = '▪️ ' + '️\n▪️ '.join(list(map(bytes.decode, subscriptions)))

        null = 'You don\'t have any subscriptions'
        bot.send_text_message(user_id, subscriptions if cnt else null)


def send_random_meme(user_id):
    r = requests.get('https://www.reddit.com/r/memes/random/.json', headers={'User-agent': 'random meme'})
    url = r.json()[0]['data']['children'][0]['data']['url']
    text = r.json()[0]['data']['children'][0]['data']['selftext']

    if url[-4:] == '.jpg':
        bot.send_image_url(user_id, url)
    else:
        bot.send_text_message(user_id, text | url)


def verify_url(url, goto_url=True):
    p = urllib.parse.urlsplit(url)

    cond = (p.netloc == 'reddit.com' and re.fullmatch(r'/r/.+.*', p.path)) or \
           (p.netloc == '' and re.fullmatch(r'(www.)?reddit.com/r/.+.*', p.path))
    if not cond:
        return ''

    url = urllib.parse.urlunparse(('https', p.netloc, p.path, '', '', '')).replace('///', '//')
    if not goto_url:
        return url

    try:
        r = requests.get(
            urllib.parse.urljoin(url, 'random/.json?limit=1'), headers={'User-agent': 'random meme'}
        ).json()
        url = url if r['data']['dist'] else ''
    except:
        return ''

    return url
