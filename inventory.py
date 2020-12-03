from json import loads
import json
import numpy as np
from parse import parse, compile
import math
import re
import copy

from skilltree import SkillTree
from libutil import LibUtil as myutil

item_stat_type = ["이동속도", "공격속도", "물리크리티컬히트", "마법크리티컬히트", "모든속성강화", "모든속성저항", "캐스트속도"]
stat_type = ['힘', '지능', '체력', '정신력']
stat_conv = {'힘':'힘', '지':'지능', '체':'체력', '정':'정신력'}
dam_type = ['물리', '마법', '독립']
speed_type = ['공격', '이동', '캐스팅']
 

emblem_type = {'찬란한':{'붉은빛':25, '옐로우':15, '그린':15, '듀얼':15},
               '화려한':{'붉은빛':17, '옐로우':10, '그린':10, '듀얼':10},
               '빛나는':{'붉은빛':10}}
emblem_type2 = {'찬란한':{'녹색빛':3.0, '듀얼':1.5},
                '화려한':{'녹색빛':2.2, '듀얼':1.1},
                '빛나는':{'녹색빛':1.2}}
emblem_type3 = {'찬란한':{'푸른빛':1.5, '노란빛':1.5, '듀얼':0.8},
                '화려한':{'푸른빛':1.1, '노란빛':1.1, '듀얼':0.6},
                '빛나는':{'푸른빛':0.6, '노란빛':0.6}}
emblem_type4 = {'찬란한':{'노란빛':2.2, '듀얼':1.1},
                '화려한':{'노란빛':1.6, '듀얼':0.8},
                '빛나는':{'노란빛':0.9}}

elem_type = ['화속성', '명속성', '수속성', '암속성']

amplify_effect = {'95':[7, 9, 11, 13, 15, 19, 23, 28, 32, 34, 42, 76, 112, 148, 235, 324, 413,],
                  '100':[7, 10, 12, 14, 16, 20, 24, 28, 33, 35, 44, 79, 116, 153, 243, 335, 433] }
#myth 9(38) - 10(47) -> 11(85) - 12(124)  15(358)
substone_effect = {'95':[0, 1, 3, 5, 7, 9, 11, 18, 21, 24, 27, 50, 76, 101, 152, 212, 271,],
                  '100':[0, 1, 3, 5, 7, 9, 11, 19, 22, 25, 28, 53, 76, 106, 159, 221, 285,]}
earing_effect = {'95':[0, 1, 3, 6, 9, 14, 20, 27, 32, 36, 46, 73, 109, 146, 219, 305, 390,],
                 '100':[0, 1, 3, 6, 10, 15, 21, 29, 34, 38, 50, 82, 123, 161, 237, 326, 420,]} 

flag_effect = [0, 4, 5, 6, 7, 9, 11, 13, 14, 15, 17, 27, 54, 108, 216]

wep_refine_effect = [0, 4, 6, 8, 12, 17, 27, 37, 52]

mastery_conv = {'상의':0.6, '하의':0.5, '머리어깨':0.4, '신발':0.3, '허리':0.2}

elemental_kings = ['강인한 이그니스', '명석한 아쿠아젤로', '강인한 테네브리스', '명석한 루메누스', '초열의 주술사 미호', '빙설의 마법사 루나', '고대의 용사 리처드', 'SD 팩', '쁘띠 바스테트', '쁘띠 샴']

