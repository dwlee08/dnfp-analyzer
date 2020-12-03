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

    def analyze_stat(self):
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

        max_stat = max(stat_info.values())
        self.char_stat['주스탯'] = {'value':max_stat, 'list':[]}
        for key in stat_info.keys():
            if stat_info[key] == max_stat:
                self.char_stat['주스탯']['list'].append(key)

        max_elem = max(elem_info.values())
        self.char_stat['주속강'] = {'value':max_elem, 'list':[]}
        for key in elem_info.keys():
            if elem_info[key] == max_elem:
                self.char_stat['주속강']['list'].append(key)

        max_dam = max(dam_info.values())
        self.char_stat['주공격'] = []
        for key in dam_info.keys():
            if dam_info[key] == max_dam:
                self.char_stat['주공격'].append(key)
    
    def analyze_sw(self, cbuff):
        sinfo = self.sw_dict['skill']['buff']['skillInfo']    
        
        sw_name = cbuff['name']
        sw_values = sinfo['option']['values']
        sw_lvl = sinfo['option']['level']
        vidx = cbuff['option_idx']
        
        self.char_stat['nick'] = self.nick = cbuff['nick']
        self.base_stat = cbuff['base_stat']

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

            self.char_stat['버프'] = (sw_name, sw_lvl, buff_val, buff_power)
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

    def get_epic_status(self, s_id, c_id):
        mon_end = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        #fix: 2021 prepare
        today = datetime.datetime.today()
        thisyear = today.year
        thismon = today.month
        thisday = today.day

        thishour = today.hour
        thismin = today.minute

        cur_list = {'지옥파티':0, '에픽':0, '신화':0, '시로코':0, '신화목록':{}, '에픽목록':{}, '시로코목록':{}}
        for year in range(2020, thisyear+1):
            for mon in range(1, thismon+1):
                _startDate = datetime.date(year, mon, 1)
                if year == 2020 and mon == 1:
                    _startDate = _startDate.replace(day=9)
                    
                startDate = str(_startDate).replace('-','')+'T0000'

                _endDate = datetime.date(year, mon, mon_end[mon-1])
                if mon == thismon:
                    _endDate = _endDate.replace(day=thisday)
                    endTime = 'T'+str(thishour).zfill(2)+str(thismin).zfill(2)
                else:
                    endTime = 'T2359'

                endDate = str(_endDate).replace('-','')+endTime

                order = year*100 + mon
                
                url = 'servers/'+s_id+'/characters/'+c_id+'/timeline?limit=100&code=504,505,507,513&startDate='+startDate+'&endDate='+endDate+'&'
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

                            if ir in ['신화' , '에픽']:
                                if code == 505 and dname == '지혜의 인도':
                                    cur_list['지옥파티'] += 10

                                if iname[0:4] not in ['무형 : ', '무의식 :', '환영 : ']:
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
        if self.test_mode is True:
            with open('epictree.json', 'w') as f:
                json.dump(cur_list, f)
        
        return cur_list

    def do_create_char_dict(self, epic_status):
        character = self

        classid = character.classid
        jobid = character.jobid
        s_id = character.sid
        cha_id = character.cid
        
        if epic_status is True:
            character.epic_status = self.get_epic_status(s_id, cha_id)
        else:
            character.epic_status = None
   
        #self.logger.info('start analyze :' + character.name + ' ' + character.server)

        character.char_stat['inventory'].create_equip_info()
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
        if character.buffer is not None:
            character.buffer['inventory'].handle_item_options()

        character.char_stat['skilltree'].handle_special_case()

        #던전 속성       
        d_info = {}
        d_info['name'] = '시로코'
        d_info['지역버프'] = {'factor':2.334, 'inc':4397}
        d_info['축스탯'] = 18000
        d_info['아포스탯'] = 17000
        d_info['축공격력'] = 2000
        d_info['버퍼속저깍'] = 60
        d_info['몹속저'] = 50
        d_info['비진각보정'] = 1.15
        d_info['공격유형'] = {}
        d_info['공격유형']['지속딜']=  {'시간':70, '방어력':99.8, '반영스탯':['축스탯'], '계산식':'지속딜*1.7+그로기딜*0.5', '정령왕':1.10, '반영률':0.8, '제외스킬':[50, 85, 100]}
        d_info['공격유형']['그로기딜'] = {'시간':25., '방어력':99.6, '반영스탯':['축스탯', '아포스탯'], '계산식':'그로기딜*2', '정령왕':1.16, '반영률':1, '제외스킬': None}

        character.char_stat['skilltree'].calculate_deal(d_info)

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

        if self.test_mode is True:
            with open("result.json", "w") as f:
                json.dump(character.char_stat, f)

    def __init__(self, cid, sid, test_mode = False):
        self.test_mode = test_mode
        self.inner_data = {}

        try:
            raw_dicts = self.get_dicts(sid, cid)
        except:
            self.status = ('error', 'Neople API 접속불가')
            return None

        self.s_dict, self.sw_dict, self.sk_dict = raw_dicts[0:3]
        self.e_dict, self.c_dict, self.a_dict, self.g_dict, self.t_dict = raw_dicts[3:8]

        sw_dict = self.sw_dict
        
        if sw_dict['skill']['buff'] is None:
            self.status = ('error', '버프강화 미지정')
            return None

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
            cbuff = self.buff_dict[self.classid][self.jobid]
            self.isBuffer = False

        self.char_stat = {
                '레벨':self.level, '이름':self.name, '서버':self.server, '모험단':self.advname, 'class':self.classname, '전직':self.jobname, 'ids':(sid, cid), '버퍼여부':self.isBuffer, 'jobid':self.jobid,
                '스공':1, '증댐':0, '크증댐':0, '추댐':0, '속추댐':0,
                '물마독공':0, '힘지':0, '모공':0, '지속댐':0, '증추':0, '크증추':0,
                '패시브':{}
            }

        self.analyze_sw(cbuff)
        self.analyze_stat()

        self.char_stat['inventory'] = Inventory(self.e_dict, self.c_dict, self.a_dict, self.g_dict, self.t_dict, self.test_mode)
        self.char_stat['skilltree'] = SkillTree(self, self.test_mode)
        self.char_stat['inventory'].bind_skill(self.char_stat['skilltree'])
        self.char_stat['inventory'].analyze_enchants()
        self.char_stat['inventory'].analyze_avatar()
        self.char_stat['inventory'].analyze_flag_and_gem()
        typ, v = self.char_stat['inventory'].get_main_stat()
        #print('마부/아바타/젬 지능', v)
        v = self.calculate_base_stat(v, typ) + self.base_stat
        self.char_stat['inventory'].main_stat = {'type':typ, 'value':v}
        
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
 
            self.buffer['inventory'] = Inventory(sw_e_dict, sw_c_dict, sw_a_dict, self.g_dict, self.t_dict)
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

        final_stat = bless_stat + awk_stat + add_stat

        final_dam = self.char_stat['버프분석결과']['축']['공']['value']
        final_dam += add_dam

        # for scoring
        bless_stat += add_stat
        awk_stat += add_stat
                
        deal_ori = 1.31 * (1 + 15983/250) * 2600 * 1.34 * 1.5 * 0.004
        deal = 1.31 * (1+ (15983+ final_stat)/250) * (2600 + final_dam) * 1.34 * 1.5 * 0.004

        a_deal = 1.31 * (1+ (15983+ awk_stat)/250) * (2600 + final_dam) * 1.34 * 1.5 * 0.004

        if self.classname == '프리스트(여)':
            c_deal = 1.31 * (1+ (15983+ (bless_stat * 0.95))/250) * (2600 + final_dam) * 1.34 * 1.5 * 0.004
        elif self.classname == '마법사(여)':
            c_deal = 1.31 * (1+ (15983+ (bless_stat * 0.95))/250) * (2600 + final_dam) * 1.34 * 1.5 * 0.004
        else:
            c_deal = 1.31 * (1+ (15983+ (bless_stat * 0.975))/250) * (2600 + final_dam) * 1.34 * 1.5 * 0.004

        dealp = (deal/100 - 100)

        deal_amp_base = deal/deal_ori
        deal_amp = round(((deal/deal_ori * 100) - 100) * 700)

        cdeal_amp_base = c_deal/deal_ori
        cdeal_amp = round(((c_deal/deal_ori * 100) - 100) * 700)

        adeal_amp_base = a_deal/deal_ori
        adeal_amp = round(((a_deal/deal_ori * 100) - 100) * 700)

        final_score = deal_amp
        c_score = cdeal_amp
        g_score = adeal_amp

        self.char_stat['버프분석결과']['점수표'] = (c_score, g_score, final_score, dealp, deal)
        self.char_stat['버프분석결과']['최종버프'] = {'공격력':round(final_dam), '힘/지능':round(final_stat)}

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

            if self.classTypeNeo is True:
                awkact = skilltree.skill_enchant['100']
                si = awkact['actives'][0]
                blv = 2
                mfact = 1.7
                afact = 1.5
            else:
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

            if self.char_stat['속강딜증가'] > 230:
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
     
            g_jo_real = int(g_real_deal / 100000000000000)
            g_2nd_real = int((g_real_deal % 100000000000000)/10000000000) 
            
            if g_jo_real > 0:
                g_text = str(g_jo_real)+'조 '+str(g_2nd_real)+'억'
            else:
                g_text = str(g_2nd_real)+'억'

            report['시로코1시딜'] = g_real_deal
            deal_text = '시로코 1시 그로기딜(25초)은 ' + g_text +' 입니다.'

            g_score = self.char_stat['시로코분석결과']['그로기딜']['점수']
            c_score = self.char_stat['시로코분석결과']['지속딜']['점수']
            report['점수표'] = self.char_stat['시로코분석결과']['점수표']

            if g_score > c_score*1.05*0.85:
                postfix.append('폭딜러')
            elif g_score*1.05 < c_score*0.85:
                postfix.append('지딜러')
            else:
                postfix.append('멀티플레이어')
        else:
            buff30_dam = round(self.char_stat['버프분석결과']['축']['공']['value'])
            buff30_stat = round(self.char_stat['버프분석결과']['축']['힘지']['value'])
            if self.classname in ['마법사(여)', '프리스트(여)']:
                add_stat = round(sum(list(self.char_stat['버프분석결과']['보조스킬'].values())))
            else:
                add_stat = round(self.char_stat['버프분석결과']['보조스킬']['신념의 오라'])
                add_dam = round(self.char_stat['버프분석결과']['보조스킬']['크로스 크래쉬'])
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

            dealp = self.char_stat['버프분석결과']['점수표'][3]

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
                    report_type = '신이 곁에 있음을 깨닫게 합니다.'
                elif 80 < dealp <= 100:
                    report_type = '신의 힘을 갖게 합니다.'
                elif 100 < dealp:
                    report_type = '무신(武神)의 경지를 느낍니다.'

            deal = self.char_stat['버프분석결과']['점수표'][4]

            deal_base = int(deal)/10000
            deal_jo = math.ceil(deal_base) - 1
            deal_uk = int(deal)%10000

            report['버프점수표'] = self.char_stat['버프분석결과']['점수표']
            
        wep_reinforce = inventory.weapon_info['reinforce']
        avg_reinforce = inventory.inner_data['평균증폭수치']
        remodel_count = inventory.inner_data['산물장착수']
        high_remodel = inventory.inner_data['최대개조수치']
        max_reinforce = inventory.inner_data['최대증폭수치']

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
            postfix.append('증폭의 왕')
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
            myth_count = epic_status['신화']
            epic_count = epic_status['에픽']
            indo_count = epic_status['지옥파티']
            myth_list = epic_status['신화목록']
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

            if indo_count >= 5000:
                prefix.append('지혜의 인도에 녹아버린')
            elif indo_count >= 4000:
                prefix.append('지혜의 인도에 미쳐버린')
            elif indo_count >= 3000:
                prefix.append('지혜의 인도가 지겨운')
            elif indo_count >= 2000:
                prefix.append('지혜의 인도에 빠진')

            if isBuffer is False:
                if myth_tier[0] == 3:
                    postfix.append('군심나를 다 가진 궁댕이맨')
                elif myth_tier[0] >= 1:
                    postfix.append('군심나의 선택을 받은자')
                elif myth_tier[0] == 0 and myth_tier[1] > 0:
                    postfix.append('신화메타 승리자')
                elif sum(myth_tier[0:3]) == 0 and myth_tier[3] > 0:
                    postfix.append('신화메타 실패자')
                elif sum(myth_tier[0:4]) == 0 and myth_tier[4] > 0:
                    postfix.append('흐무시아 오너')
            else:
                if myth_tier[0] >= 1:
                    postfix.append('광흑의 선택을 받은자')
                elif myth_tier[0] == 0 and myth_tier[1] > 0:
                    postfix.append('신화메타 승리자')
                elif sum(myth_tier[0:3]) == 0 and sum(myth_tier[3:]) > 0:
                    postfix.append('신화메타 실패자')

            if myth_count >= 5:
                postfix.append('신화돼지') 

        pcharname = '???'

        if len(prefix) == 0:
            prefix.append('특징없는')

        if len(postfix) == 0:
            if isBuffer is True:
                postfix.append('평범한 버퍼')
            else:
                if self.classTypeNeo is True:
                    postfix.append('평범한 딜러')
                else:
                    postfix.append('아무거나')

        prefix_text = ', '.join(prefix)
        postfix_text = ', '.join(postfix)


        if isBuffer is False:
            report_text = prefix_text + ' ' + server + ' - ' + pcharname +'은(는) ' + postfix_text + ' 이며, ' + deal_text
        else:
            if deal_jo >= 1:
                d_text = str(deal_jo) + '조 '+ str(deal_uk)
            else:
                d_text = str(deal_uk)
            
            report_text = prefix_text +' '+ server + ' - ' + pcharname + '은(는) '+ postfix_text+'이며 시로코1시 1조 딜러의 딜을 '+ d_text +'억으로 ' + str(round(abs(dealp),2)) +'% '+report_inc+'시켜 ' + report_type       

        report['explain'] = report_text

        return report


