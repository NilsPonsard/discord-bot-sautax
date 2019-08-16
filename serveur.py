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

# help page
color = discord.Colour.from_rgb(255, 215, 0)
#(255, 215, 0)

embededHelp = discord.Embed(colour=color,
                            title="**Aide**", description="préfixe : {} \n**commandes**:".format(prefix))
with open("help.txt", "r") as file:
    for l in file.readlines():
        t = l.split(" : ")
        if len(t) > 1:
            embededHelp.add_field(name=t[0], value=t[1], inline=False)
embededHelp.set_author(name="créé par sautax#9170",
                       url="https://github.com/sautax")


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
            trusted = False
            for id in trustedIDs:
                if message.author.id == id:
                    trusted = True
            if trusted:

                await message.channel.send("restarting ...")
                activity = discord.Activity()
                activity.type = discord.ActivityType.playing
                activity.name = "redémarrer...".format(prefix)
                await client.change_presence(
                    activity=activity, status=discord.Status.dnd)
                sys.exit(0)
            else:
                await message.channel.send("vous n'avez pas la permission")
        (commande, arguments) = parse(message)
        if commande == "hello":
            await message.channel.send('Hello!')

        # executer du python depuis discord
        if commande == "eval":
            await message.channel.send(bot_eval(message))

        if commande == "exec":
            await message.channel.send(bot_exec(message))

        if commande == "help":
            await message.channel.send(content=None, embed=embededHelp)

        if commande == "lol":  # sous catégorie lol

            if arguments[0] == "rotation":  # rotation des champions gratuits
                sent_message = await message.channel.send(content="processing...")
                (content, embed, file) = lol.champ_rotation()
                await message.channel.send(content=content, embed=embed, file=file)
                await sent_message.delete()

            elif len(arguments) >= 1:

                if len(arguments) >= 2:

                    if arguments[0] == "skins":
                        nom = " ".join(arguments[1:])
                        (content, list_embed) = lol.champ_skins(
                            nom)
                        for embed in list_embed:
                            await message.channel.send(content=content, embed=embed)

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
activity.type = discord.ActivityType.listening
activity.name = "quelque chose | {}help".format(prefix)
client.activity = activity
client.run(secret)
