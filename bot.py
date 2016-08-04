import _thread
import asyncio
import discord
import dota2api
import os

from flask import Flask
app = Flask(__name__)

api = dota2api.Initialise("B57B59DCAED83EF462AC75019B4F0804")
client = discord.Client()


def get_games():
    resp = api.get_live_league_games()
    ret = []
    for game in resp['games']:
        if game['league_id'] == 4664:
            ret.append(game)
    return ret


def describe(game, time=False):

    radiant, dire = "Radiant", "Dire"
    try:
        radiant = game['radiant_team']['team_name']
    except:
        pass
    try:
        dire = game['dire_team']['team_name']
    except:
        pass

    num = game.get('game_number', 1)

    if time:
        time = int(game['scoreboard']['duration']) // 60
        return '{} vs {} Game {} ({} mins)'.format(radiant, dire, num, time)
    else:
        return '{} vs {} Game {}'.format(radiant, dire, num)


def get_winner(mid):
    i = api.get_match_details(match_id=mid)

    if i['radiant_win']:
        if 'radiant_team' in i:
            return i['radiant_team']['team_name']
        else:
            return "Radiant"
    else:
        if 'dire_team' in i:
            return i['radiant_team']['team_name']
        else:
            return "Dire"


@client.event
async def on_message(message):
    if message.content.startswith('!live'):
        await client.send_message(message.channel, describe_live_games())


async def update_tracker(last_known):

    current = get_games()
    msg = []

    for i in range(len(last_known)):
        mid = last_known[i]['match_id']
        if mid not in [x['match_id'] for x in current]:
            d = describe(last_known[i])
            victor = get_winner(mid)
            msg.append("{} has finished. {} victorious!".format(d, victor))
            del last_known[i]

    for i in current:
        d = describe(i)
        mid = i['match_id']
        if mid not in [x['match_id'] for x in last_known]:
            msg.append("{} has started!".format(d))
            last_known.append(i)

    if msg:
        client.send_message(client.get_server("195955299482337281"),
                            "\n".join(msg))

    await asyncio.sleep(60)
    await update_tracker(last_known)


@client.event
async def on_ready():
    await update_tracker([])
    # loop = asyncio.get_event_loop()
    # loop.call_soon(update_tracker, [], loop)


@app.route('/')
def describe_live_games():
    games = get_games()
    if games:
        return "\n".join([describe(x, True) for x in get_games()])
    else:
        return "No games in progress."

if __name__ == "__main__":
    _thread.start_new_thread(app.run, (),
                             {"port": os.environ.get('PORT', 5000)})
    # print("test")
    client.run('MjEwNDQwMTk1NDU4MzM0NzIw.CoO3oQ.aLq9tFdUv8QIO0l26vjy8PB8JMM')
