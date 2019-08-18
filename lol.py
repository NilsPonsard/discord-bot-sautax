import requests
import json
import difflib
import discord
import os
import time
import queue
import threading
import io
from PIL import Image

if not os.path.isfile("lolKey"):  # vérifier si le fichier existe
    with open("lolKey", "w") as file:
        file.write("Put your riot API key here")
        file.close()
    print("you need to define the riot api Key")

with open("lolKey", "r") as file:
    api_key = file.readline().replace("\n", "")


ddragon_versions = json.loads(requests.get(
    "https://ddragon.leagueoflegends.com/api/versions.json").content)

version = ddragon_versions[0]

champions = json.loads(requests.get(
    "http://ddragon.leagueoflegends.com/cdn/{}/data/fr_FR/champion.json".format(version)).content)["data"]

champions_by_ID = dict()
for c in champions:
    champions_by_ID[str(champions[c]["key"])] = champions[c]


class LolAPI:
    def __init__(self, key):
        self.key = key
        self.BaseUrl = "https://euw1.api.riotgames.com{}"
        self.options = {
            "Origin": None,
            "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Riot-Token": key,
            "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0"
        }

    def request(self, urlEnd):
        response = requests.get(
            self.BaseUrl.format(urlEnd), headers=self.options)
        if 200 == response.status_code:
            return json.loads(response.content), 200
        else:
            return -1, response.status_code


class FreeChampManager:
    def __init__(self):
        self.urlEnd = "/lol/platform/v3/champion-rotations"
        self.lastChecked = 0
        self.image = io.BytesIO()
        self.idList = []
        self.names = ""
        self.file = ""

    def get(self):
        current = time.time()
        if current-self.lastChecked > 3600:
            (content, status) = api.request(
                "/lol/platform/v3/champion-rotations")
            freeChampIds = content["freeChampionIds"]
            if freeChampIds != self.idList:
                self.request(content)
        self.image = io.BytesIO(self.image.getvalue())
        file = discord.File(self.image, filename="image.png")
        print(time.time()-current)
        return self.names, file

    def request(self, content):
        freeChampIds = content["freeChampionIds"]
        self.idList = freeChampIds
        txt = ""
        showImage = True
        names = []

        images = []

        for key in freeChampIds:
            c = champions_by_ID[str(key)]
            txt = txt + c["name"] + "\n"
            url = "http://ddragon.leagueoflegends.com/cdn/{}/img/champion/{}.png".format(
                version, c["id"])
            response = requests.get(url)
            names.append(c["id"])
            if response.status_code == 200:
                images.append(Image.open(io.BytesIO(response.content)))
        self.names = txt
        columns = len(images)
        rows = 1
        if len(images) % 2 == 0:
            rows = 2
            columns = int(len(images)/2)
        if len(images) % 3 == 0:
            rows = 3
            columns = int(len(images)/2)
        width = images[0].width
        height = images[0].height
        out = Image.new("RGB", (int(columns*width), int(rows*height)))
        x = 0
        y = 0
        for im in images:
            if x >= columns:
                y += 1
                x = 0
            out.paste(im, (x*width, y*height))
            x += 1
        finish = io.BytesIO()

        out.save(finish, "PNG")

        self.image = io.BytesIO(finish.getvalue())

        self.lastChecked = time.time()


api = LolAPI(api_key)
manager = FreeChampManager()


