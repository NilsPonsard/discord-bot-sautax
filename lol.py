import requests
import json
import difflib
import discord
import os
import io
from PIL import Image

with open("lolKey", "r") as file:
    api_key = file.readline()


ddragon_versions = json.loads(requests.get(
    "https://ddragon.leagueoflegends.com/api/versions.json").content)

version = ddragon_versions[0]

champions = json.loads(requests.get(
    "http://ddragon.leagueoflegends.com/cdn/{}/data/fr_FR/champion.json".format(version)).content)["data"]


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
            return json.loads(response.content)
        else:
            return -1


api = LolAPI(api_key)


def champ_skins(nom):
    # trouver le bon champion
    max_ratio = 0
    max_ratio_name = ""
    for c in champions:
        name = champions[c]["name"]
        ratio = difflib.SequenceMatcher(
            None, name.lower(), nom.lower()).ratio()

        if ratio > max_ratio:
            max_ratio = ratio
            max_ratio_name = name
            if ratio == 1:
                break
    if max_ratio < 0.6:
        return "Champion non trouvé", [None]
    else:
        r = requests.get(
            "http://ddragon.leagueoflegends.com/cdn/{}/data/fr_FR/champion/{}.json".format(version, max_ratio_name))
        if r.status_code != 200:
            return "Erreur lors de l'obtention des données", [None]
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
            list_embed.append(embed)
        return "", list_embed


def champ_lore(nom):
    max_ratio = 0
    max_ratio_name = ""
    for c in champions:
        name = champions[c]["name"]
        ratio = difflib.SequenceMatcher(
            None, name.lower(), nom.lower()).ratio()

        if ratio > max_ratio:
            max_ratio = ratio
            max_ratio_name = name
            if ratio == 1:
                break
    if max_ratio < 0.6:
        return "Champion non trouvé", None
    else:
        r = requests.get(
            "http://ddragon.leagueoflegends.com/cdn/{}/data/fr_FR/champion/{}.json".format(version, max_ratio_name))
        if r.status_code != 200:
            return "Erreur lors de l'obtention des données", None
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


def champ_rotation():
    content = api.request("/lol/platform/v3/champion-rotations")
    if content == -1:
        return "une erreur est survenue", [None]
    freeChampIds = content["freeChampionIds"]
    txt = ""
    showImage = True
    names = []

    images = []
    for c in champions:
        for key in freeChampIds:
            if int(champions[c]["key"]) == key:
                txt = txt + champions[c]["name"] + "\n"
                url = "http://ddragon.leagueoflegends.com/cdn/{}/img/champion/{}.png".format(
                    version, c)
                response = requests.get(url)
                names.append(c)
                if response.status_code == 200:
                    images.append(Image.open(io.BytesIO(response.content)))

                else:
                    showImage = False
    embed = discord.Embed(
        title="Rotation des champions gratuits", description=txt)
    if showImage == False:
        return "", embed, None

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

    image_file = discord.File(io.BytesIO(
        finish.getvalue()), filename="rotation.png")

    finish.close()
    return "", embed, image_file
