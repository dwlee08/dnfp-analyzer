from flask import request, jsonify
import json
from urllib import parse as urlparse
import time
import sys

import sqlite3
from dnfp import app, apputils
from inventory import Inventory
from skilltree import SkillTree
from character import Character
from libutil import LibUtil as myutil

def get_neople_ids(name, server):
    server_dict={'안톤':'anton','바칼':'bakal','카인':'cain','카시야스':'casillas',
                '디레지에':'diregie','힐더':'hilder','프레이':'prey','시로코':'siroco'}
    s_id=server_dict[server]

    cha_id_url = 'servers/'+s_id+'/characters?characterName='+urlparse.quote(name)+'&'

    try:
        cha_id_dic=myutil.load_api(cha_id_url)
    except:
        raise

    cha_id=cha_id_dic['rows'][0]['characterId']

    return s_id, cha_id
      
def create_char_json(s_id, cha_id, test_mode = False, epic_status = False):
    character = Character(cha_id, s_id, test_mode)
    if character.status[0] != 'ok':
        print (character.status[1])
        return character.status[1]

    character.do_create_char_dict(epic_status)
       
    return character.char_stat

def make_char_stat(s_id, cha_id, test_mode = False, epic_status = True):
    char_stat = create_char_json(s_id, cha_id, test_mode = test_mode, epic_status = epic_status)

    return char_stat

@app.route("/char", methods=("GET", "POST"))
def char_stat():
    name = request.args.get("name")
    server = request.args.get("server")

    sid, cid = get_neople_ids(name, server)

    char_stat = make_char_stat(sid, cid, test_mode = False, epic_status = False)
    return jsonify(char_stat)

