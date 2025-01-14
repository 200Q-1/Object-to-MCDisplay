import bpy
import requests
import json
import base64
import tempfile
import urllib
import os

def get_skin(self,context):
    username = "200Q"
    url = "https://api.mojang.com/users/profiles/minecraft/"+username
    headers = {"content-type": "application/json"}
    r = requests.get(url, headers=headers)
    data = r.json()

    url = "https://sessionserver.mojang.com/session/minecraft/profile/"+data["id"]
    r = requests.get(url, headers=headers)
    data = r.json()

    textures= data['properties'][0]['value']
    textures = json.loads(base64.b64decode(textures))

    url= textures['textures']['SKIN']['url']
    with urllib.request.urlopen(url) as web_file:
        with tempfile.TemporaryDirectory() as temp:
            png=os.path.join(temp,username+".png")
            with open(png, mode='wb') as local_file:
                local_file.write(web_file.read())
                data = bpy.data.images.load(png)
            data.pack()
            data.name = username
    return data