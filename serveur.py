import sys
import io
import os
import asyncio
import importlib
import time
import lol  # api de riot, infos sur lol
import image  # création d'images
# discord.py lib
import discord

"""
où stocker les clefs d'api ?
league api RGAPI-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx: fichier lolKey
api discord : fichier secret
"""

"""
les ID de personnes de confiance sont stockés dans le fichier trustedIDs
"""
if not os.path.isfile("secret"):  # vérifier si le fichier existe
    with open("secret", "w") as file:
        file.write("put your discord bot token here")
        file.close()
    print("you need to define the discord api Key")

if not os.path.isfile("trustedIDs"):  # vérifier si le fichier existe
    with open("trustedIDs", "w") as file:
        file.write("put your discordUser id here (access to admin commands)")
        file.close()
    print("you need to define the admin User Id")


trustedIDs = []
with open("trustedIDs", "r") as file:
    lines = file.readlines()
    for id in lines:
        try:
            trustedIDs.append(int(id))
        except:
            print("you need to define the admin User Id")

prefix = "$"
secret = ""

# get token from the secret file
with open("secret", "r") as file:
    secret = file.readline().replace("\n", "")

# help page
color = discord.Colour.from_rgb(255, 215, 0)
# (255, 215, 0)

embededHelp = discord.Embed(colour=color,
                            title="**Aide**", description="préfixe : {} \n**commandes**:".format(prefix))
with open("help.txt", "r") as file:
    for l in file.readlines():
        t = l.split(" : ")
        if len(t) > 1:
            embededHelp.add_field(name=t[0], value=t[1], inline=False)
embededHelp.set_author(name="créé par sautax#9170",
                       url="https://github.com/sautax")


def isTrusted(message):
    trusted = False
    for id in trustedIDs:
        if message.author.id == id:
            trusted = True
            break
    return trusted


def bot_exec(message):  # fonction exec du bot (programme)
    trusted = isTrusted(message)
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
    trusted = isTrusted(message)
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
    content.replace("\n", " ")
    content = content.split(" ")
    if len(content) > 1:
        return content[0], content[1:]
    else:
        return content[0], [""]


# create client
client = discord.Client()


async def restart(message):
    m = await message.channel.send("restarting :hourglass_flowing_sand: ")
    activity = discord.Activity()
    activity.type = discord.ActivityType.playing
    activity.name = "Redémarrer...".format(prefix)
    await client.change_presence(
        activity=activity, status=discord.Status.dnd)
    with open("lastchannel", "w") as file:
        file.write(str(m.channel.id))
    print("restarting")
    sys.exit(0)


# debug : successfully started bot

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    if os.path.isfile("lastchannel"):  # vérifier si le fichier existe
        with open("lastchannel", "r") as file:
            content = file.readline()
            if len(content) > 5:  # vérifier si il y a bien un ID
                channel = client.get_channel(int(content))
                async for message in channel.history(limit=200):
                    if message.author == client.user:
                        await message.edit(content="Sucessfully restarted :white_check_mark:")
                        print("sucessfully restarted and sent the message")
                        break
    with open("lastchannel", "w") as file:
        file.write(" ")
    print("erased the content of the file")


# analyse messages
@client.event
async def on_message(message):
    start = time.time()
    if message.author == client.user:
        return
    if message.content.startswith(prefix):
        # redémarre le bot en tuant la tâche : fonction critique
        if message.content.startswith('$restart'):
            trusted = isTrusted(message)
            if trusted:
                await restart(message)
            else:
                await message.channel.send("vous n'avez pas la permission")
        (commande, arguments) = parse(message)
        if commande == "reload":
            trusted = isTrusted(message)
            if trusted:
                if arguments[0] == "":
                    await restart(message)
                try:

                    if arguments[0] == "lol":
                        m = await message.channel.send("Reloading module lol :hourglass_flowing_sand: ")
                        importlib.reload(lol)
                    elif arguments[0] == "image":
                        m = await message.channel.send("Reloading module image :hourglass_flowing_sand: ")
                        print("terminating quee")
                        image.mandelbrot_in_q.put(None)
                        image.mandelbrot_out_q.put(None)
                        print("queue terminated")
                        image.mandelbrot_t.join()
                        importlib.reload(image)
                    else:
                        await restart(message)
                    await m.edit(content="Module reloaded :white_check_mark:")

                except:
                    await message.channel.send("erreur")
                    await restart(message)

            else:
                await message.channel.send("vous n'avez pas la permission")

        if commande == "hello":
            await message.channel.send('Hello!')

        # executer du python depuis discord
        if commande == "eval":
            await message.channel.send(bot_eval(message))

        if commande == "say":
            await message.channel.send(" ".join(arguments))
            await message.delete()
        if commande == "image":
            if len(arguments) > 0:

                if len(arguments) > 1:
                    if arguments[0] == "mandelbrot":
                        m = await message.channel.send("processing ...")

                        await image.mandelbrot(int(arguments[1]), message, m, client)

            else:
                await message.channel.send("commande inconnue")
        if commande == "op":
            trusted = isTrusted(message)
            if trusted:
                mentions = message.mentions
                with open("trustedIDs", "a") as file:  # appending, ajout à la fin du fichier
                    for user in mentions:
                        m = await message.channel.send("ajoute "+user.name+" aux administrateurs")
                        already_added = False
                        for i in trustedIDs:
                            if user.id == i:
                                already_added = True
                        if already_added == False:
                            file.write("\n"+str(user.id))
                            trustedIDs.append(user.id)
                        await m.edit(content=user.name +
                                     " est maintenant administrateur")

            else:
                await message.channel.send("vous n'avez pas la permission")

        if commande == "exec":
            await message.channel.send(bot_exec(message))

        if commande == "help":
            await message.channel.send(content=None, embed=embededHelp)

        if commande == "lol":  # sous catégorie lol

            if arguments[0] == "rotation":  # rotation des champions gratuits
                sent_message = await message.channel.send(content="processing...")
                await lol.champ_rotation(message, sent_message, client)

            elif len(arguments) >= 1:

                if len(arguments) >= 2:
                    if arguments[0] == "stats" or arguments[0] == "stat" or arguments[0] == "player":
                        player = "%20".join(arguments[1:])
                        (content, embed) = lol.player_infos(player)
                        await message.channel.send(content=content, embed=embed)

                    elif arguments[0] == "masteries" or arguments[0] == "mastery":
                        player = "%20".join(arguments[1:])
                        (content, embed) = lol.masteries(player)
                        await message.channel.send(content=content, embed=embed)

                    elif arguments[0] == "skins" or arguments[0] == "skin":
                        nom = " ".join(arguments[1:])
                        await lol.champ_skins(message, client, nom)

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
            await message.channel.send("inviter ce bot : \n https://discordapp.com/oauth2/authorize?client_id=607969795798728716&scope=bot&permissions=2084043889")

        if commande == "ping":
            await message.channel.send("ping : `{}`".format(client.latency))
        taken = time.time()-start
        print("{} {} : {}s".format(commande, arguments, str(taken)[:6]))


@client.event
async def on_message_edit(before, after):
    await on_message(after)
activity = discord.Activity()
activity.type = discord.ActivityType.listening
activity.name = "quelque chose | {}help".format(prefix)
client.activity = activity

client.run(secret)
