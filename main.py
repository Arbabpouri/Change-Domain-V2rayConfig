# in the name of god
from base64 import b64decode, b64encode
from json import loads
import logging
from os import system
from re import findall

try:

    from telethon import TelegramClient, Button
    from telethon.events import NewMessage
    from pythonping import ping

except ModuleNotFoundError:

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

Responsive, user_check = {}, set({})
# ------------------------------------------------------------------------------------------------------------------------------------------

# ------------------------------------------------- tools --------------------------------------------

# check vmess:// config
async def check_vmess(server) -> list:

    try:
        data = eval(b64decode(str(server).replace("vmess://", '')).decode())
    except:
        return [False]

    if isinstance(data, dict):
        if "host" in list(data.keys()):
            return [True, data]
        else:
            return [False]


# encode data and change to v2ray config
async def encode_vmess(data) -> list:
    for i in config['hosts']:
        if data['host'] in i:
            num = i.index(data['host'])
            data['host'] = i[0 if num == 1 else 1]
            ping = await get_ping(data['host'])
            server = b64encode(str(data).encode()).decode()
            return [True, server, ping]
    else:
        return [False]


# check vless config
async def check_and_change_host_vless(server:str) -> list:
    check = findall(r"host=([^&]+)", server)
    if check != []:

        for i in config['hosts']:
            
            if check[0] in i:

                num = i.index(check[0])
                host = i[0 if num == 1 else 1]
                data = server.replace(check[0], host)
                ping = await get_ping(check[0])
                return [True, data, ping]
            
        else:
            return [False]
        
    else:
        return [False]


# get server ping
async def get_ping(host):
    try:
        getPing = ping(str(host), verbose= False).rtt_avg_ms
        return getPing
    except:
        return 2000.0

# --------------------------------------------------- Bot -----------------------------------------------

# start menu
@client.on(NewMessage(pattern= '/start', func= lambda e: e.is_private and str(e.sender_id) not in list(Responsive.keys())))
async def start(event):
    button = [
        [Button.text('💢 دریافت سرور 💢', resize= True, single_use= True)],
        [Button.text('👨‍💻 پشتیبانی 👨‍💻', resize= True, single_use= False)]
    ]
    
    await client.send_message(event.sender_id, f"🤙 سلام {f'[{event.chat.first_name}](tg://user?id={str(event.sender_id)})'} عزیز به ربات خوش اومدی 😍\n☄️ از منوی زیر انتخاب کن 😄""", buttons= button)
    button = None


# get server and check and change host
@client.on(NewMessage(pattern= '💢 دریافت سرور 💢', func= lambda e: e.is_private and str(e.sender_id) not in list(Responsive.keys())))
async def get(event):
    await client.send_message(event.sender_id, "🔺 خب به بخش دریافت سرور خوش امدید , لطفا سرور خود را که از کار افتاده را برای ما ارسال کنید 💢\n⭕️ درصورت بروز مشکل میتوانید با پشتیبانی در میان بگذارید ✔️", buttons= [[Button.text('❌ کنسل کردن ❌', resize= True, single_use= True)]])
    Responsive[str(event.sender_id)] = str(event.message.message)


@client.on(NewMessage(func= lambda e: e.is_private and str(e.sender_id) in list(Responsive.keys())))
async def get_server(event):

    if str(event.message.message) == Responsive[str(event.sender_id)] or str(event.message.message) == "❌ کنسل کردن ❌": return False
    
    elif str(event.message.message).lower().startswith("vmess://"):
        if event.sender_id in user_check:
            return False
        
        user_check.add(event.sender_id)
        check = await check_vmess(event.message.message)

        if check[0] == True:
            Message = await event.reply("⏳ کمی صبر کنید", buttons= [[Button.text('❌ کنسل کردن ❌', resize= True, single_use= True)]])
            server = await encode_vmess(check[1])
            
            if server[0] == True:
                await Message.delete()
                await event.reply(f'✅ سرور شما اماده است\n💡 روی ان کلیک کنید تا کپی شود  : \n\n\n<code>vmess://{server[1]}</code>\n\n\n🌐 - وضعیت سرور = {server[2] if server[2] < 2000.0 else "❗️ OFF"}\n\n\n اگر سرور دیگری دارید ارسال کنید , در غیر این صورت روی دکمه کنسل کردن کلیک کنید',buttons= [[Button.text('❌ کنسل کردن ❌', resize= True, single_use= True)]], parse_mode='html')
                server = 0
                check = 0
                if event.sender_id in user_check: user_check.remove(event.sender_id)
            
            else:
                check = 0
                server = 0
                await client.send_message(event.sender_id, "❌ سرور ارسالی اشتباه است ❌\n✅ لطفا دقت کنید", buttons= [[Button.text('❌ کنسل کردن ❌', resize= True, single_use= True)]])
                if event.sender_id in user_check: user_check.remove(event.sender_id)
        
        else:
            check = 0
            await client.send_message(event.sender_id, "❌ سرور ارسالی اشتباه است ❌\n✅ لطفا دقت کنید")
            if event.sender_id in user_check: user_check.remove(event.sender_id)

    elif str(event.message.message).lower().startswith("vless://"):
        if event.sender_id in user_check:
        
            return False
        Message = await event.reply("⏳ کمی صبر کنید", buttons= [[Button.text('❌ کنسل کردن ❌', resize= True, single_use= True)]])
        user_check.add(event.sender_id)
        check = await check_and_change_host_vless(str(event.message.message))
        
        if check[0] == True:
            await Message.delete()
            await event.reply(f'✅ سرور شما اماده است\n💡 روی ان کلیک کنید تا کپی شود  : \n\n\n<code>{check[1]}</code>\n\n\n🌐 - وضعیت سرور = {check[2] if check[2] < 2000.0 else "❗️ OFF"}\n\n\n اگر سرور دیگری دارید ارسال کنید , در غیر این صورت روی دکمه کنسل کردن کلیک کنید',buttons= [[Button.text('❌ کنسل کردن ❌', resize= True, single_use= True)]], parse_mode='html')
            check = 0
            if event.sender_id in user_check: user_check.remove(event.sender_id)

        else:
            check = 0
            await client.send_message(event.sender_id, "❌ سرور ارسالی اشتباه است ❌\n✅ لطفا دقت کنید")
            if event.sender_id in user_check: user_check.remove(event.sender_id)

    else:
        await client.send_message(event.sender_id, "❌ سرور ارسالی اشتباه است ❌\n✅ لطفا دقت کنید")
        if event.sender_id in user_check: user_check.remove(event.sender_id)
        

# send supporter id
@client.on(NewMessage(pattern= '👨‍💻 پشتیبانی 👨‍💻', func= lambda e: e.is_private and str(e.sender_id) not in list(Responsive.keys())))      
async def support(event):
    button = [
        [Button.url('📞 پشتیبانی', f'https://t.me/{config["AdminUsername"]}')]
    ]
    await client.send_message(event.sender_id, "⁉️ سوال خود را در قالب یک متن به پشتیبانی ارسال کنید\n‼️ روی دکمه پشتیبانی زیر کلیک کنید تا هدایت شوید", buttons= button)


@client.on(NewMessage(pattern= '❌ کنسل کردن ❌', func= lambda e: e.is_private))
async def cancel(event):
    if str(event.sender_id) in list(Responsive.keys()): del Responsive[str(event.sender_id)]
    if event.sender_id in user_check: user_check.remove(event.sender_id)
    await start(event)


# --------------------------------------------------- run -----------------------------------------------


if __name__ == "__main__":
    print('bot is online')
    client.run_until_disconnected() # run