def player_infos(name):
    (result, code) = api.request(
        urlEnd="/lol/summoner/v4/summoners/by-name/{}".format(name))
    if result == -1:
        if code == 404:
            return "impossible de trouver le joueur", None
        return "une erreur est survenue", None
    else:
        name = result["name"]
        iconURL = "http://ddragon.leagueoflegends.com/cdn/{}/img/profileicon/{}.png".format(
            version, result["profileIconId"])
        ID = result["id"]
        total_mastery_score, status = api.request(
            "/lol/champion-mastery/v4/scores/by-summoner/{}".format(ID))
        full_mastery_data, status = api.request(
            "/lol/champion-mastery/v4/champion-masteries/by-summoner/{}".format(ID))
        match_list, status = api.request(
            "/lol/match/v4/matchlists/by-account/{}".format(ID))
        profiles, status = api.request(
            "/lol/league/v4/entries/by-summoner/{}".format(ID))
        in_game, status = api.request(
            "/lol/spectator/v4/active-games/by-summoner/{}".format(ID))

        embed = discord.Embed(
            title="**{}**".format(result["name"]), content="", colour=discord.Colour.from_rgb(255, 215, 0))
        top_five = ""
        embed.add_field(name="Niveau / total de maîtrise",
                        value="**{}** / `{}`".format(result["summonerLevel"], total_mastery_score))
        for profile in profiles:
            wins = profile["wins"]
            losses = profile["losses"]
            matches = wins+losses
            winrate = str((wins/matches)*100)
            winrate = winrate[0:4]
            hotstreak = ""
            if profile["hotStreak"]:
                hotstreak = "| :fire: Hot Streak"
            embed.add_field(name=profile["queueType"].replace("_", " ").capitalize(),
                            value="**{} {}** {} LP\nWinrate : **{}%** {}".format(profile["tier"].capitalize(), profile["rank"], profile["leaguePoints"], winrate, hotstreak))

        for i in range(0, 6):
            try:
                coffre_dispo = ""
                points = full_mastery_data[i]["championPoints"]
                level = full_mastery_data[i]["championLevel"]
                top_five = top_five + "**[{}]** ".format(level) + \
                    champions_by_ID[str(full_mastery_data[i]["championId"])]["name"] + " | score : `{}` ".format(
                    points) + "\n"

            except:
                top_five = top_five+"."
        embed.add_field(name="Champions les plus joués (main)", value=top_five)

        txt_ingame = ":red_circle: Not in game"
        if in_game != -1:
            txt_ingame = ":large_blue_circle: {}".format(
                in_game["gameType"].replace("_", " ").capitalize())
        embed.add_field(name="live game", value=txt_ingame, inline=False)
        embed.set_thumbnail(url=iconURL)
        return "", embed


def masteries(name):
    (result, code) = api.request(
        urlEnd="/lol/summoner/v4/summoners/by-name/{}".format(name))
    if result == -1:
        if code == 404:
            return "impossible de trouver le joueur", None
        return "une erreur est survenue", None
    else:
        name = result["name"]
        iconURL = "http://ddragon.leagueoflegends.com/cdn/{}/img/profileicon/{}.png".format(
            version, result["profileIconId"])
        ID = result["id"]
        total_mastery_score = api.request(
            "/lol/champion-mastery/v4/scores/by-summoner/{}".format(ID))
        full_mastery_data = api.request(
            "/lol/champion-mastery/v4/champion-masteries/by-summoner/{}".format(ID))
        embed = discord.Embed(
            title="**{}** | Niveau `{}`  | `{}` total de points de maîtrise ".format(result["name"], result["summonerLevel"], total_mastery_score), content="", colour=discord.Colour.from_rgb(255, 215, 0))
        i = 0
        for champ in full_mastery_data:
            if i >= 20:
                break
            i += 1
            coffre_obtenu = "`oui`"
            if champ["chestGranted"] == False:
                coffre_obtenu = "**non**"
            embed.add_field(inline=False,
                            name=str(i)+". "+champions_by_ID[str(champ["championId"])]["name"], value="`{}` points | coffre obtenu : {}".format(champ["championPoints"], coffre_obtenu))

        embed.set_thumbnail(url=iconURL)
        return "", embed


champ_skins_q = queue.Queue()


async def champ_skins_loop(client):
    start = time.time()
    if not champ_skins_q.empty():
        q = champ_skins_q.get()
        if q == None:
            return
        else:
            (embed,  message) = q
            await message.channel.send(content="", embed=embed)
            client.loop.create_task(champ_skins_loop(client))

    else:
        client.loop.create_task(champ_skins_loop(client))
    end = str(time.time()-start)[:6]
    print("send {}".format(end))


