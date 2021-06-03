from json import loads
import json
import numpy as np
import math
import re
import datetime

from inventory import Inventory
from skilltree import SkillTree
from libutil import LibUtil as myutil

sid_dict={'anton':'안톤','bakal':'바칼','cain':'카인','casillas':'카시야스',
          'diregie':'디레지에','hilder':'힐더','prey':'프레이','siroco':'시로코'}

class Character():
    buff_dict = None

    @classmethod
    def initstatic(cls):
        with open("./buff.json", "r") as buff_json:
            cls.buff_dict = json.load(buff_json)

    def calculate_base_stat(self, v, typ):
        if self.classname == '프리스트(남)' and typ == '정신력':
            v += 32

        #길드/모험단 스탯
        for item in self.s_dict['buff']:
            for status in item['status']:
                if status['name'] == typ:
                    v += status['value']

        return v

    def get_buff_info(self):
        buff50_base = 750
        if self.classname == '프리스트(남)':
            buff_name = '영광의 축복'
            apo_name = '아포칼립스'
            passive_name = '수호의 은총'
            buff_aura_name = '신념의 오라'
            buff30_base = 620
        elif self.classname == '프리스트(여)':
            buff_name = '용맹의 축복'
            apo_name = '크럭스 오브 빅토리아'
            passive_name = '계시 : 아리아'
            buff_aura_name = '신실한 열정'
            buff30_base = 665
        else:
            buff_name = '금단의 저주'
            apo_name = '마리오네트'
            passive_name = '퍼페티어'
            buff_aura_name = '소악마'
            buff30_base = 665

        return (buff30_base, buff50_base, buff_name, apo_name, passive_name, buff_aura_name)

    def analyze_stat(self, diff = None):
        stat_info = {'힘':0, '체':0, '지':0, '정':0}
        elem_info = {}
        dam_info = {}
        for cur in self.s_dict['status']:
            cur_name = cur['name'].replace(' ','')
            cur_val = cur['value']
        
            if (cur_name == '힘' or cur_name == '지능' or
                    cur_name == '체력' or cur_name == '정신력'):
                stat_info[cur_name[0]] = cur_val
            elif (cur_name == '화속성강화' or cur_name == '수속성강화' or
                    cur_name == '명속성강화' or cur_name == '암속성강화'):
                elem_info[cur_name[0]] = cur_val
            elif (cur_name == '물리공격' or cur_name == '마법공격' or
                    cur_name == '독립공격'):
                dam_info[cur_name[0]] = cur_val
            
            self.char_stat[cur_name] = cur_val

            if diff is not None:
                if cur_name in diff.keys():
                    self.char_stat[cur_name] += diff[cur_name]

        max_stat = max(stat_info.values())
        self.char_stat['주스탯'] = {'value':max_stat, 'list':[]}
        for key in stat_info.keys():
            if stat_info[key] == max_stat:
                self.char_stat['주스탯']['list'].append(key)

        max_elem = max(elem_info.values())
        self.char_stat['주속강'] = {'value':max_elem, 'list':[]}
        for key in elem_info.keys():
            if max_elem - elem_info[key] < 13:
                self.char_stat['주속강']['list'].append(key)

        max_dam = max(dam_info.values())
        self.char_stat['주공격'] = []
        for key in dam_info.keys():
            if dam_info[key] == max_dam:
                self.char_stat['주공격'].append(key)
    
    def analyze_sw(self, cbuff):
        sinfo = self.sw_dict['skill']['buff']['skillInfo']    

        vidx = cbuff['option_idx']
        self.char_stat['nick'] = self.nick = cbuff['nick']
        self.base_stat = cbuff['base_stat']

        if self.nick in ['ghostknight', 'daemonslayer', 'vegabond', 'mnenmaster', 'mlauncher', 'mmechanic', 'darknight', 'mranger', 'duelist', 'dragonknight', 'rogue', 'franger', 'daemonknight', 'fspitfire', 'battlemage', 'holybattle', 'vanguard', 'berserk', 'icemage', 'necromancer', 'swordmaster', 'fstriker', 'avenger', 'dimrunner', 'elemental', 'elvenknight', 'flauncher', 'fmechanic', 'agent', 'warlock', 'infighter', 'mspitfire', 'siranui', 'mstriker', 'dragonlancer']:
            self.char_stat['char_type'] = '딜러'
        elif self.nick in ['weaponmaster', 'diva', 'redemer', 'alchemist', 'bloodmage', 'dancer', 'shadowdancer', 'soulbringer', 'summoner', 'asura', 'windmage', 'darktempler', 'fnenmaster', 'poisonmaster', 'inferno', 'giant', 'mstreetfighter', 'creator', 'exocist', 'troubleshooter', 'paladin', 'pathfinder', 'darklancer', 'hitman']:
            self.char_stat['char_type'] = '시너지'
        else:
            self.char_stat['char_type'] = '버퍼'

        sw_name = sinfo['name']
        if sinfo['option'] is None:
            self.char_stat['버프'] = (sw_name, 0, 0, None)
            self.inner_data['dam_type'] = "독립공격"
            return

        sw_values = sinfo['option']['values']
        sw_lvl = sinfo['option']['level']

        if self.buffer is None:
            buff_max = cbuff['option_max']
            buff_val = float(sw_values[vidx])
            self.inner_data['dam_type'] = cbuff['ctype']

            extra_buff = []
            extra_options = cbuff.get('extra_options')
            if extra_options is not None:
                for opt in extra_options:
                    etyp, evidx = opt
                    evval = float(sw_values[evidx])
                    if sw_name == "오기조원":
                        evval *= 5
                    extra_buff.append((etyp, evval))
        
            for eb in extra_buff: 
                typ, v = eb
                for key in self.char_stat.keys():
                    if key.find(typ) >= 0:
                        self.char_stat[key] += v

            if sw_name == "오기조원":
                buff_val *= 5
            elif sw_name == "섀도우 박서":
                buff_val *= 1.5

            buff_power = buff_val/buff_max * 100

            if buff_power > 100:
                buff_power = 100

            self.char_stat['버프'] = (sw_name, sw_lvl, buff_val, buff_power)
            
            self.char_stat['points'] += buff_power

        else:
            buff_val = float(sw_values[vidx])
            self.char_stat['버프'] = (sw_name, sw_lvl, buff_val, None)
            self.inner_data['dam_type'] = "독립공격"

    def get_dicts(self, s_id, cha_id):
        max_retry = 3
        while True:
            try:
                s_dict=myutil.load_api('servers/'+s_id+'/characters/'+cha_id+'/status?')
                e_dict=myutil.load_api('servers/'+s_id+'/characters/'+cha_id+'/equip/equipment?')
                c_dict=myutil.load_api('servers/'+s_id+'/characters/'+cha_id+'/equip/creature?')
                sw_dict=myutil.load_api('servers/'+s_id+'/characters/'+cha_id+'/skill/buff/equip/equipment?')
                a_dict=myutil.load_api('servers/'+s_id+'/characters/'+cha_id+'/equip/avatar?')

                g_dict=myutil.load_api('servers/'+s_id+'/characters/'+cha_id+'/equip/flag?')
                t_dict=myutil.load_api('servers/'+s_id+'/characters/'+cha_id+'/equip/talisman?')
                sk_dict=myutil.load_api('servers/'+s_id+'/characters/'+cha_id+'/skill/style?')
            except:
                max_retry -= 1
                if max_retry == 0:
                    raise
            else:
                break

        if self.test_mode is True:
            with open("s_dict.json", "w") as of:
                json.dump(s_dict, of)
            with open("e_dict.json", "w") as of:
                json.dump(e_dict, of)
            with open("c_dict.json", "w") as of:
                json.dump(c_dict, of)
            with open("a_dict.json", "w") as of:
                json.dump(a_dict, of)
            with open("g_dict.json", "w") as of:
                json.dump(g_dict, of)
            with open("t_dict.json", "w") as of:
                json.dump(t_dict, of)
            with open("sk_dict.json", "w") as of:
                json.dump(sk_dict, of)
            with open("sw_dict.json", "w") as of:
                json.dump(sw_dict, of)
        
        return [s_dict, sw_dict, sk_dict, e_dict, c_dict, a_dict, g_dict, t_dict]

    def get_sw_dicts(self, s_id, cha_id):
        max_tries = 3
        while True:
            try:
                a_dict=myutil.load_api('servers/'+s_id+'/characters/'+cha_id+'/skill/buff/equip/avatar?')
                c_dict=myutil.load_api('servers/'+s_id+'/characters/'+cha_id+'/skill/buff/equip/creature?')
            except:
                max_tries -= 1
                if max_tries == 0:
                    raise
            else:
                break
        
        
        sw_a_dict = a_dict['skill']['buff']
        try:
            sw_c_dict = {'creature':c_dict['skill']['buff']['creature'][0]}
        except:
            sw_c_dict = {'creature':None}

        if self.test_mode is True:
            with open('sw_a_dict.json', 'w') as f:
                json.dump(sw_a_dict, f)
            with open('sw_c_dict.json', 'w') as f:
                json.dump(sw_c_dict, f)

        return (sw_a_dict, sw_c_dict)

    def get_epic_status(self, s_id, c_id, _cur_list = None):
        mon_end = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        #fix: 2021 prepare
        today = datetime.datetime.today()
        thisyear = today.year
        thismon = today.month
        thisday = today.day

        thishour = today.hour
        thismin = today.minute
        isEnd = False

        if _cur_list is not None:
            cur_list = _cur_list
        else:
            cur_list = {'지옥파티':0, '에픽':0, '신화':0, '시로코':0, '신화목록':{}, '에픽목록':{}, '시로코목록':{}}

        for year in range(2020, thisyear+1):
            for mon in range(1, 13):
                if isEnd is True:
                    break

                _startDate = datetime.date(year, mon, 1)
                if year == 2020 and mon == 1:
                    _startDate = _startDate.replace(day=9)
                    
                startDate = str(_startDate).replace('-','')+'T0000'

                _mon_end = mon_end[mon-1]

                if year % 4 != 0 and mon == 2:
                    _mon_end -= 1

                _endDate = datetime.date(year, mon, _mon_end)
                if mon == thismon and year == thisyear:
                    _endDate = _endDate.replace(day=thisday)
                    endTime = 'T'+str(thishour).zfill(2)+str(thismin).zfill(2)
                    isEnd = True
                else:
                    endTime = 'T2359'

                endDate = str(_endDate).replace('-','')+endTime

                order = year*100 + mon
                
                url = 'servers/'+s_id+'/characters/'+c_id+'/timeline?limit=100&code=504,505,507,513,518&startDate='+startDate+'&endDate='+endDate+'&'
                while (url is not None):
                    try:
                        tresult = myutil.load_api(url)
                    except:
                        print(url)
                        raise
                    
                    if len(tresult['timeline']['rows']) > 0:
                        for entry in tresult['timeline']['rows']:
                            code = entry['code']
                            edata = entry['data']

                            ir = edata['itemRarity']
                            iid = edata['itemId']
                            iname = edata['itemName']
                            dname = edata.get('dungeonName')

                            if iname == '무형의 잔향':
                                cur_list['시로코'] += 1
                                if '무형의 잔향' in cur_list['시로코목록'].keys():
                                    cur_list['시로코목록']['무형의 잔향']['count'] += 1
                                    cur_list['시로코목록']['무형의 잔향']['code'].append(code)
                                else:
                                    cur_list['시로코목록']['무형의 잔향'] = {'id':iid, 'count':1, 'code':[code]}

                            elif ir in ['신화' , '에픽']:
                                if code == 505 and dname == '지혜의 인도':
                                    cur_list['지옥파티'] += 10

                                if iname.find('무형 :') < 0 and iname.find('무의식 :') < 0 and iname.find('환영 :') < 0:
                                    cur_list[ir] += 1
                                else:
                                    cur_list['시로코'] += 1
                                    if iname in cur_list['시로코목록'].keys():
                                        cur_list['시로코목록'][iname]['count'] += 1
                                        cur_list['시로코목록'][iname]['code'].append(code)
                                    else:
                                        cur_list['시로코목록'][iname] = {'id':iid, 'count':1, 'code':[code]}
                                    continue

                                if ir == '신화':
                                    if iname in cur_list['신화목록'].keys():
                                        cur_list['신화목록'][iname]['count'] += 1
                                        cur_list['신화목록'][iname]['code'].append(code)
                                    else:
                                        cur_list['신화목록'][iname] = {'id':iid, 'count':1, 'code':[code]}
                                else:
                                    if iname in cur_list['에픽목록'].keys():
                                        cur_list['에픽목록'][iname]['count'] += 1
                                        cur_list['에픽목록'][iname]['code'].append(code)
                                    else:
                                        cur_list['에픽목록'][iname] = {'id':iid, 'count':1, 'code':[code]}
 
                            else:
                                continue

                    if tresult['timeline']['next'] is not None:
                        lnext = tresult['timeline']['next']
                        url = 'servers/'+s_id+'/characters/'+c_id+'/timeline?next='+lnext+'&'
                    else:
                        url = None
                        
                if mon == thismon and year == thisyear:
                    break

        if self.test_mode is True:
            with open('epictree.json', 'w') as f:
                json.dump(cur_list, f)
        
        return cur_list

    def do_create_char_dict(self, epic_status, custom_data, squad_data = None):
        character = self

        classid = character.classid
        jobid = character.jobid
        s_id = character.sid
        cha_id = character.cid
        noclass = character.char_stat.get('noclass')
        
        if epic_status is True and noclass is None:
            character.epic_status = self.get_epic_status(s_id, cha_id)
        else:
            character.epic_status = None
   
        #self.logger.info('start analyze :' + character.name + ' ' + character.server)

        if custom_data is not None:
            character.char_stat['inventory'].create_equip_from_custom(custom_data)
        else:
            character.char_stat['inventory'].create_equip_info()

        if noclass is not None:
            character.char_stat['장비'] = character.char_stat['inventory'].equip_info
            return

        character.inner_data['main_siroco'] = character.char_stat['inventory'].extra_info['siroco']
        character.char_stat['inventory'].build_item_db_list()
        if character.buffer is not None:
            character.buffer['inventory'].create_equip_info()
            character.buffer['inventory'].build_item_db_list()
            buff_equip_list = list(character.buffer['inventory'].equip_info.values())
        else:
            buff_equip_list = []

        #타임라인 누락되었지만 장착한 신화 장비가 있을경우 등록
        if epic_status is True:
            equip_list = list(character.char_stat['inventory'].equip_info.values()) + buff_equip_list
            for eitem in equip_list:
                if eitem['등급'] == '신화' and eitem['name'] not in character.epic_status['신화목록'].keys():
                    character.epic_status['신화목록'][eitem['name']] = {'id':eitem['id'], 'count':1, 'code':[505]}
                    character.epic_status['신화'] += 1
            
        character.char_stat['inventory'].handle_item_options()
        for name, stat in character.char_stat['inventory'].istatus.items():
            for slot, item in character.char_stat['inventory'].equip_info.items():
                if item['name'] == name:
                    item['status'] = stat

        if character.char_stat['char_type'] == '시너지':
            character.char_stat['inventory'].sops.append({'시너지':34})

        final_synergy = {}
        for ops in character.char_stat['inventory'].sops:
            _k = list(ops.keys())[0]
            v = list(ops.values())[0]

            if _k in ['깡스탯', '힘지깡']:
                k = '스탯'
            else:
                k = _k

            if k not in final_synergy.keys():
                if k.find('시너지스공') >= 0:
                    final_synergy[k] = (1 + v/100)
                else:
                    final_synergy[k] = v
            else:
                if k.find('시너지스공') >= 0:
                    final_synergy[k] *= (1 + v/100)
                else:
                    final_synergy[k] += v

        if character.char_stat['char_type'] != '버퍼':
            character.char_stat['시너지옵션'] = final_synergy

        for name, ops in character.char_stat['inventory'].iops.items():
            if (name.find('시로코') >= 0 and name.find('[시로코]') < 0) or (name.find('오즈마융합') >= 0):
                args = name.split('-')
                key = args[1]

                if args[0] == '시로코1':
                    subkey = '1'
                elif args[0] == '시로코2':
                    subkey = '2'
                else:
                    subkey = 'ozma'

                item = character.char_stat['inventory'].equip_info[key]
                for op in ops:
                    item['data']['siroco'][subkey].append(op)
            elif name.find('신화') >= 0:
                key = '신화'
                for item in character.char_stat['inventory'].equip_info.values():
                    if item['등급'] == '신화':
                        for op in ops:
                            item['data']['myth'].append(op)
                        break
            elif name.find('변환') >= 0:
                args = name.split('-')
                key = args[1]
                
                item = character.char_stat['inventory'].equip_info[key]
                for op in ops:
                    item['data']['transform'].append(op)
            else:
                for op in ops:
                    if len(op) == 2:
                        for slot, item in character.char_stat['inventory'].equip_info.items():
                            if item['name'] == name:
                                item['data']['options'].append(op)
                    else:
                        for slot, item in character.char_stat['inventory'].equip_info.items():
                            if item['name'] == name:
                                item['data']['stats'].append(op)

        for name, ops in character.char_stat['inventory'].buff_iops.items():
            #print (name, ops)
            if (name.find('시로코') >= 0 and name.find('[시로코]') < 0) or (name.find('오즈마융합') >= 0):
                args = name.split('-')
                key = args[1]

                if args[0] == '시로코1':
                    subkey = '1'
                elif args[0] == '시로코2':
                    subkey = '2'
                else:
                    subkey = 'ozma'

                item = character.char_stat['inventory'].equip_info[key]
                for op in ops:
                    item['data']['buffsiroco'][subkey].append(op)
            elif name.find('신화') >= 0:
                key = '신화'
                for item in character.char_stat['inventory'].equip_info.values():
                    if item['등급'] == '신화':
                        for op in ops:
                            item['data']['buffmyth'].append(op)
                        break
            elif name.find('변환') >= 0:
                args = name.split('-')
                key = args[1]

                item = character.char_stat['inventory'].equip_info[key]
                for op in ops:
                    item['data']['bufftransform'].append(op)
            else:
                for op in ops:
                    if len(op) == 2:
                        for slot, item in character.char_stat['inventory'].equip_info.items():
                            if item['name'] == name:
                                item['data']['buffoptions'].append(op)

        if character.buffer is not None:
            character.buffer['inventory'].handle_item_options()
            for name, ops in character.buffer['inventory'].iops.items():
                if (name.find('시로코') >= 0 and name.find('[시로코]') < 0) or (name.find('오즈마융합') >= 0):
                    args = name.split('-')
                    key = args[1]

                    if args[0] == '시로코1':
                        subkey = '1'
                    elif args[0] == '시로코2':
                        subkey = '2'
                    else:
                        subkey = 'ozma'

                    item = character.buffer['inventory'].equip_info[key]
                    for op in ops:
                        item['data']['siroco'][subkey].append(op)

                elif name.find('신화') >= 0:
                    key = '신화'
                    for item in character.buffer['inventory'].equip_info.values():
                        if item['등급'] == '신화':
                            for op in ops:
                                item['data']['myth'].append(op)

                elif name.find('변환') >= 0:
                    args = name.split('-')
                    key = args[1]
                    
                    item = character.buffer['inventory'].equip_info[key]
                    for op in ops:
                        item['data']['transform'].append(op)

                else:
                    for op in ops:
                        if len(op) == 2:
                            for slot, item in character.buffer['inventory'].equip_info.items():
                                if item['name'] == name:
                                    item['data']['options'].append(op)

                        else:
                            for slot, item in character.buffer['inventory'].equip_info.items():
                                if item['name'] == name:
                                    item['data']['stats'].append(op)

            for name, ops in character.buffer['inventory'].buff_iops.items():
                if (name.find('시로코') >= 0 and name.find('[시로코]') < 0) or (name.find('오즈마융합') >= 0):
                    args = name.split('-')
                    key = args[1]

                    if args[0] == '시로코1':
                        subkey = '1'
                    elif args[0] == '시로코2':
                        subkey = '2'
                    else:
                        subkey = 'ozma'

                    item = character.buffer['inventory'].equip_info[key]
                    for op in ops:
                        item['data']['buffsiroco'][subkey].append(op)
                elif name.find('신화') >= 0:
                    key = '신화'
                    for item in character.buffer['inventory'].equip_info.values():
                        if item['등급'] == '신화':
                            for op in ops:
                                item['data']['buffmyth'].append(op)
                            break

                elif name.find('변환') >= 0:
                    args = name.split('-')
                    key = args[1]
                    
                    item = character.buffer['inventory'].equip_info[key]
                    for op in ops:
                        item['data']['bufftransform'].append(op)

                else:
                    for op in ops:
                        if len(op) == 2:
                            for slot, item in character.buffer['inventory'].equip_info.items():
                                if item['name'] == name:
                                    item['data']['buffoptions'].append(op)



        character.char_stat['skilltree'].handle_special_case()

        if squad_data is not None:
            bless = squad_data['bless']
            apo = squad_data['apo']
            dam = squad_data['dam']
            synergy = squad_data['synergy']
        else:
            bless = 18000
            apo = 17000
            dam = 2000
            synergy = None

        #던전 속성       
        d_info = {}
        d_info['name'] = '시로코'
        #d_info['지역버프'] = {'factor':2.31, 'inc':3980}
        d_info['지역버프'] = {'factor':2.334, 'inc':4397}
        d_info['축스탯'] = bless
        d_info['아포스탯'] = apo
        d_info['축공격력'] = dam
        d_info['버퍼속저깍'] = 60
        d_info['몹속저'] = 50
        d_info['비진각보정'] = 1.15
        d_info['공격유형'] = {}
        d_info['공격유형']['지속딜']=  {'시간':40, '방어력':99.6, '반영스탯':['축스탯', '아포스탯'], '계산식':'지속딜*2', '정령왕':1.10, '반영률':1, '제외스킬': None, '가동률':1}
        d_info['공격유형']['지속정자극딜']=  {'시간':40, '쿨감':20, '방어력':99.6, '반영스탯':['축스탯', '아포스탯'], '계산식':'지속정자극딜*2', '정령왕':1.10, '반영률':1, '제외스킬': None, '가동률':1}
        d_info['공격유형']['그로기딜'] = {'시간':25, '방어력':99.6, '반영스탯':['축스탯', '아포스탯'], '계산식':'그로기딜*2', '정령왕':1.16, '반영률':1, '제외스킬': None, '가동률':1}
        d_info['공격유형']['정자극딜'] = {'시간':25, '쿨감':20, '방어력':99.6, '반영스탯':['축스탯', '아포스탯'], '계산식':'정자극딜*2', '정령왕':1.16, '반영률':1, '제외스킬': None, '가동률':1}
        d_info['공격유형']['80초딜'] = {'시간':80,'방어력':99.6, '반영스탯':['축스탯', '아포스탯'], '계산식':'80초딜*2', '정령왕':1.10, '반영률':1, '제외스킬': None, '가동률':0.95}
        d_info['공격유형']['60초딜'] = {'시간':60,'방어력':99.6, '반영스탯':['축스탯', '아포스탯'], '계산식':'60초딜*2', '정령왕':1.10, '반영률':1, '제외스킬': None, '가동률':0.97}

        character.char_stat['skilltree'].calculate_deal(d_info, synergy)

        if squad_data is not None:
            bless = squad_data['bless']
            apo = squad_data['apo']
            dam = squad_data['dam']
            synergy = squad_data['synergy']
        else:
            bless = 28000
            apo = 27000
            dam = 2500
            synergy = None

        d_info = {}
        d_info['name'] = '오즈마'
        #d_info['지역버프'] = {'factor':2.334, 'inc':4397}
        d_info['지역버프'] = {'factor':2.334, 'inc':4397}
        d_info['축스탯'] = bless
        d_info['아포스탯'] = apo
        d_info['축공격력'] = dam
        d_info['버퍼속저깍'] = 60
        d_info['몹속저'] = 50
        d_info['비진각보정'] = 1.15
        d_info['공격유형'] = {}
        d_info['공격유형']['40초딜']=  {'시간':40, '방어력':99.4, '반영스탯':['축스탯', '아포스탯'], '계산식':'40초딜*2', '정령왕':1.10, '반영률':1, '제외스킬': None, '가동률':0.9, '추가딜증':1.25*1.2}
        d_info['공격유형']['40초정자극딜']=  {'시간':40, '쿨감':20, '방어력':99.4, '반영스탯':['축스탯', '아포스탯'], '계산식':'40초정자극딜*2', '정령왕':1.10, '반영률':1, '제외스킬': None, '가동률':0.9, '추가딜증':1.25*1.2}
        d_info['공격유형']['240초딜']=  {'시간':240, '방어력':99.4, '반영스탯':['축스탯', '아포스탯'], '계산식':'240초딜*2', '정령왕':1.10, '반영률':1, '제외스킬': None, '가동률':0.8}
        d_info['공격유형']['240초정자극딜']=  {'시간':240, '쿨감':20, '방어력':99.4, '반영스탯':['축스탯', '아포스탯'], '계산식':'240초정자극딜*2', '정령왕':1.10, '반영률':1, '제외스킬': None, '가동률':0.8}

        character.char_stat['skilltree'].calculate_deal(d_info, synergy)

        character.char_stat['아이템속강증가'] = character.char_stat['inventory'].item_elem

        if character.buffer is not None:
            character.char_stat['버프분석결과'] = {}
            character.char_stat['skilltree'].calculate_buff()
            character.buffer['skilltree'].calculate_buff()
            character.calculate_buff_score()

        report = character.create_report()

        character.char_stat['장비'] = character.char_stat['inventory'].equip_info
        if character.buffer is not None:
            character.char_stat['스위칭장비'] = character.buffer['inventory'].equip_info

        del character.char_stat['inventory']
        del character.char_stat['skilltree']
        character.char_stat['리포트'] = report
        if epic_status is True:
            character.char_stat['에픽획득'] = character.epic_status

        main_stat = character.char_stat['main_stat']
        b = character.char_stat[main_stat['type']]
        a = main_stat['value']

        main_stat['mastery'] = b - a

        if self.test_mode is True:
            with open("result.json", "w") as f:
                json.dump(character.char_stat, f)

    def __init__(self, cid, sid, test_mode = False, custom_data = None):
        self.test_mode = test_mode
 
        if cid is None and sid is None:
            return None

        self.inner_data = {}

        try:
            raw_dicts = self.get_dicts(sid, cid)
        except:
            self.status = ('error', 'Neople API 접속불가')
            return None

        self.s_dict, self.sw_dict, self.sk_dict = raw_dicts[0:3]
        self.e_dict, self.c_dict, self.a_dict, self.g_dict, self.t_dict = raw_dicts[3:8]

        sw_dict = self.sw_dict

        self.name = sw_dict['characterName']
        self.server = sid_dict[sid]
        self.advname = sw_dict["adventureName"]
        self.classname = sw_dict["jobName"]
        self.jobname = sw_dict["jobGrowName"]
        self.classid = sw_dict["jobId"]
        self.jobid = sw_dict["jobGrowId"]
        self.level = sw_dict["level"]
        self.cid = cid
        self.sid = sid
        
        if sw_dict['skill']['buff'] is None:
            self.status = ('error', '버프강화 미지정')
            self.char_stat = {
                    '레벨':self.level, '이름':self.name, '서버':self.server, '모험단':self.advname, 'class':self.classname, '전직':self.jobname, 'ids':(sid, cid), '버퍼여부':False, 'jobid':self.jobid, 'noclass': True, 'points': 0
                }

            self.char_stat['inventory'] = Inventory(self, self.e_dict, self.c_dict, self.a_dict, self.g_dict, self.t_dict, test_mode = self.test_mode, custom_data = None)
            self.buffer = None
            return None
       
        if self.jobname[0] == '眞':
            self.classTypeNeo = True
        else:
            self.classTypeNeo = False

            try:
                cbuff = self.buff_dict[self.classid][self.jobid]
                self.bonus_disable = False
            except:
                newjobid = SkillTree.get_neo_jobid(self.classid, self.jobid)
                if newjobid is not None:
                    self.jobid = newjobid
                    self.bonus_disable = True

        if self.jobname in ['眞 크루세이더', '眞 인챈트리스']:
            sinfo = self.sw_dict['skill']['buff']['skillInfo']    
            if sinfo['name'] == '성령의 메이스':
                self.buffer = None
                cbuff = self.buff_dict[self.classid][self.jobid]
                self.isBuffer = False
            else:
                self.buffer = {}
                cbuff = self.buff_dict[self.classid][self.jobid]['buffer']
                self.isBuffer = True
        else:
            self.buffer = None
            #print (self.classid, self.jobid)
            cbuff = self.buff_dict[self.classid][self.jobid]
            self.isBuffer = False

        self.char_stat = {
                '레벨':self.level, '이름':self.name, '서버':self.server, '모험단':self.advname, 'class':self.classname, '전직':self.jobname, 'ids':(sid, cid), '버퍼여부':self.isBuffer, 'jobid':self.jobid,
                '스공':1, '증댐':0, '크증댐':0, '추댐':0, '속추댐':0,
                '물마독공':0, '힘지':0, '모공':0, '지속댐':0, '증추':0, '크증추':0,
                '패시브':{}, '버프패시브':{}, '변환옵션':[], 'points': 0
            }
        
        #if test_mode is True:
        for slot in self.e_dict['equipment']:
            if 'skin' in slot.keys():
                idx = self.e_dict['equipment'].index(slot)
                del self.e_dict['equipment'][idx]['skin']

        if custom_data is None:
            self.analyze_stat()
        else:
            self.analyze_stat(custom_data['diff'])
            custom_data['char_stat'] = self.char_stat
        self.analyze_sw(cbuff)

        self.char_stat['inventory'] = Inventory(self, self.e_dict, self.c_dict, self.a_dict, self.g_dict, self.t_dict, test_mode = self.test_mode, custom_data = custom_data)
        self.char_stat['skilltree'] = SkillTree(self, self.test_mode)
        self.char_stat['inventory'].bind_skill(self.char_stat['skilltree'])
        self.char_stat['inventory'].analyze_enchants()
        self.char_stat['inventory'].analyze_avatar()
        self.char_stat['inventory'].analyze_flag_and_gem()
        typ, v = self.char_stat['inventory'].get_main_stat()
        #print('마부/아바타/젬 지능', v)
        v = self.calculate_base_stat(v, typ) + self.base_stat
        self.char_stat['inventory'].main_stat = {'type':typ, 'value':v}

        #self.char_stat['enchants']
        invest = self.char_stat['inventory'].enchant

        self.char_stat['invest'] = invest
        self.char_stat['main_stat'] = self.char_stat['inventory'].main_stat

        if self.isBuffer is False:
            elem_enchants = invest['elem']

            maxv = max(elem_enchants.values())
            for e, v in elem_enchants.items():
                if v == maxv:
                    maxe = e

            if maxe == '모든 속성 강화':
                vsum = elem_enchants[maxe]
                maxv = 0
                _maxe = maxe
                for e, v in elem_enchants.items():
                    if e == _maxe:
                        continue

                    if v > maxv:
                        maxv = v
                        maxe = e
                
                vsum += int(maxv / 2)

                p = (float(vsum) / 124.0) * 100
            else:
                vsum = maxv + elem_enchants['모든 속성 강화']

                p = (float(vsum) / 138.0) * 100

            stat_enchants = invest['stat']

            maxv = max(stat_enchants.values())

            p += (float(maxv) / 800) * 100

            dam_enchants = invest['dam']

            maxv = max(dam_enchants.values())

            p += (float(maxv) / 240) * 100
        
        else: #buffer enchant point
            stat_enchants = invest['stat']

            maxv = max(stat_enchants.values())

            p = (float(maxv + 1600) / 3200) * 365

        self.char_stat['points'] += p

        if self.buffer is not None:
            sw_a_dict, sw_c_dict = self.get_sw_dicts(sid, cid)
            sw_e_dict = self.sw_dict['skill']['buff']

            e_add_list = []
            if sw_e_dict.get('equipment') is None:
                sw_e_dict['equipment'] = self.e_dict['equipment']
            else:
                for item in self.e_dict['equipment']:
                    slot = item['slotName']
                    isExist = False
                    for sw_item in sw_e_dict['equipment']:
                        sw_slot = sw_item['slotName']
                        if sw_slot == slot:
                            isExist = True
                            break
                    if isExist is False:
                        e_add_list.append(item)

            sw_e_dict['equipment'] += e_add_list

            a_add_list = []
            if sw_a_dict.get('avatar') is None:
                sw_a_dict['avatar'] = self.a_dict['avatar']
            else:
                for item in self.a_dict['avatar']:
                    slot = item['slotName']
                    isExist = False
                    for sw_item in sw_a_dict['avatar']:
                        sw_slot = sw_item['slotName']
                        if sw_slot == slot:
                            isExist = True
                            break
                        
                    if isExist is False:
                        a_add_list.append(item)

            sw_a_dict['avatar'] += a_add_list

            buff30_base, buff50_base, buff_name, apo_name, passive_name, buff_aura_name = self.get_buff_info()
 
            self.buffer['inventory'] = Inventory(self, sw_e_dict, sw_c_dict, sw_a_dict, self.g_dict, self.t_dict)
            self.buffer['skilltree'] = SkillTree(self, self.test_mode)
            self.buffer['inventory'].bind_skill(self.buffer['skilltree'])
            self.buffer['inventory'].analyze_enchants()
            self.buffer['inventory'].analyze_avatar()
            self.buffer['inventory'].analyze_flag_and_gem()
            typ, v = self.buffer['inventory'].get_main_stat()
            v = self.calculate_base_stat(v, typ) + self.base_stat
            self.buffer['inventory'].main_stat = {'type':typ, 'value':v}

            self.char_stat['skilltree'].buffoption = {'type':'아포', 'name':apo_name, '계수':0, '힘지':1, '암속저':0, '오라':{'name':buff_aura_name, 'value':0}, 'passive':passive_name, 'base':buff50_base, '보조스킬':{}}
            self.buffer['skilltree'].buffoption = {'type':'축', 'name':buff_name,'힘지':1, '물공':1, '마공':1, '독공':1, '암속저':0, '오라':{'name':buff_aura_name, 'value':0}, 'passive':passive_name, 'base':buff30_base}

            self.buffer['inventory'].analyze_talisman()

        self.char_stat['inventory'].analyze_talisman()

        self.char_stat['dicts'] = {
            'equipment': self.e_dict['equipment'],
            'setInfo': self.e_dict['setItemInfo'],
            'creature': self.c_dict['creature'],
            'avatar': self.a_dict['avatar'],
            'flag': self.g_dict['flag'],
            'talismans': self.t_dict['talismans']
        }
        if self.buffer is not None:
            self.char_stat['dicts'].update({
                'sw_equipment': sw_e_dict['equipment'],
                'sw_setInfo': sw_e_dict['setItemInfo'],
                'sw_avatar': sw_a_dict['avatar'],
            })

        self.status = ('ok', None)

    def calculate_buff_score(self):
        add_dam = 0
        add_stat = 0
        for k, v in self.char_stat['버프분석결과']['보조스킬'].items():
            if k in ['신념의 오라', '신실한 열정', '소악마', '그랜드 크로스 크래쉬']:
                add_stat += v
            else:
                add_dam += v

        bless_stat = self.char_stat['버프분석결과']['축']['힘지']['value']
        awk_stat = self.char_stat['버프분석결과']['아포']['value']
        awk_stat2 = self.char_stat['버프분석결과']['아포']['value2']

        final_stat = bless_stat + awk_stat + add_stat
        final_stat2 = bless_stat + awk_stat2 + add_stat

        final_dam = self.char_stat['버프분석결과']['축']['공']['value']
        final_dam += add_dam

        # for scoring
        #bless_stat += add_stat
        #awk_stat += add_stat
                
        deal_ori = 1.31 * (1 + 15750/250) * 2500 * 1.34 * 1.5 * 0.004
        deal = 1.31 * (1+ (15750+ final_stat)/250) * (2500 + final_dam) * 1.34 * 1.5 * 0.004

        """
        a_deal = 1.31 * (1+ (15983+ awk_stat)/250) * (2500 + final_dam) * 1.34 * 1.5 * 0.004

        if self.classname == '프리스트(여)':
            c_deal = 1.31 * (1+ (15983+ (bless_stat * 0.95))/250) * (2600 + final_dam) * 1.34 * 1.5 * 0.004
        elif self.classname == '마법사(여)':
            c_deal = 1.31 * (1+ (15983+ (bless_stat * 0.95))/250) * (2600 + final_dam) * 1.34 * 1.5 * 0.004
        else:
            c_deal = 1.31 * (1+ (15983+ (bless_stat * 0.975))/250) * (2600 + final_dam) * 1.34 * 1.5 * 0.004
        """

        dealp = (deal/100 - 100)

        deal_amp_base = deal/deal_ori

        #print (deal_amp_base * 1.6)

        #cdeal_amp_base = c_deal/deal_ori
        #cdeal_amp = round(((c_deal/deal_ori * 100) - 100) * 700)

        #adeal_amp_base = a_deal/deal_ori
        #adeal_amp = round(((a_deal/deal_ori * 100) - 100) * 700)

        if self.char_stat['inventory'].extra_info['siroco_roxy'] != 0:
            fdam = (final_dam + 2650) * (1 + self.char_stat['inventory'].extra_info['siroco_roxy'] / 100)
        else:
            fdam = final_dam + 2650

        final_score = round((1 + (15000 + final_stat) / 250) * fdam / 10)
        final_score2 = round((1 + (15000 + final_stat2) / 250) * fdam / 10)

        bless_only_stat = bless_stat + add_stat
        bless_score = round((1 + (15000 + bless_only_stat) / 250) * fdam / 10)

        self.char_stat['버프분석결과']['점수표'] = (final_score, dealp, deal, final_score2, bless_score)
        self.char_stat['버프분석결과']['최종버프'] = {'공격력':round(final_dam), '힘/지능':round(final_stat)}

        vsum = (final_score * 2.5 + bless_score * 1.5)/3

        namep = self.char_stat.get('모험가명성')
        if namep is not None:
            self.char_stat['points'] = (namep-6068)/15

        self.char_stat['points'] += vsum / 200

    def deal_to_text(self, g_real_deal):
        g_jo_real = int(g_real_deal / 100000000000000)
        g_2nd_real = int((g_real_deal % 100000000000000)/10000000000) 
            
        if g_jo_real > 0:
            return str(g_jo_real)+'조 '+str(g_2nd_real)+'억'
        else:
            return str(g_2nd_real)+'억'

    def create_epic_report(self, epic_status, prefix, postfix, isBuffer, siroco_status):
        myth_count = epic_status['신화']
        epic_count = epic_status['에픽']
        indo_count = epic_status['지옥파티']
        myth_list = epic_status['신화목록']
        siroco_list = epic_status['시로코목록']
        siroco_count = epic_status['시로코']

        if siroco_count == 4 and siroco_status == 13:
            prefix.append('차단이 필요한 시로코보상 기린')

        if siroco_count >= 10 and siroco_status != 13:
            if siroco_status == 3:
                prefix.append('시로코보상운 없는')
                postfix.append('잔향없찐')
            elif (siroco_status % 10) < 3 and siroco_status >= 10:
                prefix.append('시로코보상운 없는')
                postfix.append('미졸업자')
            else:
                postfix.append('시로코 무료봉사자')
            
        #print('신화목록', myth_list)
        if myth_count == 0:
            if indo_count > 5000:
                postfix.append('아직도 안접고 이걸 보는 대단한 찐신없찐')
            elif indo_count > 4000:
                postfix.append('아무신화나 좀 나오라고 하는 신없찐')
            elif indo_count > 3000:
                postfix.append('분노에 가득찬 신없찐')
            elif indo_count > 2000:
                postfix.append('설마 안나오겠어? 생각하는 신없찐')
            elif indo_count > 1000:
                postfix.append('곧 먹을거라 생각하는 신없찐')
            elif indo_count <= 1000:
                postfix.append('아직은 괜찮은 신없찐')
        
        myth_tier = [0, 0, 0, 0, 0]

        if isBuffer is False:
            for myth in myth_list.keys():
                if myth in ['고대 심연의 로브', '군신의 마지막 갈망', '영원한 나락의 다크버스']:
                    myth_tier[0] += 1
                elif myth in ['영원을 새긴 바다', '차원을 관통하는 초신성', '숙명을 뒤엎는 광란', '결속의 체인 플레이트', '길 방랑자의 물소 코트', '사탄 : 분노의 군주', '작열하는 대지의 용맹', '종말의 역전']:
                    myth_tier[1] += 1
                elif myth in ['낭만적인 선율의 왈츠', '영명한 세상의 순환', '또다른 시간의 흐름', '아린 고통의 비극']:
                    myth_tier[4] += 1
                elif myth in ['대제사장의 예복', '선택이익', '천사의 날개', '라이도 : 질서의 창조자', '시간을 거스르는 자침', '천지에 울려퍼지는 포효', '운명을 거스르는 자']:
                    myth_tier[3] += 1
                else:
                    myth_tier[2] += 1
        else:
            for myth in myth_list.keys():
                if myth in ['숙명을 뒤엎는 광란', '영원히 끝나지 않는 탐구']:
                    myth_tier[0] += 1
                elif myth in ['영원한 나락의 다크버스', '천지에 울려퍼지는 포효', '고대 심연의 로브', '차원을 관통하는 초신성', '수석 집행관의 코트', '시간을 거스르는 자침', '아린 고통의 비극', '새벽을 녹이는 따스함']:
                    myth_tier[1] += 1
                elif myth in ['작열하는 대지의 용맹', '결속의 체인 플레이트', '대 마법사[???]의 로브']:
                    myth_tier[4] += 1
                elif myth in ['생사를 다스리는 그림자의 재킷', '또다른 시간의 흐름', '천사의 날개', '최후의 전술', '웨어러블 아크 팩']:
                    myth_tier[3] += 1
                else:
                    myth_tier[2] += 1

        if myth_tier[0] > 0:
            old_max_tier = 1
        elif myth_tier[1] > 0:
            old_max_tier = 2
        elif myth_tier[2] > 0:
            old_max_tier = 3
        elif myth_tier[3] > 0:
            old_max_tier = 4
        elif myth_tier[4] > 0:
            old_max_tier = 5
        else:
            old_max_tier = 0
        
        new_myth_tier = [0, 0, 0, 0, 0]

        if isBuffer is False:
            for myth in myth_list.keys():
                if myth in ['군신의 마지막 갈망', '영원한 나락의 다크버스', '종말의 역전', '트로피카 : 드레이크', '영원히 끝나지 않는 탐구']:
                    new_myth_tier[0] += 1
                elif myth in ['또다른 시간의 흐름', '시간을 거스르는 자침', '고대 심연의 로브', '영원을 새긴 바다', '숙명을 뒤엎는 광란', '사탄 : 분노의 군주', '작열하는 대지의 용맹', '낭만적인 선율의 왈츠', '천지에 울려퍼지는 포효']:
                    new_myth_tier[1] += 1
                elif myth in ['영명한 세상의 순환', '아린 고통의 비극', '천사의 날개', '수석 집행관의 코트', '최후의 전술']:
                    new_myth_tier[4] += 1
                elif myth in ['대제사장의 예복', '라이도 : 질서의 창조자', '운명을 거스르는 자', '새벽을 녹이는 따스함', '길 방랑자의 물소 코트', '웨어러블 아크 팩', '대 마법사[???]의 로브', '플라즈마 초 진공관']:
                    new_myth_tier[3] += 1
                else:
                    new_myth_tier[2] += 1
        else:
            for myth in myth_list.keys():
                if myth in ['숙명을 뒤엎는 광란', '영원히 끝나지 않는 탐구', '천지에 울려퍼지는 포효', '영원한 나락의 다크버스']:
                    new_myth_tier[0] += 1
                elif myth in ['고대 심연의 로브', '차원을 관통하는 초신성', '시간을 거스르는 자침', '아린 고통의 비극', '새벽을 녹이는 따스함', '운명을 거스르는 자', '수석 집행관의 코트']:
                    new_myth_tier[1] += 1
                elif myth in ['트로피카 : 드레이크', '작열하는 대지의 용맹', '결속의 체인 플레이트', '대 마법사[???]의 로브', '길 방랑자의 물소 코트', '영명한 세상의 순환', '선택이익']:
                    new_myth_tier[3] += 1
                elif myth in ['생사를 다스리는 그림자의 재킷', '선택이익', '천사의 날개', '웨어러블 아크 팩']:
                    new_myth_tier[4] += 1
                else:
                    new_myth_tier[2] += 1

        myth_tier = new_myth_tier

        if myth_tier[0] > 0:
            new_max_tier = 1
        elif myth_tier[1] > 0:
            new_max_tier = 2
        elif myth_tier[2] > 0:
            new_max_tier = 3
        elif myth_tier[3] > 0:
            new_max_tier = 4
        elif myth_tier[4] > 0:
            new_max_tier = 5
        else:
            new_max_tier = 0

        if indo_count < 800 and myth_count >= 1:
            giraffe = False
            for myth, myth_info in myth_list.items():
                if 505 in myth_info['code']:
                    giraffe = True
                    break

            if giraffe is True:
                if sum(myth_tier[0:2]) > 0:
                    prefix.append('차단이 필요한 신화기린')
            else:
                if sum(myth_tier[0:2]) > 0:
                    prefix.append('기도메타 성공한')
                else:
                    prefix.append('기도메타 실패한')

        if old_max_tier - new_max_tier > 1:
            prefix.append('신화 인생 역전한')
        elif old_max_tier - new_max_tier > 0:
            prefix.append('신화 존버 성공한')

        if indo_count >= 5000:
            prefix.append('지혜의 인도에 녹아버린')
        elif indo_count >= 4000:
            prefix.append('지혜의 인도에 미쳐버린')
        elif indo_count >= 3000:
            prefix.append('지혜의 인도가 지겨운')
        elif indo_count >= 2000:
            prefix.append('지혜의 인도에 빠진')

        if sum(myth_tier[0:2]) > 0:
            postfix.append('상급신화 보유자')
        elif sum(myth_tier[2:4]) > 0:
            postfix.append('중급신화 보유자')
        elif myth_tier[4] > 0:  
            postfix.append('하급신화 보유자')

        if myth_count >= 5:
            postfix.append('신화돼지') 
    
    def create_report_explain(self, prefix, postfix, report, server, isBuffer, dealp, deal_jo, deal_uk, report_inc, report_type):
        pcharname = '???'

        if len(postfix) == 0:
            if isBuffer is True:
                postfix.append('버퍼')
            else:
                if self.classTypeNeo is True:
                    postfix.append('딜러')
                else:
                    postfix.append('아무거나')

        prefix_text = ', '.join(prefix)
        postfix_text = ', '.join(postfix)


        if isBuffer is False:
            report_text = prefix_text + ' ' + server + ' - ' + pcharname +'은(는) ' + postfix_text + ' 입니다.' #  + deal_text
        else:
            if deal_jo >= 1:
                d_text = str(deal_jo) + '조 '+ str(deal_uk)
            else:
                d_text = str(deal_uk)
            
            report_text = prefix_text +' '+ server + ' - ' + pcharname + '은(는) '+ postfix_text + '이며 시로코1시 1조 딜러의 딜을 '+ d_text +'억으로 ' + str(round(abs(dealp), 2)) +'% '+report_inc+'시켜 ' + report_type

        report['explain'] = {'full': report_text, 'prefix': prefix, 'postfix': postfix, 'misc':(dealp, deal_jo, deal_uk, report_inc, report_type)}

    def create_report(self):
        prefix = []
        postfix = []
        report = {}

        skilltree = self.char_stat['skilltree']
        inventory = self.char_stat['inventory']
        isBuffer = True if self.buffer is not None else False
        epic_status = self.epic_status
        char_stat = self.char_stat
        server = self.server

        synergy = char_stat.get('시너지옵션')

        if synergy is not None and len(synergy) > 1 and isBuffer is False:
            dam_arr = {'스공':0}
            for key in ['증댐', '크증댐', '추댐', '모공', '물마독공', '힘지']:
                dam_arr[key] = 95

            ori_inc = 1

            for val in dam_arr.values():
                ori_inc *= (1 + val / 100)

            nos_inc = 1
            inc = 1
            stat = 0

            for k, v in synergy.items():
                if k == '시너지스공':
                    inc *= v
                elif k == '스탯':
                    stat += v
                elif k == '시너지':
                    pass
                elif k == '증추':
                    dam_arr['증댐'] += v
                elif k == '크증추':
                    dam_arr['크증댐'] += v
                else:
                    try:
                        dam_arr[k] += v
                    except:
                        pass

            for k, val in dam_arr.items():
                inc *= (1 + val / 100)
                nos_inc *= (1 + val / 100)
            
            deal_ori = (1 + 50000/250) * ori_inc
            deal = (1 + (50000 + stat)/250) * inc
            deal_nos = (1 + (50000 + stat)/250) * nos_inc

            sinc = str(round((deal/deal_ori - 1)*100, 2)) + '%'
            dinc = str(round((deal_nos/deal_ori - 1) * 100, 2)) + '%'

            #print (sinc, dinc)
            char_stat['시너지력'] = {'딜러': dinc, '시너지': sinc}

            """
            print(nos_inc/ori_inc)

            final_score = round((1 + (85000) / 250) * (5650 / 10))
            final_score2 = round((1 + (85000 + stat) / 250) * (5650 * (nos_inc/ori_inc)) / 10)

            final_score = round((1 + (50000) / 250) * (4650 / 10))
            final_score2 = round((1 + (50000 + stat) / 250) * (4650 * (nos_inc/ori_inc)) / 10)


            #final_score2 = round((1 + (15000 + stat) / 250) * fdam / 10)

            print(final_score2 / final_score)
            """


        if isBuffer is False:
            dam_arr = {}
            for key in self.char_stat.keys():
                if key in ['증댐', '크증댐', '추댐', '모공', '물마독공', '힘지']:
                    dam_arr[key] = char_stat[key]
                        
            dam_std = np.std(list(dam_arr.values()))
            #print (dam_std)
            if dam_std > 30:
                key_max = max(dam_arr.keys(), key=(lambda k: dam_arr[k]))
                
                only_one = True
                for k in dam_arr.keys():
                    if k == key_max:
                        continue

                    if dam_arr[key_max] - dam_arr[k] < 50:
                        only_one = False
                        break

                if only_one is True:
                    if key_max[-1] == '지':
                        prefix.append(key_max + '가 넘쳐흐르는')
                    else:
                        prefix.append(key_max + '이 넘쳐흐르는')
            elif dam_std < 10:
                postfix.append('완벽주의자')

            report['옵션밸런스'] = round(100 - dam_std, 2)

            si = None
            if self.classTypeNeo is True:
                awkact = skilltree.skill_enchant['100']
                if len(awkact['actives']) > 0:
                    si = awkact['actives'][0]
                    blv = 2
                    mfact = 2.1
                    afact = 1.8
                
            if si is None:
                awkact = skilltree.skill_enchant['85']
                si = awkact['actives'][0]
                blv = 3
                mfact = 2.8
                afact = 2.5

            if si[2] >= blv and awkact['dam']*si[0]['dam']> mfact:
                prefix.append('각성기에 미쳐버린')
            elif si[2] >= blv and awkact['dam']*si[0]['dam'] > afact:
                prefix.append('각성기에 매료된')

            act_cool_mean = skilltree.inner_data['평균쿨감']

            if 0.72 < act_cool_mean <= 0.8:
                postfix.append('쿨감 빌런')
            elif 0.64 < act_cool_mean <= 0.72:
                postfix.append('쿨감 성애자')
            elif act_cool_mean <= 0.64:
                postfix.append('쿨감 변태')

            if self.char_stat.get('속강딜증가') > 230:
                postfix.append('속강빌런')
        
            if self.char_stat['공격속도'] < 80:
                if self.char_stat['캐스팅속도'] <= 80:
                    prefix.append('묵직한')
                elif char_stat['캐스팅속도'] >= 150:
                    prefix.append('난사하는')
            elif self.char_stat['공격속도'] >= 120:
                prefix.append('몰아치는')
     
            if self.char_stat['이동속도'] <= 65:
                postfix.append('거북이')
            elif self.char_stat['이동속도'] >= 105:
                postfix.append('번개발')

            g_real_deal = self.char_stat['시로코분석결과']['그로기딜']['총합딜']
     
            report['시로코1시딜'] = g_real_deal

            g_score = self.char_stat['시로코분석결과']['그로기딜']['점수']
            c_score = self.char_stat['시로코분석결과']['지속딜']['점수']
            report['점수표'] = self.char_stat['시로코분석결과']['점수표']
            report['오즈마점수표'] = self.char_stat['오즈마분석결과']['점수표']

            report['점수표']['총점'] = round(g_real_deal)
            report['점수표']['text'] = self.deal_to_text(g_real_deal)
            report['점수표']['25c'] = self.deal_to_text(self.char_stat['시로코분석결과']['정자극딜']['총합딜'])
            report['점수표']['40'] = self.deal_to_text(self.char_stat['시로코분석결과']['지속딜']['총합딜'])
            report['점수표']['40c'] = self.deal_to_text(self.char_stat['시로코분석결과']['지속정자극딜']['총합딜'])

            report['오즈마점수표']['no'] = self.deal_to_text(self.char_stat['오즈마분석결과']['40초딜']['총합딜'])
            report['오즈마점수표']['yes'] = self.deal_to_text(self.char_stat['오즈마분석결과']['40초정자극딜']['총합딜'])

            """
            if g_score > c_score*1.05:
                postfix.append('폭딜러')
            elif g_score*1.05 < c_score:
                postfix.append('지딜러')
            else:
                postfix.append('멀티플레이어')
            """
        else:
            buff30_dam = round(self.char_stat['버프분석결과']['축']['공']['value'])
            buff30_stat = round(self.char_stat['버프분석결과']['축']['힘지']['value'])
            if self.classname in ['마법사(여)', '프리스트(여)']:
                add_stat = round(sum(list(self.char_stat['버프분석결과']['보조스킬'].values())))
            else:
                try:
                    add_stat = round(self.char_stat['버프분석결과']['보조스킬']['신념의 오라'])
                except:
                    add_dam = 0
                try:
                    add_dam = round(self.char_stat['버프분석결과']['보조스킬']['크로스 크래쉬'])
                except:
                    add_dam = 0
            buff50_stat = round(self.char_stat['버프분석결과']['아포']['value'])

            if self.classname == '프리스트(여)':
                stat_buff_icons = {'icons':['용맹의 축복', '용맹의 아리아'], 'value':buff30_stat}
                stat_apo_icons = {'icons':['크럭스 오브 빅토리아', '라우스 디 안젤루스'], 'value':buff50_stat}
                stat_aura_icons = {'icons':['그랜드 크로스 크래쉬', '신실한 열정'], 'value':add_stat}
                dam_buff_icons = {'icons':['용맹의 축복', '용맹의 아리아'], 'value':buff30_dam}
                dam_aura_icons = None

                stat_max_icon = 2
                dam_max_icon = 2
                dam_y_margin = 1

            elif self.classname == '프리스트(남)':
                stat_buff_icons = {'icons':['영광의 축복', '디바인 퍼니쉬먼트'], 'value':buff30_stat}
                stat_apo_icons = {'icons':['아포칼립스', '디바인 퍼니쉬먼트', '최후의 심판'], 'value':buff50_stat}
                stat_aura_icons = {'icons':['신념의 오라'], 'value':add_stat}
                dam_buff_icons = {'icons':['영광의 축복', '디바인 퍼니쉬먼트'], 'value':buff30_dam}
                dam_aura_icons =  {'icons':['크로스 크래쉬'], 'value':add_dam}

                stat_max_icon = 3
                dam_max_icon = 2
                dam_y_margin = 1
            else:
                stat_buff_icons = {'icons':['금단의 저주', '데스티니 퍼펫', '편애'], 'value':buff30_stat}
                stat_apo_icons = {'icons':['마리오네트', '종막극'], 'value':buff50_stat}
                stat_aura_icons = {'icons':['소악마'], 'value':add_stat}
                dam_buff_icons = {'icons':['금단의 저주', '데스티니 퍼펫', '편애'], 'value':buff30_dam}
                dam_aura_icons = None

                stat_max_icon = 2
                dam_max_icon = 2
                dam_y_margin = 1

            stat_icon_list = (stat_apo_icons, stat_buff_icons, stat_aura_icons)
            dam_icon_list = (dam_buff_icons, dam_aura_icons)
            icon_info = (stat_max_icon, dam_max_icon, dam_y_margin)

            report['버프정보'] = (stat_icon_list, dam_icon_list, icon_info)

            dealp = self.char_stat['버프분석결과']['점수표'][1]

            if (dealp < 0):
                report_inc = '감소'
                if 0 >= dealp > -10:
                    report_type = '약화 시킵니다.'
                if -10 >= dealp > -20:
                    report_type = '힘이 빠지게 합니다.'
                elif -20 >= dealp > -30:
                    report_type = '병들게 합니다.'
                elif -30 >= dealp > -40:
                    report_type = '무기대신 숟가락을 쥐어줍니다.'
                elif -40 >= dealp > -50:
                    report_type = '적을 응원합니다.'
                elif dealp <= -50:
                    report_type = '있으나마나 합니다.'

            else:
                report_inc = '증가'
                if dealp <= 5:
                    report_type = '1인분하게 합니다.'
                elif 5 < dealp <= 10:
                    report_type = '응원합니다.'
                elif 10 < dealp <= 20:
                    report_type = '채찍질 합니다.'
                elif 20 < dealp <= 30:
                    report_type = '싸울수 있는 힘을 줍니다.'
                elif 30 < dealp <= 40:
                    report_type = '강력한 힘을 느끼게 합니다.'
                elif 40 < dealp <= 50:
                    report_type = '최강의 전사를 만듭니다.'
                elif 50 < dealp <= 60:
                    report_type = '신의 기운을 느끼게 합니다.'
                elif 60 < dealp <= 80:
                    report_type = '신의 가호를 받게 합니다.'
                elif 80 < dealp <= 100:
                    report_type = '신의 능력을 갖게 합니다.'
                elif 100 < dealp <= 120:
                    report_type = '신과 대등한 힘을 부여합니다.'
                elif 120 < dealp:
                    report_type = '신을 초월한 존재를 만듭니다'


            deal = self.char_stat['버프분석결과']['점수표'][2]

            deal_base = int(deal)/10000
            deal_jo = math.ceil(deal_base) - 1
            deal_uk = int(deal)%10000

            report['버프점수표'] = self.char_stat['버프분석결과']['점수표']
            
        wep_reinforce = inventory.weapon_info['reinforce']
        avg_reinforce = inventory.inner_data['평균증폭수치'] 
        remodel_count = inventory.inner_data['산물장착수']
        high_remodel = inventory.inner_data['최대개조수치']
        max_reinforce = inventory.inner_data['최대증폭수치']

        if isBuffer is True:
            avg_reinforce += self.buffer['inventory'].inner_data['평균증폭수치']
            avg_reinforce /= 2

            max_reinforce = max(max_reinforce, self.buffer['inventory'].inner_data['최대증폭수치'])
        else:
            dealp = 0
            deal_jo = 0
            deal_uk = 0
            report_inc = ''
            report_type = ''

        self.char_stat['avg_dim'] = avg_reinforce

        if 9 < avg_reinforce <= 10:
            prefix.append('증폭을 꿈꾸는')
        elif 10 < avg_reinforce <= 11:
            prefix.append('증폭에 입문한')
        elif 11 < avg_reinforce <= 12:
            prefix.append('증폭에 빠져버린')
        elif 12 < avg_reinforce <= 13:
            prefix.append('증폭에 매혹된')
        elif avg_reinforce > 13:
            prefix.append('증폭에 미쳐버린')

        if wep_reinforce == 13:
            prefix.append('분홍빛이 감도는')
        elif wep_reinforce == 14:
            prefix.append('분홍빛이 반짝이는')
        elif wep_reinforce == 15:
            prefix.append('황금빛이 눈부신')
        elif wep_reinforce > 15:
            prefix.append('황금빛을 찬란하게 발하는')

        if max_reinforce == 13:
            postfix.append('증폭의 승리자')
        elif max_reinforce == 14:
            postfix.append('증폭의 정복자')
        elif max_reinforce == 15:
            postfix.append('증폭의 신')

        if 2<=remodel_count <3:
            postfix.append('산물빌런')
        elif remodel_count >= 3:
            postfix.append('산물성애자')

        if high_remodel is True:
            prefix.append('기름냄새가 나는')

        #epic_status
        if epic_status is not None:
            self.create_epic_report(epic_status, prefix, postfix, isBuffer, self.char_stat['siroco_status'])

        self.create_report_explain(prefix, postfix, report, server, isBuffer, dealp, deal_jo, deal_uk, report_inc, report_type)

        return report


