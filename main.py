
from config import settings
import discord
from discord.ext import commands
import aiohttp
from lulzurl.easyurl import EasyUrl
import xml.etree.ElementTree as ET

discordSettingBotPrefix = settings['prefix']
discordSettingToken = settings['token']
discordSettingRobotId = settings['robot_id']

botlibreSettingApplicationId = settings['application']
botlibreSettingInstance = settings['instance']

intents = discord.Intents.default()
intents.message_content = True

# discord bot instance
bot = commands.Bot(command_prefix=discordSettingBotPrefix, intents=intents)

# mapping between DiscordId:botlibreId so that each Discord user has their own conversation context
discordUserConvoIdMapping = {}

def aiohttpCallHandlerJson(url: any, message, convo):
    async def wrappedAsyncFunction():
        async with aiohttp.ClientSession() as session:

            xmlChat = ET.Element('chat')
            xmlChat.set("application", f'{botlibreSettingApplicationId}')
            xmlChat.set("instance", f'{botlibreSettingInstance}')            
            if convo:
                xmlChat.set("conversation", f'{convo}')
            xmlMessage = ET.SubElement(xmlChat, 'message')
            xmlMessage.text = f"{message}"
            request = ET.tostring(xmlChat)
            headers = {'Content-Type' : 'application/xml'}

            async with session.post(url, data=request, headers=headers) as resp:
                result = await resp.text()
                status = resp.status
                
        return result, status
    return wrappedAsyncFunction()

async def generateResponseForMessage(message, discord_user_id):

    global discordUserConvoIdMapping

    # if a convo exists for the user, we'll reuse it, otherwise botlibre gives us a new one
    convo_id = discordUserConvoIdMapping.get(discord_user_id)

    # lulzurl allows using HTTP api as functions
    fub = EasyUrl("https://www.botlibre.com", aiohttpCallHandlerJson)
    result, status = await fub.rest.api.chat(message, convo_id)
    
    # report the wrong result back in **bold** format
    status_okay = 200
    if status != status_okay:
        return f"**{result}**"

    xml = ET.fromstring(result)
    
    # extract convo id if it doesn't exist for the Discord user
    if not convo_id:
        new_convo_id = dict(xml.items())['conversation']
        discordUserConvoIdMapping[discord_user_id] = new_convo_id
        
    return next(xml.iter('message')).text

@bot.event
async def on_message(msg: discord.Message):

    # if the bot is the author, just ignore it
    if msg.author == bot.user:
        return

    # if it's a comment and not a message, process it as a message
    context = await bot.get_context(msg)
    if context.command:
        await bot.process_commands(msg)
        return

    # check for any pings and replace all <@discord_user_id> occurences with actual usernames
    betterMessage = str(msg.content)
    bot_ping_detect = False
    for pingedUser in msg.mentions:
        mentionCode = lambda id: f"<@{id}>"
        betterMessage = betterMessage.replace(mentionCode(pingedUser.id), pingedUser.name)
        if pingedUser.id == discordSettingRobotId:
            bot_ping_detect = True

    # if the message was a reply, find who did it reply to
    reply_id = None
    if msg.reference:
        fm = await msg.channel.fetch_message(msg.reference.message_id)
        reply_id = fm.author.id

    # only process further if either the bot was pinged or replied to
    if discordSettingRobotId != reply_id and not bot_ping_detect:
        return
    
    # go to botlibre API and generate a response
    response = await generateResponseForMessage(msg.content, msg.author.id)

    # only send if it makes sense to
    makesSenseToSend = lambda msg: msg and msg != ""
    if makesSenseToSend(response):
        await msg.reply(response)

bot.run(discordSettingToken)