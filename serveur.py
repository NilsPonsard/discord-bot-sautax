# tests pour exec
import sys
import io
from commandes import *
import lol
# discord.py lib
import discord

trustedIDs = []
with open("trustedIDs", "r") as file:
    lines = file.readlines()
    for id in lines:
        trustedIDs.append(int(id))

prefix = "$"
secret = ""

# get token from the secret file
with open("secret", "r") as file:
    secret = file.readline()


def bot_exec(message):  # fonction exec du bot (programme)
    trusted = False
    for id in trustedIDs:
        if message.author.id == id:
            trusted = True

    if trusted:
        out = ""

        # somewhere to store output
        pout = io.StringIO()

        # set stdout to our StringIO instance
        sys.stdout = pout
        try:
            exec(message.content[6:])
            out = pout.getvalue()
        except:
            out = "une erreur est survenue"

        sys.stdout = sys.__stdout__
        return out

    else:
        return "vous n'avez pas la permission"


def bot_eval(message):  # fonction eval du bot (expression)
    trusted = False
    for id in trustedIDs:
        if message.author.id == id:
            trusted = True
    out = ""
    if trusted:
        try:
            out = eval(message.content[5:])
        except:
            out = "une erreur est survenue"
        return out
    else:
        return "vous n'avez pas la permission"


def parse(message):
    content = message.content[len(prefix):]
    content = content.split(" ")
    if len(content) > 1:
        return content[0], content[1:]
    else:
        return content[0], [""]

    # create client
client = discord.Client()

# debug : successfully started bot
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


# analyse messages
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith(prefix):
        # redémarre le bot en tuant la tâche : fonction critique
        if message.content.startswith('$restart'):
            await message.channel.send("restarting ...")
            sys.exit(0)
        (commande, arguments) = parse(message)
        if commande == "hello":
            await message.channel.send('Hello!')

        # executer du python depuis discord
        if commande == "eval":
            await message.channel.send(bot_eval(message))
        if commande == "exec":
            await message.channel.send(bot_exec(message))
        if commande == "lol":
            if arguments[0] == "rotation":
                await message.channel.send(lol.champ_rotation())
            elif len(arguments) >= 1:

                if len(arguments) >= 2:
                    if arguments[0] == "skins":

                        nom = " ".join(arguments[1:])
                        (content, list_embed) = lol.champ_skins(
                            nom)
                        for embed in list_embed:
                            await message.channel.send(content=content, embed=embed)
                        # await message.channel.send(content="{} skins".format(len(list_embed)), embed=None)

                    elif arguments[0] == "lore":

                        nom = " ".join(arguments[1:])
                        (content, embed) = lol.champ_lore(
                            nom)
                        await message.channel.send(content=content, embed=embed)
                    else:
                        await message.channel.send("commande inconnue")
                else:
                    await message.channel.send("commande inconnue")
            else:
                await message.channel.send("commande inconnue")
        if commande == "invite":
            await message.channel.send("inviter ce bot : \n https://discordapp.com/oauth2/authorize?client_id=607969795798728716&scope=bot&permissions=8")
        if commande == "ping":
            await message.channel.send("ping : `{}`".format(client.latency))
activity = discord.Activity()
activity.url = "google.com"
activity.name = "test"
client.activity = activity
# client.activity(discord.Activity(url="google.com"))
# start bot
client.run(secret)
