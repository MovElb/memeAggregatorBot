import aioredis
import aiohttp
import argparse
import asyncio
from asyncbot import Bot
import json

with open('.tokens/access_token') as ac_fd, \
     open('.tokens/redis_config.json') as rs_fd, \
     open('.tokens/reddit_oauth.json') as ro_fd:
    ACCESS_TOKEN = ac_fd.read()
    REDIS_CONFIG = json.load(rs_fd)
    REDDIT_OAUTH = json.load(ro_fd)

URLS_KEY = REDIS_CONFIG['urls_key']


async def schedule(delay):
    bot = Bot(ACCESS_TOKEN)

    session = aiohttp.ClientSession()

    sentinel = await aioredis.create_sentinel([(REDIS_CONFIG['host'], 26379)], password=REDIS_CONFIG['password'])
    master = sentinel.master_for(REDIS_CONFIG['service_name'])

    while True:
        await update_subscriptions(bot, master, session)
        await asyncio.sleep(delay)


async def update_subscriptions(bot, master, session):
    urls_iter = master.isscan(URLS_KEY)
    urls_num = await master.scard(URLS_KEY)
    BATCH_SIZE = 10

    for i in range((urls_num - 1) // BATCH_SIZE + 1):
        tasks = []
        for j in range(min(BATCH_SIZE, urls_num - i * BATCH_SIZE)):
            url = await urls_iter.__anext__()
            tasks.append(process_url(url.decode(), session, master, bot))
        await asyncio.gather(*tasks)


async def process_url(url, session, master, bot):
    subscribers_num = await master.scard(url)
    if not subscribers_num:
        return

    url_get = url + '/new/.json?limit=1'
    async with session.get(url_get, params=REDDIT_OAUTH, headers={'user-agent': 'meme-aggregator-bot'}) as resp:
        post_data = (await resp.json())['data']['children'][0]['data']

    post = {
        'title': post_data['title'],
        'text': post_data['selftext'],
        'permalink': post_data['permalink'],
        'url': post_data['url'],
        'is_img': post_data['url'][-4:] == '.jpg'
    }

    latest_post = await master.get(url + '_latest')
    if latest_post is not None and post['permalink'] == json.loads(latest_post.decode())['permalink']:
        return
    await master.set(url + '_latest', json.dumps(post))

    subscribers_iter = master.isscan(url)
    if post['is_img']:
        await send_post(subscribers_iter, subscribers_num, bot.send_image_url, post['url'])
    else:
        await send_post(subscribers_iter, subscribers_num, bot.send_text_message, post['title'] + '\n' + post['text'])


async def send_post(sub_iter, sub_num, send_function, post):
    BATCH_SIZE = 10
    for i in range((sub_num - 1) // BATCH_SIZE + 1):
        tasks = []
        for j in range(min(BATCH_SIZE, sub_num - i * BATCH_SIZE)):
            user_id = (await sub_iter.__anext__()).decode()
            tasks.append(send_function(user_id, post))
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--delay', type=int, default=5, help='How often in seconds sources are updated')
    args = parser.parse_args()

    asyncio.run(schedule(args.delay))
