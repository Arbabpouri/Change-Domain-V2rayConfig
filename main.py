# in the name of god
from base64 import b64decode, b64encode
from json import loads
import logging
from os import system
try:
    from telethon import TelegramClient, Button
    from telethon.tl.types import PeerUser
    from telethon.events import NewMessage
    from pythonping import ping
except ImportError:
    system('pip3 install telethon')
    system('pip3 install pythonping')
    print('library installed')
except Exception as ex:
    print('etesal internet ra barresi konid ya be surat dasti ketabkhane "telethon" va "pythonping" ra nasb konid (pip install telethon/pythonping)')

logging.basicConfig(filename="log.txt", filemode="a",format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    config = loads(open('./config/config.json', 'r').read())

except FileNotFoundError:
    print('./config/config.json , not found')
    exit()

except Exception as ex:
    print(ex)
    exit()

# client
client = TelegramClient(
    session= "bot",
    api_id= config["ApiID"],
    api_hash= config["ApiHash"]
).start(bot_token= config["Token"])
Responsive, user_check = [], []
# ------------------------------------------------------------------------------------------------------------------------------------------
# check vmess:// or ...
async def check_server(server):
    for i in config["server_start_with"]:
        if str(server).startswith(str(i)):
            try:
                data = eval(b64decode(str(server).replace(str(i), '')).decode())
            except:
                return False

            if isinstance(data, dict):
                check_key = ['add', 'aid', 'alpn', 'host', 'id', 'net', 'path', 'port', 'ps', 'scy', 'sni', 'tls', 'type', 'v']
                if list(data.keys()).sort() == check_key.sort():
                    return [True, data, i]
                else:
                    return False
    else:
        return False

# encode data and change to v2ray config
async def encoder(data):
    for i in config['hosts']:
        if data['host'] in i:
            num = i.index(data['host'])
            data['host'] = i[0 if num == 1 else 1]
            Ping = await get_ping(data['host'])
            server = b64encode(str(data).encode()).decode()
            return [True, server, Ping]
    else:
        return False

# get server ping
async def get_ping(host):
    try:
        getPing = ping(str(host), verbose= False).rtt_avg_ms
        return getPing
    except:
        return 2000.0

# start menu
@client.on(NewMessage(pattern= '/start', func= lambda e: e.is_private and e.sender_id not in Responsive))
async def start(event):
    button = [
        [Button.text('💢 دریافت سرور 💢', resize= True, single_use= True)],
        [Button.text('👨‍💻 پشتیبانی 👨‍💻', resize= True, single_use= False)]
    ]
    
    await client.send_message(event.sender_id, f"🤙 سلام {f'[{event.chat.first_name}](tg://user?id={str(event.sender_id)})'} عزیز به ربات خوش اومدی 😍\n☄️ از منوی زیر انتخاب کن 😄""", buttons= button)
    button = None

# get server and check and change host
@client.on(NewMessage(pattern= '💢 دریافت سرور 💢', func= lambda e: e.is_private and e.sender_id not in Responsive))
async def get(event):
    button = [[Button.text('❌ کنسل کردن ❌', resize= True, single_use= True)]]
    await client.send_message(event.sender_id, "🔺 خب به بخش دریافت سرور خوش امدید , لطفا سرور خود را که از کار افتاده را برای ما ارسال کنید 💢\n⭕️ درصورت بروز مشکل میتوانید با پشتیبانی در میان بگذارید ✔️", buttons= button)
    Responsive.append(event.sender_id)
    @client.on(NewMessage(func= lambda e: e.is_private and e.sender_id in Responsive))
    async def get_server(event2):
        if event.message.message == event2.message.message or event.sender_id != event2.sender_id:
            return False
        elif event2.message.message == '❌ کنسل کردن ❌':
            await start(event2)
            Responsive.remove(event2.sender_id)
            client.remove_event_handler(get_server)
            if event2.sender_id in user_check:
                user_check.remove(event2.sender_id)
        else:
            if event2.sender_id in user_check:
                return False
            user_check.append(event2.sender_id)
            check = await check_server(event2.message.message)
            if isinstance(check, list) and len(check) == 3 and check[0] == True:
                Message = await event2.reply("⏳ کمی صبر کنید", buttons= button)
                server = await encoder(check[1])
                if isinstance(server, list) and len(server) == 3 and server[0] == True:
                    await Message.delete()
                    await event2.reply(f'✅ سرور شما اماده است\n💡 روی ان کلیک کنید تا کپی شود  : \n\n\n<code>{check[2]}{server[1]}</code>\n\n\n🌐 - وضعیت سرور = {server[2] if server[2] < 2000.0 else "❗️ OFF"}\n\n\n اگر سرور دیگری دارید ارسال کنید , در غیر این صورت روی دکمه کنسل کردن کلیک کنید',buttons= button, parse_mode='html')
                    user_check.remove(event2.sender_id)
                else:
                    await client.send_message(event2.sender_id, "❌ سرور ارسالی اشتباه است ❌\n✅ لطفا دقت کنید", buttons= button)
                    user_check.remove(event2.sender_id)
            else:
                await client.send_message(event2.sender_id, "❌ سرور ارسالی اشتباه است ❌\n✅ لطفا دقت کنید")
                user_check.remove(event2.sender_id)

# send supporter id
@client.on(NewMessage(pattern= '👨‍💻 پشتیبانی 👨‍💻', func= lambda e: e.is_private and e.sender_id not in Responsive))      
async def support(event):
    button = [
        [Button.url('📞 پشتیبانی', f'https://t.me/{config["AdminUsername"]}')]
    ]
    await client.send_message(event.sender_id, "⁉️ سوال خود را در قالب یک متن به پشتیبانی ارسال کنید\n‼️ روی دکمه پشتیبانی زیر کلیک کنید تا هدایت شوید", buttons= button)

print('bot is online')
client.run_until_disconnected() # run