class Inventory():
    item_db = None
    set_db = None
    talisman_db = None
    buffer_talisman_db = None

    @classmethod
    def initstatic(cls):
        with open("./item_db.json", "r") as f:
            cls.item_db = json.load(f)

        with open("./set_db.json", "r") as f:
            cls.set_db = json.load(f)

        with open('./talisman_db.json', "r") as f:
            cls.talisman_db = json.load(f)
       
        with open('./buff_talisman_db.json', "r") as f:
            cls.buffer_talisman_db = json.load(f)

    def __init__(self, e_dict, c_dict, a_dict, g_dict, t_dict, test_mode = False):
        self.test_mode = test_mode
        self.debug_list = {}
        self.item_db_list = []
        self.inner_data = {}

        try:
            _c_dict = {
                    'itemName':c_dict['creature']['itemName'],
                    'slotName':'크리처',
                    'itemId':c_dict['creature']['itemId'],
                    'itemRarity':c_dict['creature']['itemRarity'],
                    'amplificationName':None,
                    'reinforce':0,
                    'refine':0
                    }
            e_dict['equipment'].append(_c_dict)

            if c_dict['creature']['itemName'] in elemental_kings:
                self.inner_data['정령왕'] = True
                #print('정령왕', type(self))
        except:
            pass

        if e_dict.get('setItemInfo') is None:
            sw_iid_list = []
            for item in e_dict['equipment']:
                if item['slotName'] not in ['무기', '칭호', '크리처']:
                    sw_iid_list.append(item['itemId'])

            if len(sw_iid_list) > 0:
                sw_iids = ','.join(sw_iid_list)
                sw_set_info = myutil.load_api('custom/equipment/setitems?itemIds='+sw_iids+'&')

                if self.test_mode is True:
                    with open("sw_set_info.json", "w") as f:
                        json.dump(sw_set_info, f)
                
                e_dict['setItemInfo'] = sw_set_info['setItemInfo']
            else:
                e_dict['setItemInfo'] = []

        self.e_dict = e_dict
        self.c_dict = c_dict
        self.a_dict = a_dict
        self.g_dict = g_dict
        self.t_dict = t_dict

        self.weapon_info = {'type':None}
        for e_list in e_dict['equipment']:
            if e_list['slotName'] == '무기':
                self.weapon_info['type'] = e_list['itemTypeDetail']
                break

        self.enchant = {
            'stat':{'힘': 0, '지능' : 0, '체력': 0, '정신력':0},
            'elem':{'화속성강화':0, '명속성강화':0, '수속성강화':0, '암속성강화':0, '모든 속성 강화':0},
            'dam':{'물리 공격력':0, '마법 공격력':0, '독립 공격력':0},
            'critical':{'물리 크리티컬 히트':0.0, '마법 크리티컬 히트':0.0},
            'speed':{'공격속도':0.0, '이동속도':0.0, '캐스트속도':0.0},
            'res':{'암속성저항':0, '모든 속성 저항':0}
        }

    def calculate_option(self, opt, key, r, vmax, name):
        if isinstance(opt[key], int) or isinstance(opt[key], float):
            val = opt[key] * r
            if vmax is not None:
                val = min(val, vmax)
        elif isinstance(opt[key], list) and vmax is not None:
            val = vmax
        elif key == '스킬':
            val = opt[key]
        else: 
            #print("#CHECK#", opt, key, opt[key])
            return
            #raise Exception

        stat_key = None
        char_stat = self.owner.char_stat
        skill_enchant = self.skilltree.skill_enchant

        if key == '속저':
            if opt['증감'] in ['감', '-']:
                f = -1
            elif opt['증감'] in ['증', '+']:
                f = 1

            for key in opt.keys():
                if key.find('속성종류') >= 0:
                    stat_key = opt[key]+'속성저항'
                    try:
                        char_stat[stat_key] += val * f
                    except:
                        return
                       
        elif key == '모속저':
            diff = opt.get('증감')
            if diff is None:
                f = 1
            elif diff in ['감', '-']:
                f = -1   
            elif diff in ['증', '+']:
                f = 1

            for elem in elem_type:
                stat_key = elem+'저항'
                char_stat[stat_key] += val * f
        elif key == '속강':
            if opt['속성종류'].find('모든') >= 0:
                for elem in elem_type:
                    stat_key = elem+'강화'
                    char_stat[stat_key] += val
                stat_key = '모든속성강화'
            else:
                stat_key = opt['속성종류']+'속성강화'
                char_stat[stat_key] += val

        elif key  == '모속강' in opt.keys():
            for elem in elem_type:
                stat_key = elem+'강화'
                char_stat[stat_key] += val
            """
        elif key == '피격뎀':
            diff = opt.get('증감')
            if diff is None:
                f = 1 + val/100
            elif diff in ['감', '-']:
                #print (name, val)
                f = 1 - val/100
            elif diff in ['증', '+']:
                f = 1 + val/100

            if '피격뎀' in char_stat.keys():
                char_stat['피격시데미지'] *= f
            else:
                char_stat['피격시데미지'] = f
            """
        elif key == '증댐' or key == '크증댐':
            char_stat[key] = max(char_stat[key], val)
        elif key == '스킬':
            jobinfo, slist = opt[key]
            if jobinfo['job'] != '공통':
                if jobinfo['jid'] != self.owner.classid:
                    return
            
            for skill in slist:
                if 'minLevel' in skill.keys():
                    minl = skill['minLevel']
                    maxl = skill['maxLevel']
                    
                    damup = skill.get('damup')
                    damdown = skill.get('damdown')
                    coolup = skill.get('coolup')
                    cooldown = skill.get('cooldown')
                    coolrecover = skill.get('coolrecover')
                    lvup = skill.get('value')

                    for cur in range(minl, maxl+1):
                        if str(cur) in skill_enchant.keys():
                            if damup is not None:
                                damup = float(damup)
                                skill_enchant[str(cur)]['dam'] *= (1 + damup/100)
                            elif damdown is not None:
                                damdown = float(damdown)
                                skill_enchant[str(cur)]['dam'] *= (1 - damdown/100)

                            if coolup is not None:
                                coolup = float(coolup)
                                skill_enchant[str(cur)]['cool'] *= (1 + coolup/100)
                                if str(cur) in self.inner_data['쿨감목록'].keys():
                                    self.inner_data['쿨감목록'][str(cur)] *= (1 + coolup/100)

                            elif cooldown is not None:
                                cooldown = float(cooldown)
                                skill_enchant[str(cur)]['cool'] *= (1 - cooldown/100)
                                if str(cur) in self.inner_data['쿨감목록'].keys():
                                    self.inner_data['쿨감목록'][str(cur)] *= (1 - cooldown/100)

                            if coolrecover is not None:
                                coolrecover = float(coolrecover)
                                skill_enchant[str(cur)]['cool'] /= (1 + coolrecover/100)
                                if str(cur) in self.inner_data['쿨감목록'].keys():
                                    self.inner_data['쿨감목록'][str(cur)] /= (1 + coolrecover/100)

                            if lvup is not None:
                                if vmax is not None:
                                    r = min(vmax, r)
                                skill_enchant[str(cur)]['level'] += int(lvup * r)

                elif 'skillId' in skill.keys():
                    sn = skill['name']
                    skid = skill['skillId']

                    damup = skill.get('damup')
                    damdown = skill.get('damdown')
                    coolup = skill.get('coolup')
                    cooldown = skill.get('cooldown')
                    coolrecover = skill.get('coolrecover')
                    lvup = skill.get('value')

                    #print (sn, skid, lvup)
                    if lvup is not None and isinstance(lvup, int):
                        self.skilltree.increase_skill_level('skills', sn, lvup * r)
                        self.skilltree.increase_skill_level('actives', sn, lvup * r)
                    elif sn == '히트엔드' and lvup.find('연계점수') >= 0: 
                        self.inner_data['히트엔드추가'] = 0.4

                    skill_instance = self.skilltree.get_skill_instance('actives', sn)
                    if skill_instance is not None:
                        if damup is not None:
                            skill_instance['dam'] *= (1 + damup/100)
                        elif damdown is not None:
                            skill_instance['dam'] *= (1 - damup/100)

                        if coolup is not None:
                            skill_instance['cool'] *= (1 + coolup/100)
                        elif cooldown is not None:
                            skill_instance['cool'] *= (1 - cooldown/100)

                        if coolrecover is not None:
                            skill_instance['cool'] /= (1 + coolrecover/100)
                        
        elif key == '스공':
            char_stat[key] *= (1 + (val)/100)
            """
        elif key == '지속댐':
            char_stat[key] += val
            t = opt['지속']
            dps = val / t
            if '지속댐dps' in char_stat.keys():
                char_stat['지속댐dps'] += dps
            else:
                char_stat['지속댐dps'] = dps

            if '지속댐minsec' in char_stat.keys():
                char_stat['지속댐minsec'] = min(char_stat['지속댐minsec'], t)
            else:
                char_stat['지속댐minsec'] = t

            if '지속댐maxsec' in char_stat.keys():
                char_stat['지속댐maxsec'] = max(char_stat['지속댐maxsec'], t)
            else:
                char_stat['지속댐maxsec'] = t
            """
        elif key in ['힘지', '물마독공', '모공', '크증추', '증추', '추댐', '물리크리티컬', '마법크리티컬', '지속댐']:
            char_stat[key] += val

        if key in ['공속', '공이캐속', '공이속', '공속감소']:
            if key.find('감소') >= 0:
                f = -1
            else:
                f = 1

            char_stat['공격속도'] += val * f

        
        if key in ['이속', '공이캐속', '공이속', '이속감소']:
            if key.find('감소') >= 0:
                f = -1
            else:
                f = 1

            char_stat['이동속도'] += val * f
   
        if key in ['캐속', '공이캐속', '캐속감소']:
            if key.find('감소') >= 0:
                f = -1
            else:
                f = 1

            char_stat['캐스팅속도'] += val * f

        if key.find('깡') >= 0:
            if key.find('스탯') >= 0:
                #print ('지능증가', '아이템옵션:' + name, val)
                self.main_stat['value'] += val
            elif key.find('힘지') >= 0:
                if self.main_stat['type'] == '지능':
                   #print ('지능증가', '아이템옵션:' + name, val)
                   self.main_stat['value'] += val

        if stat_key is not None:
            key = stat_key
        try:
            self.debug_list[key].append((name, val))
        except:
            self.debug_list[key] = [(name, val)]

    def handle_item_options(self):
        #prepare to some items - middle handling option

        item_db_list = self.item_db_list
        classname = self.owner.classname
        jobname = self.owner.jobname
        char_stat = self.owner.char_stat

        self.inner_data['쿨감목록'] = {'15':1, '20':1, '25':1, '30':1, '35':1, '40':1, '45':1, '65':1, '70':1, '75':1, '80':1, '95':1} 
        self.inner_data['주사위최솟값'] = 1
        self.inner_data['베테랑신화'] = False
        self.inner_data['역작신화'] = False
        self.inner_data['마을적용패시브'] = 0
        def_count = 0
        for eitem in item_db_list:
            ename = eitem['name']
            if ename == '운명을 거스르는 자':
                self.inner_data['주사위최솟값'] = 2
            elif ename == '최후의 전술':
                self.inner_data['베테랑신화'] = True
            elif ename == '천상의 날개':
                self.inner_data['역작신화'] = True
            elif ename == '융합된 자연의 핵' or ename == '개악 : 지옥의 길 세트(3)':
                self.inner_data['마을적용패시브'] = 1 if '마을적용패시브' not in self.inner_data.keys() else 2
            elif ename == '시로코2':
                for opt in eitem['options']:
                    if '수문장' in list(opt.keys()):
                        def_count += 1
            
        #print('수문장', def_count)

        if def_count > 0:
            elem_list = [char_stat['화속성강화'], char_stat['명속성강화'], char_stat['수속성강화'], char_stat['암속성강화']]
            elemsum = 0
            emax = max(elem_list)
            for elem in elem_list:
                e = max(elem + 30 * def_count, emax)
                if emax - elem >= 170:
                    e += 15

                #print (e)

                elemsum += e

            #print(elemsum / 4)
            char_stat['화속성강화'] = char_stat['명속성강화'] = char_stat['수속성강화'] = char_stat['암속성강화'] = elemsum/4
                
        v = None
        defer_list1 = []
        defer_list2 = []
        for item_db in item_db_list:
            iname = item_db['name']

            if iname in ['전장의 매', '데파르망', '퀘이크 프론', '전쟁의 시작', '베테랑 군인의 정복 세트(5)']:
                if self.inner_data['베테랑신화'] is False and len(item_db['options']) > 0:
                    opt = item_db['options'][0]
                    optkey = list(opt.keys())[0]
                    opt[optkey] -= 1
            elif iname == '오퍼레이션 델타':
                if self.inner_data['베테랑신화'] is False and len(item_db['options']) > 0:
                    opt = item_db['options'][0]
                    optkey = list(opt.keys())[0]
                    opt[optkey] -= 4

            elif iname == '전설의 대장장이 - 역작 세트(3)':
                if self.inner_data['역작신화']:
                    item_db['options'][1]['스킬'][1][0]['cooldown'] *= 1.5
                    item_db['options'][1]['스킬'][1][1]['cooldown'] *= 1.5

            for opt in item_db['options']:
                r = 1
                if 'condition' in opt.keys():
                    condition = opt['condition']
                    if condition['type'] == '암속저':
                        defer_list1.append((opt, iname))
                        continue

                    if condition['type'] == '착용':
                        req = condition['required']
                        matched = 0
                        for rname in req:
                            rname=rname.replace('\'','')
                            for item in item_db_list:
                                ename = item.get('name')

                                if ename is not None:
                                    ename = ename.replace(' ', '')
                                else:
                                    continue

                                if ename == rname:
                                    matched += 1

                        if matched < len(req):
                            #print('착용조건 만족x', str(req), opt)
                            continue
                    elif condition['type'] == '개조':
                        step = condition['per-step']
                        for item in self.e_dict['equipment']:
                            ename = item.get('itemName')
                            if ename is not None:
                                ename = ename.replace(' ', '')
                            else:
                                continue

                            if ename == iname.replace(' ',''):
                                r = item["reinforce"]
                                break
                        if r == 0:
                            continue
                        r /= step

                    elif condition['type'] == '강화증폭':
                        v = condition['per-val']
                        rmax = condition['max']
                        for item in self.e_dict['equipment']:
                            ename = item.get('itemName')
                            if ename is not None:
                                ename = ename.replace(' ', '')
                            else:
                                continue

                            if ename == iname.replace(' ',''):
                                try:
                                    r = min(int(rmax), item["reinforce"])
                                except:
                                    r = min(int(rmax[:-1]), item["reinforce"])
                                break

                        if r == 0:
                            continue
                    elif condition['type'] == '주사위':
                        v = 1
                        dice = condition['cond']
                        dice_min = self.inner_data['주사위최솟값']
                        if dice == '짝수':
                            r = 3 / ( 6 - dice_min)
                        elif dice == '2이상':
                            r = 5 / ( 6 - dice_min)
                        elif dice == '6':
                            r = 1 / ( 6 - dice_min)
                        elif dice == '4또는5':
                            r = 2 / ( 6 - dice_min)

                elif 'step' in opt.keys():
                    step = opt['step']
                    reopt = opt['options']

                    for item in self.e_dict['equipment']:
                        ename = item.get('itemName')
                        if ename is not None:
                            ename = ename.replace(' ', '')
                        else:
                            continue

                        if ename == iname.replace(' ',''):
                            r = item["reinforce"]
                            break

                    if r < step:
                        continue

                    for ro in reopt:
                        rolist = list(ro.keys()) 
                        if len(rolist) == 0:
                            continue

                        rekey = rolist[0]
                        if rekey == '속추댐':
                            defer_list1.append((ro, iname))
                            #print ('속추댐', ro)
                            continue
                        v = ro[rekey]
                        self.calculate_option(ro, rekey, 1, None, iname)

                    continue

                if '속추댐' in opt.keys():
                    defer_list1.append((opt, iname))
                    continue

                if '수문장' in opt.keys():
                    continue

                for key in opt.keys():
                    self.calculate_option(opt, key, r, None, iname)

        self.skilltree.apply_baselevel()

        buff_option = None
        buff_type = None
        if self.owner.buffer is not None:
            main_stat_type = self.main_stat['type']

            buff_option = self.skilltree.buffoption 
            buff_type = buff_option['type']
            buff_name = buff_option['name']
            passive_name = buff_option['passive']
            aura_name = buff_option['오라']['name']

            for item_db in item_db_list:
                iname = item_db['name']

                status = item_db.get('status')
                if status is not None:
                    for statv in status:
                        if statv['name'] == main_stat_type:
                            self.main_stat['value'] += statv['value']
                            #if buff_type == '아포':
                                #print('지능증가', '아이템스탯:'+iname, statv['value'])
                        elif statv['name'] == '암속성저항':
                            self.skilltree.buffoption['암속저'] += statv['value']

                buffopts = item_db.get('buffopts')

                if buffopts is None:
                    continue

                for bo in buffopts:
                    for key, val in bo.items():
                        if buff_type == '축':
                            if key in ['축물마독', '축물공']:
                                buff_option['물공'] *= (1 + val/100)
                            
                            if key in ['축물마독', '축마공']:
                                buff_option['마공'] *= (1 + val/100)

                            if key in ['축물마독', '축독공']:
                                buff_option['독공'] *= (1 + val/100)

                            elif key == '축힘지':
                                buff_option['힘지'] *= (1 + val/100)
                                #print('축힘지', buff_type, iname, (1 + val/100), buff_option['힘지'], buff_option['type'])


                            elif key == '축레벨':
                                self.skilltree.increase_skill_level('skills', buff_name, int(val), req = 30)
                                #print ("축레벨링", iname, val)
                        else:
                            if key == '포계수':
                                buff_option['계수'] += val
                            
                            elif key == '포힘지':
                                buff_option['힘지'] *= (1 + val/100)
                            
                            elif key == '포레벨':
                                self.skilltree.increase_skill_level('skills', buff_name, int(val), req = 50)

                        if classname == '프리스트(여)':
                            if key in ['지능', '라핌지능']:
                                self.main_stat['value'] += int(val)
                            elif key == '지능오라':
                                buff_option['오라']['value'] += val

                        elif classname == '마법사(여)':
                            if key in ['지능', '카테지능']:
                                self.main_stat['value'] += val
                                #if buff_type  == '아포':
                                    #print('지능증가', '버퍼옵션:'+iname, val)

                            elif key == '지능오라':
                                buff_option['오라']['value'] += val

                        elif classname == '프리스트(남)':
                            if key == '체력':
                                self.main_stat['value'] += val
                                #if buff_type  == '아포':
                                    #print('지능증가', '버퍼옵션:'+iname, val)

                            elif key == '체력오라':
                                buff_option['오라']['value'] += val
                        
                        if key == '패시브레벨':
                            #print('패시브레벨증가', iname, val)
                            if iname == '신화':
                               self.skilltree.increase_skill_level('skills', passive_name, int(val), req = 15, base = False)
                            else:
                               self.skilltree.increase_skill_level('skills', passive_name, int(val), req = 15, base = True)
                        if key == '오라레벨':
                            if iname == '신화':
                                self.skilltree.increase_skill_level('skills', aura_name, int(val), req = 48, base = False)
                            else:
                                self.skilltree.increase_skill_level('skills', aura_name, int(val), req = 48, base = True)

                        if key == '스킬구간':
                            minlv = val['min']
                            maxlv = val['max']
                            lvup = val['lvup']
                            
                            if iname == '신화':
                                self.skilltree.increase_skill_level_range('skills', (minlv, maxlv), lvup, base = False)
                            else:
                                self.skilltree.increase_skill_level_range('skills', (minlv, maxlv), lvup, base = True)
 
        #per-dark elemental options
        for defer in defer_list1:
            opt, iname = defer
            r = 1
            vmax = None
            if 'condition' in opt.keys():
                condition = opt['condition']
                #del opt['condition']

                if buff_option is not None and buff_type == '축':
                    main_item_dark_res = self.owner.char_stat['skilltree'].buffoption['암속저']

                    dr = self.owner.char_stat['암속성저항'] + (buff_option['암속저'] - main_item_dark_res)
                else:
                    dr = self.owner.char_stat['암속성저항'] 

                v = condition['per-val']
                r = int(dr/v)

                if condition['max'] is not None:
                    try:
                        vmax = float(condition['max'])
                    except:
                        vmax = float(condition['max'][:-1])
                else:
                    r = 1

                #print(iname, v, r, vmax)

            for key in opt.keys():
                if key == '속추댐':
                    defer_list2.append((opt, (r, vmax), iname))
                else:
                    self.calculate_option(opt, key, r, vmax, iname)

        #leveling
        self.skilltree.finalize_levelup()

        #엘마 초월의룬( 마력증폭 크리 28+2n, 
        #     속성마스터리 공격력: 12+1.25n (버림)
        #     쇼타임 강화 : 14.6 + 1.4n)
        if jobname == '眞 엘레멘탈마스터':
            skill = self.skilltree.get_skill('skills', '초월의 룬', req = 75)
            
            level = min(1 + skill[2], 11)

            extra_cri = 28 + 2*level
            extra_dam = 1 + (12 + int(1.25 * level))/100
            extra_cool = 1 + (14.6 + 1.4 * level)/100

            self.skilltree.inner_data['초월의 룬'] = {'크리티컬':extra_cri, '데미지':extra_dam, '쿨감':extra_cool}

        elif jobname == '眞 웨펀마스터':
            skill = self.skilltree.get_skill('skills', '무기의 극의', req = 15)

            data = skill[0]
            blv = skill[1]
            lvup = skill[2]

            #print ('무기의극의', blv, lvup)

            wm_lvl_inc = data['values'][blv + lvup]

            self.skilltree.inner_data['무기의 극의'] = {'마스터리레벨': wm_lvl_inc}

        self.skilltree.finalize_passive()
   
       #} dealer-end        
        for item in item_db_list:
            iname = item.get('name')
            if iname is None:
                continue

            if iname == '별의 바다 : 바드나후':
                v = max([char_stat['화속성강화'], char_stat['명속성강화'], char_stat['수속성강화'], char_stat['암속성강화']])
                char_stat['수속성강화'] = char_stat['명속성강화'] = v
            elif iname == '군신의 숨겨진 유산 세트(3)':
                mspeed = char_stat['이동속도']
                if mspeed < 40:
                    inc = 2
                elif 40 <= mspeed < 60:
                    inc = 4
                elif 60 <= mspeed < 80:
                    inc = 6
                elif 80 <= mspeed < 100:
                    inc = 8
                elif 100 <= mspeed < 120:
                    inc = 10
                elif 120 <= mspeed:
                    inc = 10
                    char_stat['공격속도'] += 10
                    char_stat['캐스팅속도'] += 15

                char_stat['힘지'] += inc
            elif iname == '새벽을 녹이는 따스함':
                rsum = 0
                for item in self.e_dict['equipment']:
                    r = item.get('reinforce')
                    if r is not None:
                        rsum += r
                
                rsum = min(rsum, 150)
                rsum = int(rsum/6)

                char_stat['공격속도'] += (rsum-1) * 0.8
                char_stat['이동속도'] += (rsum-1) * 0.8
                char_stat['캐스팅속도'] += (rsum-1) * 1.2
                char_stat['물리크리티컬'] += rsum * 0.5
                char_stat['마법크리티컬'] += rsum * 0.5
            elif iname == '운명의 주사위 세트(2)':
                if dice_min == 0:
                    char_stat['공격속도'] += 7
                    char_stat['이동속도'] += 7
                    char_stat['캐스팅속도'] += 10.5
                else:
                    char_stat['공격속도'] += 8.4
                    char_stat['이동속도'] += 8.4
                    char_stat['캐스팅속도'] += 12.6
            elif iname == '운명의 주사위 세트(3)':
                if dice_min == 0:
                    char_stat['공격속도'] += 3.5
                    char_stat['이동속도'] += 3.5
                    char_stat['캐스팅속도'] += 5.25
                else:
                    char_stat['공격속도'] += 4.2
                    char_stat['이동속도'] += 4.2
                    char_stat['캐스팅속도'] += 6.3
            elif iname == '탈리스만 선택':
                e_tal_list = self.inner_data['탈리스만']
                #print(e_tal_list)
                if len(e_tal_list) >= 2:
                    ft = e_tal_list[0]  
                    st = e_tal_list[1]
                elif len(e_tal_list) == 1:
                    ft = e_tal_list[0]
                    st = None
                else:
                    ft = st = None

                if ft is not None:
                    ft['dam'] *= (1.55)
                    ft['cool'] *= (0.7)

                if st is not None:
                    st['dam'] *= (1.45)
                    st['cool'] *= (0.75)

                #print(e_tal_list)

                if buff_option is not None and buff_type == '축':
                    if len(e_tal_list) >= 2:
                        self.skilltree.buffoption['힘지'] *= (1.04 * 1.02)
                    elif len(e_tal_list) == 1:
                        self.skilltree.buffoption['힘지'] *= 1.04
 
            elif iname == '영원한 흐름의 길 세트(5)':
                for lv, items in self.skilltree.skill_enchant.items():
                    if int(lv) > 45:
                        break

                    items['cool'] *= 0.95
            elif iname == '영명한 세상의 흐름':
                for lv, items in self.skilltree.skill_enchant.items():
                    if int(lv) > 45:
                        break

                    items['cool'] *= 0.9
            elif iname == '시간을 거스르는 자침':
                for lv, items in self.skilltree.skill_enchant.items():
                    if int(lv) in [50, 85, 100]:
                        continue

                    if 25 <= int(lv) <= 45:
                        items['cool'] *= 0.8
                    elif 60 <= int(lv) <= 80:
                        items['cool'] *= 0.9
            elif iname == '세계수의 뿌리':
                for lv, items in self.skilltree.skill_enchant.items():
                    if int(lv) in [50, 85, 100]:
                        continue

                    if 25 <= int(lv) <= 45:
                        items['cool'] *= 0.85
                    elif 60 <= int(lv) <= 80:
                        items['cool'] *= 0.95

        self.skilltree.finalize_active()

        #finish elemental additional damage
        for t_item_db in defer_list2:
            opt, cond, iname = t_item_db
            r, vmax = cond

            for key in opt.keys():
                if key == 'condition':
                    continue

                val = opt[key] * r
                #val = r
                if vmax is not None:
                    if isinstance(val, list):
                        val = vmax
                    else:
                        val = min(val, vmax)

                if key == '속추댐':
                    elem = opt.get('속성종류')
                    if elem is not None:
                        ev = char_stat[elem+'속성강화']
                    else:
                        ev = max([char_stat['화속성강화'], char_stat['명속성강화'], char_stat['수속성강화'], char_stat['암속성강화']])

                    #char_stat['속추댐(수치)'] += val
                    
                    # 홀리속깍 +60 + 시로코몹 속저 -50 = +10
                    #print (ev, val)
                    val = (1.05 + ((ev + 10) * 0.0045)) * val
                    
                    char_stat['속추댐'] += val
                    char_stat['추댐'] += val

                    try:
                        self.debug_list[key].append((iname, val))
                    except:
                        self.debug_list[key] = [(iname, val)]

                elif key == '속성종류':
                    continue
                else:
                    print (key)
                    raise Exception
       
        #print(self.debug_list['모공'])
        #print(debug_list['물마독공'])
        #print(self.debug_list['크증추'])
        #print(self.debug_list['힘지'])
        #print(debug_list['증추'])
        #print(self.debug_list['스킬'])
        #for k, v in self.debug_list.items():
        #    if k.find('속성강화') >= 0:
        #        print (v)
        #print(self.debug_list['속강'])

        #print(self.owner.char_stat['화속성강화'])
        val = np.mean(list(self.inner_data['쿨감목록'].values()))
        self.skilltree.inner_data['평균쿨감'] = val

    def build_item_db_list(self):
        for cur in self.e_dict['setItemInfo']:
            idx = self.e_dict['setItemInfo'].index(cur)
            setid = cur['setItemId']
            setname = cur['setItemName']
            activeno = cur['activeSetNo']

            if (setname.find('디멘션') >= 0 or setname.find('타락한 어둠') >= 0 
                    or setname.find('혈광갑주') >= 0 or setname.find('어둠의 침식') >= 0 ) and activeno in [2, 4]:
                for eitem in self.e_dict['equipment']:
                    ename = eitem.get('itemName')
                    if ename is None:
                        continue

                    if ename.find('차원 : ') >= 0 or ename.find('진 : ') >=0:
                        setid = eitem['setItemId']
                        setname = eitem['setItemName']
                        activeno += 1
                        data = {
                                'slotId':eitem['slotId'],
                                'slotName':eitem['slotName'],
                                'itemRarity':eitem['itemRarity']
                            }
                        cur['slotInfo'].append(data)

            for slot in cur['slotInfo']:
                slotname = slot['slotName']
                self.equip_info[slotname]['세트'] = idx

            try:
                for setno in self.set_db[setid].keys():
                    if setno == 'name':
                        continue

                    if int(setno) > int(activeno):
                        continue

                    #print(setno, self.set_db[setid][setno], activeno)
                    data = copy.deepcopy(self.set_db[setid][setno])
                    data['name'] = self.set_db[setid]['name']+'('+setno+')'
                    self.item_db_list.append(data)
            except:
                try:
                    should_create_db = True
                    for key in self.set_db.keys():
                        if self.set_db[key]['name'] == setname:
                            should_create_db = False
                            for setno in self.set_db[key].keys():
                                if setno == 'name':
                                    continue
                                if int(setno) > int(activeno):
                                    continue
                                #print(setno, self.set_db[key][setno], activeno)
                                data = copy.deepcopy(self.set_db[key][setno])
                                data['name'] = self.set_db[key]['name']+'('+setno+')'
                                self.item_db_list.append(data)
                            break
                    if should_create_db is True:
                        newid = myutil.build_set_item(setname, self.skilltree.skill_db, self.item_db, self.set_db)
                        if newid == None:
                            continue

                        if newid != setid:
                            setid = newid
                        
                        #with open("set_db.json", "w") as f:
                        #    json.dump(self.set_db, f)
                        #with open("item_db.json", "w") as f:
                        #    json.dump(self.item_db, f)

                        for setno in self.set_db[setid].keys():
                            if setno == 'name':
                                continue
                            if int(setno) > int(activeno):
                                continue

                            #print(setno, self.set_db[setid][setno], activeno)
                            data = copy.deepcopy(self.set_db[setid][setno])
                            data['name'] = self.set_db[setid]['name']+'('+setno+')'
                            self.item_db_list.append(data)
                except:
                    print(setname, "??")       
                    raise

        #myth and siroco item
        myth_options = self.extra_info.get('myth')
        if myth_options is not None:
            myth_db = []
            myth_buff_db = []
            for option in myth_options:
                explain = option['explain']
                explain = explain.replace('모든 속성 강화', '마을적용옵션')
                #print (explain)
                myutil.parse_explain(explain, myth_db, "신화", self.skilltree.skill_db)

                buffexp = option['buffExplain']
                myutil.parse_buff(buffexp, myth_buff_db, "신화버퍼", self.skilltree.skill_db)
            
            data = {'name':'신화', 'options':myth_db}
            data['buffopts'] = myth_buff_db

            self.item_db_list.append(data)
            #print (myth_buff_db)

        siroco_db1 = []
        siroco_db2 = []

        siroco_buff_db1 = []
        siroco_buff_db2 = []
        
        siroco_set = self.extra_info['siroco']
        main_siroco_set = self.owner.inner_data['main_siroco']
        for siroco_part in siroco_set.keys():
            item, options = siroco_set[siroco_part]

            #first option (no condition)
            explain = options[0]['explainDetail']
            myutil.parse_explain(explain, siroco_db1, "시로코1옵", self.skilltree.skill_db)

            buffexp = options[0]['buffExplain']
            myutil.parse_buff(buffexp, siroco_buff_db1, "버퍼시로코1옵", self.skilltree.skill_db)

            #print('siroco_set len', len(siroco_set), len(main_siroco_set))

            if ((siroco_part == "무기" and (len(siroco_set) == 4 or len(main_siroco_set) ==4)) or
                    (siroco_part == "하의" and "반지" in main_siroco_set.keys()
                        and main_siroco_set["반지"][0] == item) or
                    (siroco_part == "반지" and "보조장비" in main_siroco_set.keys()
                        and main_siroco_set["보조장비"][0] == item) or
                    (siroco_part == "보조장비" and "하의" in main_siroco_set.keys()
                        and main_siroco_set["하의"][0] == item)):

                _explain = options[1]['explainDetail']
                _explain = _explain.split("\n- ")
                explain = '|'.join(_explain[1:])
                explain = explain.replace('|','\n')

                myutil.parse_explain(explain, siroco_db2, "시로코2옵", self.skilltree.skill_db)

                _buffexp = options[1]['buffExplain']
                _buffexp = _buffexp.split("\n- ")
                buffexp = '|'.join(_buffexp[1:])
                buffexp = buffexp.replace('|','\n')

                myutil.parse_buff(buffexp, siroco_buff_db2, "버퍼시로코2옵", self.skilltree.skill_db)
                
        
        siroco_data1 = {'name':"시로코1",'options':siroco_db1}
        siroco_data2 = {'name':"시로코2",'options':siroco_db2}

        siroco_data1['buffopts'] = siroco_buff_db1

        #print('버프시로코1옵', siroco_buff_db1)
        siroco_data2['buffopts'] = siroco_buff_db2
        #print('버프시로코2옵', siroco_buff_db2)

        self.item_db_list.append(siroco_data1)
        self.item_db_list.append(siroco_data2)

        new_itemlist = []
        """
        upgr_id = self.equip_info[ekey].get('upgr_id')
        for ekey in self.equip_info.keys():
            if ekey == '보조무기':
                continue
            try:
                uid = self.equip_info[ekey].get('upgr_id')
            except:
                print (ekey)
                raise

            if uid is not None:
                _item_option = self.item_db.get(uid)

                if _item_option is None:
                    should_create_db = True
                    for key in self.item_db.keys():
                        #print(key, self.item_db[key]['name'])
                        #print(equip_info[ekey]['name'])
                        if self.item_db[key]['name'] == self.equip_info[ekey]['name']:
                            #self.debug_print(ekey, self.item_db[key])
                            self.item_db_list.append(copy.deepcopy(self.item_db[key]))
                            should_create_db = False
                            break

                    if should_create_db is True:
                        #print('새로만듬', ekey, self.equip_info[ekey]['name'])
                        new_itemlist.append(eid)
                    
        if len(new_itemlist) > 0:
            #print (new_itemlist)
            myutil.build_single_item(new_itemlist, self.skilltree.skill_db, self.item_db)
            #with open("item_db.json", "w") as f:
            #    json.dump(self.item_db, f)

            for iid in new_itemlist:
                self.item_db_list.append(copy.deepcopy(self.item_db[iid]))
        """
        for ekey in self.equip_info.keys():
            if ekey == '보조무기':
                continue
            try:
                eid = self.equip_info[ekey].get('id')
            except:
                print (ekey)
                raise

            if eid is not None:
                _item_option = self.item_db.get(eid)

                if _item_option is not None:
                    item_option = copy.deepcopy(_item_option)

                    self.item_db_list.append(item_option)
                else:
                    should_create_db = True
                    """
                    for key in self.item_db.keys():
                        #print(key, self.item_db[key]['name'])
                        #print(equip_info[ekey]['name'])
                        if self.item_db[key]['name'] == self.equip_info[ekey]['name']:
                            #self.debug_print(ekey, self.item_db[key])
                            self.item_db_list.append(copy.deepcopy(self.item_db[key]))
                            should_create_db = False
                            break
                    """
                    if should_create_db is True:
                        #print('새로만듬', ekey, self.equip_info[ekey]['name'])
                        new_itemlist.append(eid)
                    
        if len(new_itemlist) > 0:
            #print (new_itemlist)
            myutil.build_single_item(new_itemlist, self.skilltree.skill_db, self.item_db)
            #with open("item_db.json", "w") as f:
            #    json.dump(self.item_db, f)

            for iid in new_itemlist:
                #print(self.item_db[iid])
                self.item_db_list.append(copy.deepcopy(self.item_db[iid]))

    @staticmethod
    def get_wep_cool(wep_type):
        wep_cool = {}
        
        if wep_type in ['소검', '염주', '광창', '코어블레이드']:
            wep_cool['마법공격'] = 1.05
            if wep_type in ['염주']:    
                wep_cool['물리공격'] = 0.95   
        elif wep_type in ['도', '로드', '낫', '투창']:
            wep_cool['물리공격'] = 0.95
        elif wep_type in ['둔기', '머스켓', '창', '장창', '장도']:
            wep_cool['물리공격'] = 1.05
            if wep_type in ['창']:
                wep_cool['마법공격'] = 0.95
        elif wep_type in ['대검', '건틀릿', '핸드캐넌', '배틀액스', '쌍검', '미늘창', '중검']:
            wep_cool['물리공격'] = 1.10
            if wep_type in ['배틀 액스', '쌍검']:
                wep_cool['마법공격'] = 0.9
        elif wep_type in ['광검', '너클', '권투글러브', '자동권총', '보우건', '단검']:
            wep_cool['물리공격'] = 0.9
            if wep_type in ['너클']:
                wep_cool['마법공격'] = 1.05
            elif wep_type in ['단검']:
                wep_cool['마법공격'] = 0.95
        elif wep_type in ['스탭', '완드']:
            wep_cool['마법공격'] = 1.10
        elif wep_type in ['토템']:
            wep_cool['마법공격'] = 0.95
        elif wep_type in ['차크라웨펀']:
            wep_cool['마법공격'] = 1.05

        return wep_cool


    def create_equip_info(self):
        siroco_set={}
        equip_info={}
        extra_info={}

        high_remodel = False
        remodel_count = 0

        wep_cool_eff = 1
        wep_reinforce = 0
        wep_type = None
        wep_name = None

        max_reinforce = 0
        sum_reinforce = 0

        char_dam_type = self.owner.inner_data.get('dam_type')

        for cur in self.e_dict['equipment']:
            slot = cur["slotName"]
            item_id = cur["itemId"]

            equip_info[slot] = {}
            e_cur = equip_info[slot]
            e_cur['id'] = item_id
            e_cur['name'] = cur.get('itemName')

            e_upgraded = cur.get("upgradeInfo")

            if e_upgraded is not None:
                siroco_name = e_upgraded["itemName"]
                if siroco_name != "무형의 잔향":
                    item_id = e_upgraded["itemId"]
                
                if slot == '무기':
                    siroco_set[slot] = ('잔향', cur["sirocoInfo"]["options"])
                else:
                    siroco_part = parse("{} : {kind}의 {}", siroco_name)
                    try:
                        siroco_set[slot] = (siroco_part['kind'], cur["sirocoInfo"]["options"])
                    except:
                        print (siroco_part, e_upgraded, slot)

                e_cur['효과'] = "시로코"
            
            if slot == '무기' and char_dam_type is not None:
                wep_reinforce = cur["reinforce"]
                wep_type = cur['itemTypeDetail']
                wep_name = cur.get('itemName')

                wep_cool_eff = self.get_wep_cool(wep_type).get(char_dam_type)
                if wep_cool_eff is not None and wep_cool_eff != 1:

                    for lv, skill in self.skilltree.skill_enchant.items():
                        if self.owner.jobname in ['스톰트루퍼', '眞 런처', '眞 퇴마사', '眞 사령술사'] and lv not in ['50', '85', '100']:
                            continue
                        skill['cool'] *= wep_cool_eff
                    
            if item_id != e_cur['id']:
                e_cur['upgr_id'] = item_id
            e_cur['등급'] = cur["itemRarity"]
            if e_cur['등급'] == "신화":
                e_cur['효과'] = "신화"
                if "mythologyInfo" in cur.keys():
                    extra_info['myth'] = cur["mythologyInfo"]["options"]
                else:
                    #error('잘못된 API 결과', '신화', '옵션 없음')
                    pass

            e_type = cur["amplificationName"]
            reinforce = cur["reinforce"]
            refine = cur["refine"]

            if self.owner.buffer is not None:
                main_stat_type = self.main_stat['type']
                if "itemAvailableLevel" in cur:
                    lvl = cur["itemAvailableLevel"]
                    if 95 < lvl <= 100:
                        lvl = 100
                    else:
                        lvl = 95
                    
                if e_type is not None and e_type.find(main_stat_type) >= 0:  
                    if cur["itemRarity"] == '신화':
                        f = 1.07
                    elif cur["itemRarity"] == '레전더리':
                        f = 0.93
                    else:
                        f = 1

                    v = amplify_effect[str(lvl)][reinforce]
                    v = round(v*f)

                    self.main_stat['value'] += v
                    #if self.skilltree.buffoption['type'] == '아포':
                        #print('지능증가', slot+'증폭', v)

                if slot in ['보조장비', '마법석']:
                    if cur["itemRarity"] == '레전더리':
                        f = 0.93
                    else:
                        f = 1
                    
                    v = substone_effect[str(lvl)][reinforce]
                    v = round(v*f)

                    self.main_stat['value'] += v
                    #if self.skilltree.buffoption['type'] == '아포':
                        #print('지능증가', slot+'강화', v)
                elif slot in ['상의', '하의', '머리어깨', '신발', '허리']:
                    typ = cur['itemTypeDetail'][0]

                    if slot == '상의' and cur['itemRarity'] == '신화':
                        mastery_base = 244
                    else:
                        mastery_base = 242

                    if self.main_stat['type'] == '체력':
                        mastery_base /= 2

                    if typ == '판':
                        mastery = mastery_base * mastery_conv[slot] / 2

                        rv = math.floor(cur['reinforce'] / 3)
                        mastery += rv * mastery_conv[slot]

                        self.main_stat['value'] += round(mastery)
                        #if self.skilltree.buffoption['type'] == '아포':
                            #print('지능증가', slot+'마스터리', round(mastery))

                elif slot == '무기' and refine is not None:
                    v = wep_refine_effect[refine]

                    self.main_stat['value'] += v
                    #if self.skilltree.buffoption['type'] == '아포':
                        #print('지능증가', '무기재련', v)

            if refine == 8 and reinforce < 13:
                e_reinforce = 12
            elif refine == 7 and reinforce < 11:
                e_reinforce = 10
            elif refine == 6 and reinforce < 9:
                e_reinforce = 8
            else:
                e_reinforce = reinforce

            if e_type is None:
                e_type = cur.get("remodelInfo")
                if e_type is None:
                    e_type = '강화'
                else:
                    e_type = '개조'
                    e_reinforce += 7

                    if e_reinforce >= 6:
                        high_remodel = True

                    remodel_count += 1

            if e_type != '강화' and e_type != '개조':
                max_reinforce = max(reinforce, max_reinforce)
                if slot != '슬롯':
                    sum_reinforce += reinforce
       
            e_cur['강화'] = (e_type, str(reinforce), str(refine), str(e_reinforce))

        extra_info['siroco'] = siroco_set
        self.equip_info = equip_info
        self.extra_info = extra_info
        self.weapon_info['name'] = wep_name
        self.weapon_info['reinforce'] = wep_reinforce
        self.weapon_info['cooleff'] = wep_cool_eff
        self.inner_data['최대증폭수치'] = max_reinforce
        self.inner_data['평균증폭수치'] = sum_reinforce / 11
        self.inner_data['최대개조수치'] = high_remodel
        self.inner_data['산물장착수'] = remodel_count
    
    def bind_skill(self, skilltree):
        self.skilltree = skilltree
        self.owner = skilltree.owner

        skilltree.inventory = self

        jobid = str(self.owner.jobid)
        classid = str(self.owner.classid)

        self.talisman_data = self.talisman_db
        if self.owner.buffer is not None:
            self.buffer_talisman_data = self.buffer_talisman_db

    def analyze_talisman(self):
        tal_list = []
        runes = []
        talismans = self.t_dict.get('talismans')
        if talismans is None:
            talismans = []
        for tal in talismans:
            for rune in tal['runes']:
                #TODO: 탈리스만 룬 맞지 않게 장착한 경우 체크
                #runes.append(rune['itemName'])
                rune_level = rune['itemName'][0:3]
                rune_raw = rune['itemName'][4:].split('룬')
                rune_type = rune_raw[0][:-1]
                rune_skill = re.findall(r'\[.*?\]', rune_raw[1])[0][1:-1]
            
                rune_level_dict = {'갈라진':0, '빛바랜':1, '선명한':2, '화려한':3}

                rld = rune_level_dict[rune_level]

                skill_instance = self.skilltree.get_skill_instance('actives', rune_skill)
                if skill_instance is None:
                    #print ("룬 대상스킬 없음:", "'"+rune_skill+"'")
                    continue

                if rune_type == '테라코타':
                    dinc = rld + 1

                    skill_instance['dam'] *= (1 + dinc/100)
                elif rune_type == '서클 메이지':
                    ddec = rld + 1
                    if rld < 2:
                        cdec = rld+3
                    else:
                        cdec = rld+4

                    skill_instance['dam'] *= (1 - ddec/100)
                    skill_instance['cool'] *= (1 - cdec/100)
                elif rune_type == '수호자들':
                    cdec = rld + 2

                    skill_instance['cool'] *= (1 - cdec/100)
                elif rune_type == '세컨드 팩트':
                    if rld < 2:
                        dinc = rld+2
                    else:
                        dinc = rld+3
                    
                    cinc = rld + 1
                    skill_instance['dam'] *= (1 + dinc/100)
                    skill_instance['cool'] *= (1 + cinc/100)

            tid = tal['talisman']['itemId']
            if self.owner.buffer is not None and self.owner.buffer['inventory'] == self:
                if tid in self.buffer_talisman_data.keys():
                    buff_tal = self.buffer_talisman_data[tid]

                    talisman_option = buff_tal['options'][0]['버프탈리']
                    buff = talisman_option['buff']

                    self.skilltree.buffoption['힘지'] *= (1 + buff/100)

            try:
                tal_list.append(self.talisman_data[tid])
            except:
                try:
                    #레어 탈리스만 시도
                    tname = tal['talisman']['itemName']
                    tskill = re.findall(r'\[.*?\]', sname)[0][1:-1]
                except:
                    tal_list.append(None)
                    continue

                tskill = self.skilltree.get_skill('actives', tskill)
                if tskill is None:
                    tal_list.append(None)
                    continue

                tal_list.append({'name':tname, 
                                    'options':[
                                        {'탈리스만':{
                                            'skillName':tskill, 
                                            'skillId':tskill_id, 
                                            'req':lv, 
                                            'dam':1.1, 
                                            'cool':1
                                        }
                                        }]
                                    })

        e_tal_list = []
        for cur in tal_list:
            if cur is None:
                e_tal_list.append(None)
                continue

            talisman_option = cur['options'][0]['탈리스만']

            sname = talisman_option['skillName']
            lv = talisman_option['req']
            dam = talisman_option['dam']
            cool = talisman_option['cool']

            #print(talisman_option)

            skill_instance = self.skilltree.get_skill_instance('actives', sname, req = lv)
            e_tal_list.append(skill_instance)

            if skill_instance is not None:
                skill_instance['dam'] *= (1 + dam/100)
                skill_instance['cool'] *= (1 + cool/100)

        self.inner_data['탈리스만'] = e_tal_list

        #print(e_tal_list)

    def analyze_flag_and_gem(self):
        flag = self.g_dict['flag']

        if flag is None:
            return

        opt = flag['itemAbility']
        reinforce_stat = flag_effect[flag['reinforce']]
        if reinforce_stat > 0:
            for ekey in self.enchant['stat'].keys():
                self.enchant['stat'][ekey] += reinforce_stat
                #if self.owner.buffer is not None and self.owner.buffer.get('inventory') != self:
                    #if ekey == '지능':
                        #print('지능증가', '휘장강화', reinforce_stat)

        opt_list = opt.split(", ")
        for o in opt_list:
            r = parse("{opt} +{val}", o)
            if r is None:
                continue
            s = r['opt']
            v = int(r['val'])

            #self.debug_print(s, v)
            for stat in stat_type:
                if s.find(stat) >= 0:
                    self.enchant['stat'][stat] += v
                    #if self.owner.buffer is not None and self.owner.buffer.get('inventory') != self:
                        #if stat == '지능':
                           #print ('지능증가', flag['itemName'], v)

            for dam in dam_type:
                if s.find(dam) >= 0:
                    dam += " 공격력"
                    self.enchant['dam'][dam] += v

        gems = flag['gems']
        for gem in gems:
            opt = gem['itemAbility']
            #self.debug_print(opt)
            r = parse("{opt} +{val}", opt)
            if r is not None:
                s = r['opt']
                try:
                    v = int(r['val'])
                except:
                    try:
                        v = float(r['val'][:-1])
                    except:
                        v = float(r['val'][:-2])

                #self.debug_print (s, v)
                for etype in self.enchant.values():
                    if s in etype.keys():
                        etype[s] += v

    def analyze_avatar(self):
        id_list = []
        for cur in self.a_dict['avatar']:
            if cur['slotName'] != '오라 스킨 아바타':
                id_list.append(cur.get('itemId'))
            opt = cur['optionAbility']
            r = None
            #print(opt)
            if opt is not None:
                if opt.find('스킬') >= 0:
                    avt_skill = opt.split(' 스킬Lv')[0]

                    self.skilltree.increase_skill_level('skills', avt_skill, 1)
                    self.skilltree.increase_skill_level('actives', avt_skill, 1)

                else:
                    r = parse("{type} {value:d}{}", opt)
                    if r is not None:
                        typ = r['type'].replace(" ","")
                        val = r['value']

                        for etype in self.enchant.values():
                            if typ in etype.keys():
                                #if self.owner.buffer is not None and self.owner.buffer.get('inventory') != self:
                                    #if typ == '지능':
                                        #print('지능증가', '아바타'+cur['slotName'], val)

                                etype[typ] += val
                                break

            emblems = cur['emblems']
            for em in emblems:
                if em['slotColor'] == '플래티넘':
                    if em['itemName'] is None:
                        continue

                    try:
                        plt = re.findall(r'\[.*?\]', em['itemName'])[0][1:-1]
                        self.skilltree.increase_skill_level('skills', plt, 1)
                        self.skilltree.increase_skill_level('actives', plt, 1)
                    except:
                        pass

                    if em['itemRarity'] == '레전더리':
                        inc = 8
                    else:
                        inc = 6

                    for ekey in self.enchant['stat'].keys():
                        #if self.owner.buffer is not None and self.owner.buffer.get('inventory') != self:
                            #if ekey == '지능':
                                #print('지능증가', '플래티넘엠블렘'+cur['slotName'], inc)

                        self.enchant['stat'][ekey] += inc

                    continue

                e = em['itemName']
                #print(e)
                r = parse("{grade} {color} 엠블렘[{option}", e)
                if r is not None:
                    o = r['option']
                    g = r['grade']
                    c = r['color']
                    #print(o, g, c)
                    for s in stat_type:
                        if o.find(s) >= 0:
                            try:
                                val = emblem_type[g][c]
                            except:
                                val = 0
                            #print (s, val)
                            if s in self.enchant['stat'].keys():
                                #if self.owner.buffer is not None and self.owner.buffer.get('inventory') != self:
                                    #if s == '지능':
                                        #print('지능증가', '아바타엠블렘'+cur['slotName'], val)

                                self.enchant['stat'][s] += val
                    for s in dam_type:
                        if o.find(s) >= 0:
                            try:
                                val = emblem_type2[g][c]
                            except:
                                val = 0
                            ss = s + ' 크리티컬 히트'
                            #self.debug_print (ss, val)
                            if ss in self.enchant['critical'].keys():
                                self.enchant['critical'][ss] += val
                    for s in speed_type:
                        if o.find(s) >= 0:
                            try:
                                val = emblem_type3[g][c]
                            except:
                                val = 0
                            ss = s + '속도'
                            #self.debug_print (ss, val)
                            if ss in self.enchant['speed'].keys():
                                self.enchant['speed'][ss] += val
                    s = '캐스트속도'
                    if o.find(s) >= 0:
                        try:
                            val = emblem_type4[g][c]
                        except:
                            val = 0
                        self.enchant['speed'][s] += val

        if len(id_list) > 0:
            id_list_str = ','.join(id_list)

            url = "multi/items?itemIds=" + id_list_str + "&"
            avt_dict = myutil.load_api(url)
            #TODO: avatar db

            rare = normal = etc = 0
            for avt in avt_dict['rows']:
                typ = avt['itemTypeDetail'] 
                if typ in ['상의', '하의', '모자', '머리', '얼굴', '목가슴', '허리', '신발']:
                    setname = avt.get('setItemName')
                    if setname is not None:
                        if setname == '레어 아바타 세트':
                            rare += 1
                        elif setname == '상급 아바타 세트':
                            normal += 1
                        else:
                            etc += 1
                if typ == '오라':
                    status = avt.get('itemStatus')
                    if status is not None:
                        for statv in status:
                            if statv['name'] in ['힘', '지능', '체력', '정신력']:
                                v = math.floor((statv['value'] * 10 / 11))
                                self.enchant['stat'][statv['name']] += v
                                #if statv['name'] == '지능':
                                    #print('지능증가', '오라:', v)


            inc = 0
            if 3 <= rare < 8: #레어아바타 3셋
                inc += 20
            elif rare == 8: #레어아바타 풀셋
                inc += 40

            if 3 <= normal < 8: #상급 아바타 3셋
                inc += 10
            elif normal == 8: #상급 아바타 풀셋
                inc += 20

            if etc == 8: #이벤압
                if setname == '로얄 패스 아바타 세트': 
                    inc += 93
                else:
                    inc += 25

            if inc >= 0:
                #print('지능증가', '아바타세트옵션', inc)
                for ekey in self.enchant['stat'].keys():
                    self.enchant['stat'][ekey] += inc

    def analyze_enchants(self):
        for cur in self.e_dict['equipment']:
            enchants = cur.get('enchant')
            if enchants is None:
                continue

            for key, enchant in enchants.items():
                if key == 'status':
                    for e in enchant:
                        k = e['name']
                        for etype in self.enchant.values():
                            if k in etype.keys():
                                #if self.owner.buffer is not None and self.owner.buffer.get('inventory') != self:
                                    #if k == '지능':
                                        #print ('지능증가', '마부:'+cur.get('itemName'), e['value'])
                                try:
                                    etype[k] += e['value']
                                except:
                                    etype[k] += float(e['value'][:-1])
                                break

                elif key == 'reinforceSkill':
                    for e in enchant:
                        for skill in e['skills']:
                            name = skill['name']
                            lv = skill['value']

                            self.skilltree.increase_skill_level('skills', name, int(lv))
                            self.skilltree.increase_skill_level('actives', name, int(lv))

    def get_main_stat(self):
        estat = self.enchant['stat']
        #print(estat)
        main_enchant = 0 
        main_stat_type = None
        for key, val in estat.items():
            if val > main_enchant:
                main_stat_type = key
                main_enchant = val

        if main_stat_type is None:
            main_stat_type = stat_conv[self.owner.char_stat['주스탯']['list'][0]]
        
        return main_stat_type, main_enchant