def champ_skins_run(nom, message):
    # trouver le bon champion
    start = time.time()
    max_ratio = 0
    max_ratio_name = ""
    for c in champions:
        name = champions[c]["name"]
        ratio = difflib.SequenceMatcher(
            None, name.lower(), nom.lower()).ratio()

        if ratio > max_ratio:
            max_ratio = ratio
            max_ratio_name = champions[c]["id"]
            if ratio == 1:
                break
    if max_ratio < 0.6:
        return "Champion non trouvé", [None]
    else:
        r = requests.get(
            "http://ddragon.leagueoflegends.com/cdn/{}/data/fr_FR/champion/{}.json".format(version, max_ratio_name))
        if r.status_code != 200:
            embed = discord.Embed(title=str(r.status_code),
                                  content=str(r.content)+max_ratio_name)
            return "Erreur lors de l'obtention des données", [embed]
        skins = json.loads(r.content)["data"][max_ratio_name]["skins"]
        list_embed = []
        x = 1
        for s in skins:
            embed = discord.Embed(
                title=s["name"], description="{}/{}".format(x, len(skins)))
            x += 1
            url = "http://ddragon.leagueoflegends.com/cdn/img/champion/splash/{}_{}.jpg".format(
                max_ratio_name, s["num"])
            embed.set_image(url=url)
            champ_skins_q.put((embed, message))
        champ_skins_q.put(None)
    end = str(time.time()-start)[:6]
    print("lol skins : {}".format(end))


async def champ_skins(message, client, nom):
    t = threading.Thread(target=champ_skins_run, args=(nom, message))
    t.start()
    client.loop.create_task(champ_skins_loop(client))


def champ_lore(nom):
    max_ratio = 0
    max_ratio_name = ""
    for c in champions:
        name = champions[c]["name"]
        ratio = difflib.SequenceMatcher(
            None, name.lower(), nom.lower()).ratio()

        if ratio > max_ratio:
            max_ratio = ratio
            max_ratio_name = champions[c]["id"]
            if ratio == 1:
                break
    if max_ratio < 0.6:
        return "Champion non trouvé", None
    else:
        r = requests.get(
            "http://ddragon.leagueoflegends.com/cdn/{}/data/fr_FR/champion/{}.json".format(version, max_ratio_name))
        if r.status_code != 200:
            embed = discord.Embed(title=str(r.status_code),
                                  content=str(r.content)+max_ratio_name)
            print(max_ratio_name)
            return "Erreur lors de l'obtention des données", embed
        data = json.loads(r.content)["data"][max_ratio_name]
        embed = discord.Embed(
            title=data["name"], description=data["lore"])
        url = "http://ddragon.leagueoflegends.com/cdn/img/champion/splash/{}_0.jpg".format(
            max_ratio_name)
        embed.set_image(url=url)
        url = "http://ddragon.leagueoflegends.com/cdn/{}/img/champion/{}.png".format(
            version, max_ratio_name)
        embed.set_thumbnail(url=url)
        return "", embed


champ_rotation_q = queue.Queue()


def champ_rotation_run(message, sent_message):
    (names, file) = manager.get()
    embed = discord.Embed(title="Rotation des champions", description=names)
    champ_rotation_q.put((embed, file, message, sent_message))


async def champ_rotation_loop(client):
    if not champ_rotation_q.empty():
        q = champ_rotation_q.get()
        if q == None:
            return
        else:
            (embed, file, message, sent_message) = q

            await sent_message.delete()
            await message.channel.send(content="", embed=embed, file=file)
    else:
        client.loop.create_task(champ_rotation_loop(client))


async def champ_rotation(message, sent_message, client):
    t = threading.Thread(target=champ_rotation_run,
                         args=(message, sent_message))
    t.start()
    client.loop.create_task(champ_rotation_loop(client))
