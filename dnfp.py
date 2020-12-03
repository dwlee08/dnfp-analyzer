from flask import Flask
from json import loads
import json
import urllib.request
import sqlite3
from urllib import parse as urlparse
import sys
from inventory import Inventory
from skilltree import SkillTree
from character import Character

apikey='NqzICVeo3FesBuq3Gw1CmYhiOiFdYcHr'

class apputils():
    sid_dict={'anton':'안톤','bakal':'바칼','cain':'카인','casillas':'카시야스',
            'diregie':'디레지에','hilder':'힐더','prey':'프레이','siroco':'시로코', 'all':'전체'}
    buff_dict = {}
    db = None

    @classmethod
    def initstatic(cls):
        with open("/var/www/html/runtime/buff.json", "r") as buff_json:
            cls.buff_dict = json.load(buff_json)

    @classmethod
    def get_buff_dict(cls, cid, jid):
        return cls.buff_dict[cid][jid]
      
    @staticmethod
    def quote(name):
        return urlparse.quote(name)

    @staticmethod
    def load_api(URL):
        api_load=urllib.request.urlopen(URL+'apikey='+apikey)
        if (api_load.status == 200):
            return loads(api_load.read().decode("utf-8"))
        else:
            raise Exception

        return None

    @staticmethod
    def get_neople_id(cid, sid):

            cha_id_url = 'https://api.neople.co.kr/df/servers/'+sid+'/characters/'+cid+'/status?'

            try:
                cha_id_dic=apputils.load_api(cha_id_url)
            except:
                raise

            return cha_id_dic

    @classmethod
    def sid_to_server(cls, sid):
        return cls.sid_dict[sid]

apputils.initstatic()
SkillTree.initstatic()
Inventory.initstatic()
Character.initstatic()

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['JSON_SORT_KEYS'] = False

@app.route("/")
def wrong():
    html = f"""
<form action="/char">
  <label for="name">캐릭터명</label><br>
  <input type="text" id="name" name="name" value=""><br>
  <label for="server">서버</label><br>
  <input type="text" id="server" name="server" value=""><br><br>
  <input type="submit" value="Submit">
</form> 
    """
    return html

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

import char

if __name__ == "__main__":
    app.run()
