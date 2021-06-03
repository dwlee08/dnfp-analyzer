from json import loads
import json
import numpy as np
import math
from statistics import mean
#import re

elem_type = ['화속성', '명속성', '수속성', '암속성']

class SkillTree():
    skill_db = None
    passive_db = None
    buffer_db = None

    @classmethod
    def initstatic(cls):
        with open("./skill_db.json","r") as f:
            cls.skill_db = json.load(f)

        with open("./passive.json", "r") as f:
            cls.passive_db = json.load(f)

        with open('./buffer_db.json', "r") as f:
            cls.buffer_db = json.load(f)
 
        with open('./factor_dict.json',"r") as f:
            cls.factor_db = json.load(f)

    @classmethod
    def get_neo_jobid(cls, classid, jobid):
        class_skills = cls.skill_db[classid]

        for k, v in class_skills.items():
            if k == 'name':
                continue
            if v['pjid'] == jobid:
                return k

        return None

    def build_skill_enchant(self):
        myskill_dict = self.owner.sk_dict['skill']['style']
        myskill_list = myskill_dict['active'] + myskill_dict['passive']

        if self.owner.jobname == '眞 메카닉':
            if self.has_skill(myskill_list, '솔라 모듈 시스템'):
                self.inner_data['skillpassive'] = (True, '스패로우 팩토리', '솔라 모듈 시스템')
            else:
                self.inner_data['skillpassive'] = (False, '스패로우 팩토리', '솔라 모듈 시스템')

        elif self.owner.jobname == '眞 엘레멘탈마스터':
            if self.has_skill(myskill_list, '썬더 스트라이크'):
                self.inner_data['skillpassive'] = (True, '썬더 콜링', '썬더 스트라이크')
            else:
                self.inner_data['skillpassive'] = (False, '썬더 콜링', '썬더 스트라이크')

        elif self.owner.jobname == '眞 배틀메이지':
            if self.has_skill(myskill_list, '황룡난무'):
                self.inner_data['skillpassive'] = (True, '황룡천공', '황룡난무')
            else:
                self.inner_data['skillpassive'] = (False, '황룡천공', '황룡난무')

        for skill in self.skill_list:
            skid = skill['skillId']
 
            for myskill in myskill_list:
                if skid == myskill['skillId']: 
                    req = myskill['requiredLevel']
                    level = myskill['level']
                    
                    #비진각 캐릭터 50렙제
                    if req == 50:
                        level += 1
     
                    self.skill_enchant[str(req)]['skills'].append([skill, level, 0, level])
      
        for myskill in myskill_list:
            skid = myskill['skillId']
            name = myskill['name']
            req = myskill['requiredLevel']
            level = myskill['level']

            self.init_factor(name, skid, req, level)
        
        for myskill in myskill_list:
            skid = myskill['skillId']
            name = myskill['name']
            req = myskill['requiredLevel']
            lvl = myskill['level']

            if name == '크리티컬 히트':
                rlist = list(range(0, 21))
                data = {
                        'name':name, 'skillId':skid,
                        'skillType':'passive', 'type':'크리티컬히트', 
                        'values':rlist, 'req':20
                        }

                self.skill_enchant[str(req)]['skills'].append([data, lvl, 0, lvl])
            elif name == '무기의 극의':
                rlist = [0] + list(range(2, 40))
                data = {
                        'name':name, 'skillId':skid,
                        'skillType':'passive', 'type':'없음', 
                        'values' : rlist, 'req':15
                        }

                self.skill_enchant[str(req)]['skills'].append([data, lvl, 0, lvl])
            elif name == '히트엔드':
                rlist = [0] + list(range(81, 141, 2))
                data = {
                        'name':name, 'skillId':skid,
                        'skillType':'passive', 'type':'없음', 
                        'values' : rlist, 'req':15
                        }

                self.skill_enchant[str(req)]['skills'].append([data, lvl, 0, lvl])
            elif name == '인법 : 잔영 남기기':
                rlist = [0] + list(range(100, 122, 2))
                data = {
                        'name':name, 'skillId':skid,
                        'skillType':'passive', 'type':'없음', 
                        'values' : rlist, 'req':35
                        }
                self.skill_enchant[str(req)]['skills'].append([data, lvl, 0, lvl])
            elif name == '디바인 퍼니쉬먼트':
                rlist = [0]
                for i in range(1,41):
                    rlist.append(math.floor(2.5*i+10)*24)

                data = {'name':name, 'skillId':skid,
                        'type':'패시브스탯', 'values':rlist, 'req':req, 'subtype':'오라'}

                self.skill_enchant[str(req)]['skills'].append([data, lvl, 0, lvl])
            elif name in ['매거진 드럼', '니트로 모터']:
                rlist = [0] + list(range(2, 42, 2))
                data = {
                        'name':name, 'skillId':skid,
                        'skillType':'passive', 'type':'없음', 
                        'values' : rlist, 'req':15
                        }

                self.skill_enchant[str(req)]['skills'].append([data, lvl, 0, lvl])
            elif name == '유탄 마스터리':
                rlist = [0] + list(range(10, 201, 10))
                data = {
                        'name':name, 'skillId':skid,
                        'skillType':'passive', 'type':'없음', 
                        'values' : rlist, 'req':20
                        }
                #print(name)
                self.skill_enchant[str(req)]['skills'].append([data, lvl, 0, lvl])

            elif req >= 50 and name[-2:] == '강화':
                skname = name[:-3]

                if skname == '류탄':
                    #print(name, skname)
                    si = self.get_skill_instance('actives', 'G-35L 섬광류탄')
                    if si is not None:
                        si['dam'] *= (1 + 0.1*lvl)
                        si['invest'].append('TP:'+str(lvl))


                    si = self.get_skill_instance('actives', 'G-18C 빙결류탄')
                    if si is not None:
                        si['dam'] *= (1 + 0.1*lvl)
                        si['invest'].append('TP:'+str(lvl))


                    si = self.get_skill_instance('actives', 'G-14 파열류탄')
                    if si is not None:
                        si['dam'] *= (1 + 0.1*lvl)
                        si['invest'].append('TP:'+str(lvl))

                if skname == '류심':
                    si = self.get_skill_instance('actives', '류심 쾌')
                    if si is not None:
                        si['dam'] *= (1 + 0.1*lvl)
                        si['invest'].append('TP:'+str(lvl))

                    si = self.get_skill_instance('actives', '류심 강')
                    if si is not None:
                        si['dam'] *= (1 + 0.1*lvl)
                        si['invest'].append('TP:'+str(lvl))

                    si = self.get_skill_instance('actives', '류심 승')
                    if si is not None:
                        si['dam'] *= (1 + 0.1*lvl)
                        si['invest'].append('TP:'+str(lvl))

                sil = self._get_skill_instance_all('actives', skname, None)
                if len(sil) > 0:
                    for si in sil:
                        si = si[0]
                        if skname == '흑염의 칼라':
                            si = self.get_skill_instance('actives', '흑염검')
                            if si is not None:
                                si['dam'] *= (1 + 0.1*lvl)
                        elif self.owner.classname == '격투가(여)' and skname == '크레이지 발칸':
                            hit = 8 + lvl
                            si['dam'] *= (hit/13)
                        elif self.owner.classname == '거너(남)' and skname == '더블 건호크':
                            si['dam'] *= (1 + 0.1462*lvl)
                        else:
                            si['dam'] *= (1 + 0.1*lvl)

                        si['invest'].append('TP:'+str(lvl))

        for fitem in self.factor_data:
            if fitem['skillName'] == '평타':
                penchant = fitem['penchant']
                poison = fitem['poison']

                data = {'name':'평타', 'skillId':None, 'req':1, 'dam':1, 'cool':1, 'cooltime': fitem['cool'], 'factor': fitem['factor'], 'longterm':fitem['longterm'], 'oriname':None, 'invest':[]}
                data['penchant'] = penchant if penchant != '' else None
                data['poison'] = poison if poison != '' else None

                self.skill_enchant['1']['actives'].append([data, 100, 0, 100, 100])

    def init_factor(self, name, skid, req, lvl):
        blevel = 0
        base_cool = 1
        base_inc = 0
        jobname = self.owner.jobname
        """
        직업별 특수처리
        """
        #무기의 극의 처리
        if jobname == '眞 웨펀마스터' and name.find('마스터리') >= 0:
            blevel = 1
        #프렌지 및 갈증 쿨감
        elif jobname == '眞 버서커' and name in ['블러드 러스트', '레이징 퓨리', '고어 크로스', '블러드 소드', '블러디 레이브', '아웃레이지 브레이크']:
            base_cool = 0.8
        #중화기개조
        elif jobname == '眞 런처' and req not in [50, 85, 100]:
            base_inc = 1

        skillpassive = self.inner_data.get('skillpassive')

        for fitem in self.factor_data:
            if name == fitem['skillName']:
                if skillpassive is not None:
                    skp_on, skp_name, skp_passive = skillpassive
                    if name == skp_name:
                        if skp_on is True and fitem['skillOriName'] != skp_passive:
                                continue
                        if skp_on is False and fitem['skillOriName'] == skp_passive:
                                continue

                if blevel == 0:
                    blevel = fitem['baselevel']

                if lvl < int(0.1 * blevel):
                    break

                mlevel = fitem['maxlevel']
                factor = fitem['factor']
                longterm = fitem['longterm']
                poison = fitem['poison']
                penchant = fitem['penchant']
                talisman = fitem['talisman']
                weptypeinfo = fitem['weptypeinfo']
                oriname = fitem['skillOriName']
                cool = fitem['cool']
                if name in ['썬더 스트라이크', '썬더 콜링'] or self.owner.jobname == '眞 소환사':
                    coolfixed = False
                elif oriname in ['환영폭쇄', '금기 : 독사굴']:
                    coolfixed = False
                else:
                    coolfixed = fitem['coolFixed']


                data = {'name':name, 'skillId':skid, 'req':req, 'dam':1, 'cool':base_cool, 'oriname':oriname, 'invest':[]}

                data['factor'] = factor if factor != '' else None
                data['cooltime'] = cool if cool != '' else None
                data['longterm'] = longterm if longterm != '' else None
                data['poison'] = poison if poison != '' else None
                data['penchant'] = penchant if penchant != '' else None
                data['coolFixed'] = coolfixed

                if talisman != '':
                    (tname, tfactor, dammode) = talisman[1:-1].split(',')
                    tal_list = self.owner.t_dict['talismans']
                    if tal_list is not None:
                        isFound = False
                        for tal in tal_list:
                            mytname = tal['talisman']['itemName']
                            if mytname.find(tname) >= 0:
                                isFound = True
                                break
                        if isFound == True:
                            if dammode == 'f':
                                if data.get('longterm') != None:
                                    del data['longterm']
                                data['factor'] = int(tfactor)
                            else:
                                if data.get('factor') != None:
                                    del data['factor']
                                data['longterm'] = int(tfactor)

                if weptypeinfo != '':
                    (wtype, wfactor,dammode) = weptypeinfo[1:-1].split(',')
                    if wtype == self.owner.char_stat['inventory'].weapon_info['type']:
                        if dammode == 'f':
                            if data.get('longterm') != None:
                                del data['longterm']
                            data['factor'] = int(wfactor)
                        else:
                            if data.get('factor') != None:
                                del data['factor']
                            data['longterm'] = int(wfactor)

                self.skill_enchant[str(req)]['actives'].append([data, lvl, base_inc, blevel, mlevel])

    def __init__(self, char, test_mode = False):
        self.test_mode = test_mode
        self.owner = char
        self.inner_data = {}

        classid = char.classid
        jobid = char.jobid

        self.skill_enchant = {
            '1':{'level':0, 'cool':1, 'dam':1, 'skills':[], 'actives':[]},
            '5':{'level':0, 'cool':1, 'dam':1, 'skills':[], 'actives':[]},
            '10':{'level':0, 'cool':1, 'dam':1, 'skills':[], 'actives':[]},
            '15':{'level':0, 'cool':1, 'dam':1, 'skills':[], 'actives':[]},
            '20':{'level':0, 'cool':1, 'dam':1, 'skills':[], 'actives':[]},
            '25':{'level':0, 'cool':1, 'dam':1, 'skills':[], 'actives':[]},
            '30':{'level':0, 'cool':1, 'dam':1, 'skills':[], 'actives':[]},
            '35':{'level':0, 'cool':1, 'dam':1, 'skills':[], 'actives':[]},
            '40':{'level':0, 'cool':1, 'dam':1, 'skills':[], 'actives':[]},
            '45':{'level':0, 'cool':1, 'dam':1, 'skills':[], 'actives':[]},
            '48':{'level':0, 'cool':1, 'dam':1, 'skills':[], 'actives':[]},
            '50':{'level':0, 'cool':1, 'dam':1, 'skills':[], 'actives':[]},
            '60':{'level':0, 'cool':1, 'dam':1, 'skills':[], 'actives':[]},
            '70':{'level':0, 'cool':1, 'dam':1, 'skills':[], 'actives':[]},
            '75':{'level':0, 'cool':1, 'dam':1, 'skills':[], 'actives':[]},
            '80':{'level':0, 'cool':1, 'dam':1, 'skills':[], 'actives':[]},
            '85':{'level':0, 'cool':1, 'dam':1, 'skills':[], 'actives':[]},
            '95':{'level':0, 'cool':1, 'dam':1, 'skills':[], 'actives':[]},
            '100':{'level':0, 'cool':1, 'dam':1, 'skills':[], 'actives':[]},
        }
        try:
            self.skill_data = self.skill_db[classid][jobid]['skills']
            self.factor_data = self.factor_db[classid][jobid]

            if char.buffer is not None:
                self.skill_list = self.passive_db[classid][jobid] + self.buffer_db[classid][jobid]
            else:
                self.skill_list = self.passive_db[classid][jobid]
        
        except:
            raise

        self.build_skill_enchant()

        if self.test_mode is True:
            with open('skill_data.json', 'w') as f:
                json.dump(self.skill_data, f)

    def get_skills_by_level(self, typ, req):
        return self.skill_enchant[str(req)][typ]

    def _get_skill_instance(self, typ, name, req):
        if req is None:
            for lv, item in self.skill_enchant.items():
                skills = item[typ]
                for skill in skills:
                    data = skill[0]
                    if data['name'].replace(' ','') == name.replace(' ',''):
                        return skill
                    
                    if typ == 'actives' and isinstance(data['oriname'], str) and data['oriname'].replace(' ','') == name.replace(' ',''):
                        return skill
        else:
            skills = self.skill_enchant[str(req)][typ]
            for skill in skills:
                data = skill[0]
                if data['name'].replace(' ','') == name.replace(' ',''):
                    return skill
                if typ == 'actives' and isinstance(data['oriname'], str) and data['oriname'].replace(' ','') == name.replace(' ',''):
                    return skill
           
        return None

    def _get_skill_instance_all(self, typ, name, req):
        skill_instances = []
        if req is None:
            for lv, item in self.skill_enchant.items():
                skills = item[typ]
                for skill in skills:
                    data = skill[0]
                    if data['name'].replace(' ','') == name.replace(' ',''):
                        skill_instances.append(skill)
                    if typ == 'actives' and isinstance(data['oriname'], str) and data['oriname'].replace(' ','') == name.replace(' ',''):
                        skill_instances.append(skill)
 
        else:
            skills = self.skill_enchant[str(req)][typ]
            for skill in skills:
                data = skill[0]
                if data['name'].replace(' ','') == name.replace(' ',''):
                    skill_instances.append(skill)
                if typ == 'actives' and isinstance(data['oriname'], str) and data['oriname'].replace(' ','') == name.replace(' ',''):
                    skill_instances.append(skill)
 
        return skill_instances

    def handle_special_case(self):
        if self.owner.jobname == '眞 로그':
            si = self.get_skill('skills', '히트엔드', req = 15)
            data = si[0]
            lv = min(si[1] + si[2], len(data['values']) - 1)

            hitend_add = 0 if '히트엔드추가' not in self.inner_data.keys() else self.inner_data['히트엔드추가']
            hitend = data['values'][lv]
            mywtype = self.inventory.weapon_info['type']

            if mywtype == '단검':
                hitend *= (4.25 + hitend_add)
            else:
                hitend *= (4.74 + hitend_add)

            self.inner_data['히트엔드'] = hitend
               
        elif self.owner.jobname == '眞 쿠노이치':
            si = self.get_skill('skills', '인법 : 잔영 남기기', req = 35)
            data = si[0]
            lv = min(si[1] + si[2], len(data['values']) - 1)

            mirage = data['values'][lv] - 100
                    
            self.inner_data['잔영'] = mirage

            """
            si = self.get_skill('actives', '인법 : 육도윤회', req = 40)
            data = si[0]

            print(data)
            """

        elif self.owner.jobname == '眞 엘븐나이트':
            si = self.get_skill('actives', '체인러쉬', req = 30)
            data = si[0]
            lv = min(si[1] + si[2], 16)

            chainrush = (lv * 0.5 + 12.5)

            si = self.get_skill('skills', '대자연의 가호', req = 48)
            data = si[0]
            lv = min(si[1] + si[2], 40)

            nature = (lv * 2)

            self.inner_data['체인러쉬'] = (chainrush * 6, nature)

        elif self.owner.jobname == '眞 스핏파이어' and self.owner.classname == '거너(남)':
            si = self.get_skill('skills', '매거진 드럼', req = 15)
            lv = min(si[1] + si[2], 20)

            self.inner_data['사격강화'] = lv*2

            si = self.get_skill('skills', '유탄 마스터리', req = 20)
            if si is not None:
                data = si[0]
                lv = min(si[1] + si[2], 20)

                fragup = data['values'][lv]
                self.inner_data['류탄강화'] = fragup
            else:
                self.inner_data['류탄강화'] = 0

        elif self.owner.jobname == '眞 스핏파이어' and self.owner.classname == '거너(여)':
            si = self.get_skill('skills', '니트로 모터', req = 15)
            lv = min(si[1] + si[2], 20)

            self.inner_data['사격강화'] = lv*2

            si = self.get_skill('skills', '유탄 마스터리', req = 20)

            if si is not None:
                data = si[0]
                lv = min(si[1] + si[2], 20)

                fragup = data['values'][lv]
                self.inner_data['류탄강화'] = fragup
            else:
                self.inner_data['류탄강화'] = 0
        elif self.owner.jobname == '眞 데몬슬레이어':
            si = self.get_skill('skills', '탐욕의 번제', req = 48)

            if si is not None:
                data = si[0]
                lv = min(si[1] + si[2], 40)

                self.inner_data['탐욕의 번제'] = data['values'][lv]
            else:
                self.inner_data['탐욕의 번제'] = 0

        elif self.owner.jobname == '眞 빙결사':
            si = self.get_skill('skills', '아이스크래프트', req = 75)

            if si is not None:
                data = si[0]
                lv = min(si[1] + si[2], 40)

                self.inner_data['얼음창'] = (1 + 1.5 * data['values'][lv]/100) / (1 + data['values'][lv]/100) 

            else:
                self.inner_data['얼음창'] = 1
        elif self.owner.jobname == '眞 레인저' and self.owner.classname == '거너(여)':
            si = self.get_skill('skills', '체인 인라이튼', req = 95)

            if si is not None:
                data = si[0]
                lv = min(si[1] + si[2], 40)

                self.inner_data['체인 인라이튼'] = (1 + data['values'][lv]/100)

            else:
                self.inner_data['체인 인라이튼'] = 1
        elif self.owner.jobname == '眞 검귀':
            si = self.get_skill('skills', '악귀현신', req = 95)

            if si is not None:
                self.inner_data['악귀현신'] = 1
            else:
                self.inner_data['악귀현신'] = 0
        elif self.owner.jobname == '眞 다크템플러':
            si = self.get_skill('skills', '베스퍼스', req = 75)

            if si is not None:
                data = si[0]

                lv = min(si[1] + si[2], 40)
                self.inner_data['베스퍼스'] = (1 + data['values'][lv]/100)
            else:
                self.inner_data['베스퍼스'] = 1

        """
        elif self.owner.jobname == '眞 스트리트파이터' and self.owner.classname == '격투가(여)':
            si = self.get_skill('actives', '독문무공', req = 85)

            if si is not None:
                lv = si[1] + si[2]

                self.inner_data['독문스증'] = (1 + (2 * lv / 100))
        
        elif self.owner.jobname == '眞 스트라이커' and self.owner.classname == '격투가(남)':
            si = self.get_skill('actives', '화염의 각', req = 50)

            if si is not None:
                lv = si[1] + si[2]

                self.inner_data['화각스증'] = (1 + ((4 * lv - 2) / 100))
        """


    def get_skill_instance(self, typ, name, req = None):
        skill = self._get_skill_instance(typ, name, req)

        if skill is not None:
            return skill[0]
        else:
            return None

    def get_skill(self, typ, name, req = None):
        skill = self._get_skill_instance(typ, name, req)

        return skill
    
    """
    def increase_skill_level(self, typ, name, inc, req = None):
        skill = self._get_skill_instance(typ, name, req)

        if skill is not None:
            skill[2] += inc
        else:
            raise Exception
    """

    def increase_skill_level(self, typ, name, inc, req = None, base = False):
        skill_list = self._get_skill_instance_all(typ, name, req)

        if len(skill_list) == 0:
            return False

        for skill in skill_list:
            if base is True:
                skill[1] += inc
            else:
                skill[2] += inc

        return True

    def increase_skill_level_range(self, typ, lvrange, inc, base = False):
        ret = []
        minlv, maxlv = lvrange
        minlv = int(minlv)
        maxlv = int(maxlv)
        for lv, val in self.skill_enchant.items():
            lvl = int(lv)

            if minlv <= lvl <= maxlv:
                skills = val[typ]

                for skill in skills:
                    ret.append(skill[0]['name'])
                    if base is True:
                        skill[1] += int(inc)
                    else:
                        skill[2] += int(inc)

        return ret

    def finalize_levelup(self):
        self.owner.char_stat['레벨링구간'] = {}

        for lv, val in self.skill_enchant.items():
            lvup = val['level']
            #print("최종", lv, lvup)

            for skill in val['skills']:
                skill[2] += lvup

            for skill in val['actives']:
                skill[2] += lvup

            self.owner.char_stat['레벨링구간'][lv] = lvup
 
       
    def has_skill(self, target, skname):
        for skill in target:
            if skill['name'] == skname:
                return True

        return False

        #퇴마사 진격의 황룡 염주 데미지
        #스패로우 팩토리, 솔라 모듈 시스템(솔라 모듈 있으면 스패로우 데미지 삭제)
        #여스파 독데미지 계산
        #탈리스만 있을때 완전 데미지 변경 (템페스터, 게일포스) 지딜 -> 폭딜
    """
    def prepare_buffer_passive(self):
        if self.buffer is None or self.buffer.get('main_stat') is None
            return

        for se in self.skill_enchant.values():
            for sk in se['skills']:
                data = sk[0]
                lv = sk[1]
               
                v = data['values'][lv]
                typ = data['type']

                if typ == '패시브스탯':
                    if data.get('subtype') != '오라':
                        char_stat['아포'][data['name']]=[v]
                        char_stat['아포']['스탯'] += v 
                        #print ('- 패시브기본(아포)', data['name'], v)
                    else:
                        char_stat['아포'][data['name']] = 0
    """ 

    def finalize_passive(self):
        char_stat = self.owner.char_stat
        mywep_type = char_stat['inventory'].weapon_info['type']
        mywep_name = char_stat['inventory'].weapon_info['name']

        passive_inc = 1
        passive_orig = 1

        elem_orig = max([char_stat['화속성강화'], char_stat['명속성강화'], char_stat['수속성강화'], char_stat['암속성강화']])
 
        self.inner_data['쿨패시브'] = 1
        for req, se in self.skill_enchant.items():
            for pas in se['skills']:
                data = pas[0]
                lv = pas[1]
                base = pas[3]

                sname = data['name']
                typ = data['type']
                stype = data.get('skillType')
                wep_type = data.get('wep_type')
                mastery = data.get('mastery')

                if wep_type is not None and wep_type != mywep_type:
                    continue
                try:
                    v3 = data['values'][base-1]
                except:
                    print(base)
                    v3 = 0

                lv = min(len(data['values']) - 1, lv)

                if mastery is True and '무기의 극의' in self.inner_data.keys():
                    v1 = data['values'][lv + self.inner_data['무기의 극의']['기본레벨']]
                    nlevel = min(len(data['values']) - 1, lv + self.inner_data['무기의 극의']['마스터리레벨'])
                else:
                    v1 = data['values'][lv]
                    nlevel = min(len(data['values']) - 1, lv + pas[2])

                v2 = data['values'][nlevel]

                v1 = 0 if isinstance(v1, str) else v1
                v2 = 0 if isinstance(v2, str) else v2
                v3 = 0 if isinstance(v3, str) else v3

                if '초월의 룬' in self.inner_data.keys():
                    if sname == '쇼타임' and typ == '쿨감':
                        #print (sname, v2, self.inner_data['초월의 룬']['쿨감'])
                        v2 *= self.inner_data['초월의 룬']['쿨감']

                    elif sname == '속성 마스터리' and typ == '데미지':
                        v2 *= self.inner_data['초월의 룬']['데미지']

                    elif sname == '마력 증폭' and typ == '크리티컬히트':
                        v2 += self.inner_data['초월의 룬']['크리티컬']

                v = v2 - v1

                #print (pdata['name'], typ, v1, v2, curlvl, curlvl + pas[2] + lvup, pas[2], lvup)

                if typ == '공이속':
                    char_stat['공격속도'] += v
                    char_stat['이동속도'] += v
                elif typ == '이속':
                    char_stat['이동속도'] += v
                elif typ == '공속':
                    char_stat['공격속도'] += v
                elif typ == '캐속':
                    char_stat['캐스팅속도'] += v
                elif typ == '크리티컬히트':
                    char_stat['물리크리티컬'] += v
                    char_stat['마법크리티컬'] += v
                elif typ.find('저항') >= 0:
                    elem = typ.split('속성')[0][-1]
                    if elem == '든':
                        for et in elem_type:
                            char_stat[et + '저항'] += v
                    else:
                        char_stat[elem + '속성저항'] += v

                elif typ.find('강화') >= 0:
                    if (data.get('skillType') == 'passive' and sname != '원소 융합') or sname == '아이스 로드':
                        inc = v
                    else:
                        inc = v2

                    elem = typ.split('속성')[0][-1]
                    if elem == '든' or elem == '사':
                        for et in elem_type:
                            char_stat[et + '강화'] += inc
                        t = '모든'
                    else:
                        t = elem
                        char_stat[elem + '속성강화'] += inc

                    if char_stat['패시브'].get(sname) is not None:
                        char_stat['패시브'][sname].update({'레벨':lv + pas[2], t+'속성강화':v2, 'base':v3, 'req':int(req)})
                    else:
                        char_stat['패시브'][sname] = {'레벨':lv + pas[2], t+'속성강화':v2, 'base':v3, 'req':int(req)}

                elif typ == '쿨감':
                    if sname == '윌 드라이버' and mywep_type != '토템':
                        continue

                    #TODO: level 대신 개별 스킬로 쿨타임 적용

                    self.inner_data['쿨패시브'] *= (1 - v2/100)
                    for clv, cinfo in self.skill_enchant.items():
                        if sname in ['강인한 신념', '병기 숙련', '원소 폭격', '윌 드라이버', '세라픽 페더', '블러드', 'HS-1 친구들', 'G-오퍼레이터', '쇼타임', '휘몰아치는 질풍의 봉 마스터리', '거병 마스터리', '장창 숙련', '화염의 각'] and clv in ['50', '85', '100']:
                            continue

                        askill_list = cinfo['actives']

                        for askill in askill_list:
                            data = askill[0]
                            asname = data['name']

                            if asname in ['블랙 망토', '변이 파리채', '대왕 파리채', '롤리팝 크러쉬']:
                                continue

                            if sname == '인술' and asname not in ['화염구', '환영 다중 수리검', '화염선풍', '나선 대차륜 쿠나이', '열화천도', '두꺼비유염탄', '비기 : 염무개화', '마환 풍마 수리검', '야마타오로치', '아마테라스']:
                                continue

                            if data.get('cool') is not None:
                                data['cool'] *= (1 - v2/100)

                        #cinfo['cool'] *= (1 - v2/100)
                        #print('쿨감', sname, v2, lv, nlevel)
                elif typ == '데미지':
                    if sname in ['자각의 실마리', '각성의 실마리']:
                        self.skill_enchant['85']['dam'] *= (1 + v2/100)
                        continue
                    elif sname == '대자연의 가호':
                        self.skill_enchant['85']['dam'] *= (1 + v2/100)
                        self.skill_enchant['50']['dam'] *= (1 + v2/100)
                    elif sname == '천수천안':
                        self.inner_data['천수천안'] = 14.5 + v2
                    elif sname == '현자의 돌':
                        self.inner_data[sname] = v2

                        char_stat['패시브'][sname] = {'레벨':lv + pas[2], '데미지증가':v2 , 'base':v3, 'req':int(req)}
                            #char_stat['패시브']['호문쿨루스'] = {'레벨':lv + pas[2], '데미지증가':v2-5}
                        continue
                    
                    if sname == '코어 블레이드 마스터리' and mywep_name == '프로젝트 : 오버코어':
                        v2 *= 2

                    passive_orig *= (1 + v1/100)
                    passive_inc *= (1 + v2/100)
                    
                    if char_stat['패시브'].get(sname) is not None:
                        char_stat['패시브'][sname].update({'레벨':lv + pas[2], '데미지증가':v2, 'base':v3, 'req':int(req)})
                    else:
                        char_stat['패시브'][sname] = {'레벨':lv + pas[2], '데미지증가':v2, 'base':v3, 'req':int(req)}

                elif typ == '패시브스탯' and self.owner.isBuffer is True:
                    main_stat_type = self.inventory.main_stat['type']
                    buffopt = self.buffoption
                    if data.get('subtype') != '오라':
                        inc = v2
                        self.inventory.main_stat['value'] += inc

                        #if buffopt['type'] == '아포':
                            #print ('지능증가', '패시브:'+sname, inc, v)
                            #print(sname, pas[1], pas[2])

                        char_stat['버프패시브'][sname] = v2
                        if buffopt['type'] == '아포':
                            char_stat[main_stat_type] += v

                    else:
                        aura_name = buffopt['오라']['name']
                        aura_val = buffopt['오라']['value']
                        
                        if sname == aura_name:
                            inc = v2 + aura_val
                            buffopt['오라']['value'] = inc
                        else:
                            inc = v2

                            char_stat['버프패시브'][sname] = v2

                        self.inventory.main_stat['value'] += inc
                        if buffopt['type'] == '아포':
                            char_stat[main_stat_type] += inc

                elif typ.find('추가') >= 0:
                    buff_type = self.buffoption['type']
                    if buff_type == '아포':
                        self.buffoption['보조스킬'][sname] = v2

        elem_inc = max([char_stat['화속성강화'], char_stat['명속성강화'], char_stat['수속성강화'], char_stat['암속성강화']])
                
        self.inner_data['레벨링패시브증가량'] = ((passive_inc/passive_orig) - 1) * 100   
        self.inner_data['레벨링속강증가량'] = elem_inc - elem_orig
        self.owner.char_stat['패시브레벨링증가량'] = self.inner_data['레벨링패시브증가량']
        self.owner.char_stat['속강패시브레벨링증가량'] = self.inner_data['레벨링속강증가량']
        self.inner_data['패시브총합'] = passive_inc

    def finalize_active(self):
        for lv, items in self.skill_enchant.items():
            dam = items['dam']
            cool = items['cool']

            for skill_items in items['actives']:
                act = skill_items[0]
                ori_level = skill_items[1]
                lvup = skill_items[2]
                mlevel = skill_items[3]
                maxlevel = skill_items[4]

                if ori_level + lvup > maxlevel:
                    lvup = (ori_level + lvup) - maxlevel
                elif ori_level + lvup < mlevel:
                    lvup = (ori_level + lvup) - mlevel
                
                if 1 <= int(lv) <= 20:
                    inc = 1 + (0.01 * lvup)
                elif 25 <= int(lv) <= 45:
                    inc = 1 + (0.02 * lvup)
                elif int(lv) == 50:
                    inc = 1 + (0.06 * lvup)
                elif 60 <= int(lv) <= 70:
                    inc = 1 + (0.03 * lvup)
                elif 75 <= int(lv) <= 80:
                    inc = 1 + (0.04 * lvup)
                elif int(lv) == 85:
                    inc = 1 + (0.12 * lvup)
                elif int(lv) == 95:
                    inc = 1 + (0.06 * lvup)
                elif int(lv) == 100:
                    inc = 1 + (0.19 * lvup)
                else:
                    inc = 1

                act['final_level'] = ori_level + skill_items[2]
                act['plus_level'] = skill_items[2]

                act['dam'] *= dam * inc

                acool = act.get('cooltime')
                if acool is not None and acool != '':
                    if 'coolFixed' in act.keys() and act['coolFixed']:
                        act['cool'] = 1
                        act['cooltime'] = float(act['cooltime'])
                    else:
                        act['cool'] *= cool

                        if isinstance(act['cooltime'], list):
                            try:
                                if act['final_level'] <= len(act['cooltime']):
                                    act['cooltime'] = float(act['cooltime'][act['final_level']]) * act['cool']
                                else:
                                    act['cooltime'] = float(act['cooltime'][0]) * act['cool']
                            except:
                                act['cooltime'] = float(act['cooltime'][0]) * act['cool']
                                pass
                        else:
                            act['cooltime'] = float(act['cooltime']) * act['cool']

    def apply_baselevel(self):
        char_stat = self.owner.char_stat
        mywep_name = char_stat['inventory'].weapon_info['name']
        town_inc = self.inventory.inner_data.get('마을적용패시브')
        if town_inc is None:
            town_inc = 0

        for req, se in self.skill_enchant.items():
            lvup = se['level']
            if req != '95':
                add_inc = town_inc
            else:
                add_inc = 0

            for pas in se['skills']:
                data = pas[0]

                sname = data['name']
                typ = data['type']
                wep_type = data.get('wep_type')

                if sname == '원소 융합':
                    self.owner.char_stat['암속성저항'] += 10

                if typ == '패시브스탯' and self.owner.isBuffer is True:
                    buff_type = self.buffoption['type']
                    if buff_type == '아포' and data.get('subtype') != '오라':

                        pas[1] += pas[2] + lvup
                        pas[2] = -1 * (lvup + add_inc)
                        continue

                if (data.get('skillType') == 'passive' and sname != '용독술') or sname == '아이스 로드':
                    if wep_type is not None and wep_type != self.inventory.weapon_info['type']:
                        continue

                    if typ == '데미지' and data['mastery'] is True:
                        char_dam_type = self.owner.inner_data.get('dam_type')

                        if self.owner.jobname == '眞 웨펀마스터':
                            si = self.get_skill('skills', '무기의 극의', req = 15)
                            lv = si[1] + si[2] + add_inc + lvup

                            lv = si[0]['values'][lv] + 1
                        else:
                            lv = pas[1] + pas[2] + lvup + add_inc

                        lv = min(len(data['values']) - 1, lv)
    
                        v = data['values'][lv]

                        if sname == '코어 블레이드 마스터리' and mywep_name == '프로젝트 : 오버코어':
                            v *= 2

                        self.owner.char_stat[char_dam_type] /= (1 + v/100)
                        self.owner.char_stat[char_dam_type] = int(self.owner.char_stat[char_dam_type])
                    
                    if typ not in ['데미지', '쿨감', '없음']:
                        pas[1] += pas[2] + lvup
                        pas[2] = -1 * (lvup + add_inc)
    
                    elif data['name'] == '차원일치':
                        lv = pas[1] + pas[2] + (lvup + add_inc)
 
                        v = data['values'][lv]

                        self.owner.char_stat['힘'] /= (1 + v/100)
                        self.owner.char_stat['지능'] /= (1 + v/100)
                        self.owner.char_stat['힘'] = int(self.owner.char_stat['힘'])
                        self.owner.char_stat['지능'] = int(self.owner.char_stat['지능'])
    
    def calculate_skills(self, deal_time, cooldown, pf, f, d, def_dual, exclude = None, active_rate = 1):
        skill_list = []
        ori_deal_time = deal_time
        ori_active_rate = active_rate
        count_add = 0

        for lv, items in self.skill_enchant.items():
            #if self.owner.classTypeNeo is True and lv == '50':
            #    continue

            if self.owner.classTypeNeo is False and lv in ['95', '100']:
                continue

            if exclude is not None and int(lv) in exclude:
                continue

            for skill_items in items['actives']:
                act = skill_items[0]

                name = act['name']
                dam = act['dam']
                cooltime = act.get('cooltime')
                factor = act.get('factor')
                longterm = act.get('longterm')
                oriname = act.get('oriname')
                
                if oriname is None or oriname == '':
                    skname = name
                    imgname = None
                else:
                    if oriname.find('$') >= 0:
                        _oriname = oriname.split('$')
                        skname = _oriname[0]
                        imgname = _oriname[1]
                    else:
                        skname = oriname
                        imgname = None

                if factor is not None and factor != '':
                    factor = int(factor)
                else:
                    factor = 0
                    cooltime = 0

                if longterm is not None and longterm != '':
                    longterm = int(longterm)    
                else:
                    longterm = 0

                if self.owner.jobname == '眞 스트리트파이터' and self.owner.classname == '격투가(여)':
                    penchant = int(act['penchant'])
                    penchant *= (self.owner.char_stat['버프'][2]/100)

                    poison = int(act['poison']) + penchant

                    if longterm == 0:
                        factor += poison
                    else:
                        longterm += poison

                fdeal = dam * factor
                ldeal = dam * longterm

                coolFixed = act.get('coolFixed')

                if coolFixed == False and cooldown is not None:
                    cooltime *= (1 - cooldown/100)

                if skname == '트윙클 스매쉬' and self.inner_data.get('홈런 퀸') is not None:
                    count_add = math.ceil(ori_deal_time / cooltime) + 1
                elif skname == '악귀참수' and self.inner_data.get('천쇄참수') is not None:
                    count_add = math.ceil(ori_deal_time / cooltime) + 1
                elif (skname == '엘레멘탈 필드' or skname == '폭풍의 숨결') and self.inner_data.get('고정쿨감') is not None:
                    cooltime -= self.inner_data['고정쿨감']
                elif skname == 'FSC-7' and self.inner_data.get('라이트웨이트') is not None:
                    count_add = 1
                elif skname in ['플레게의 정수', '성화']:
                    cooltime *= 0.85

                try:
                    skill_data = {'이름':skname,
                              'skimage': imgname,
                              '레벨':act['final_level'], 
                              '레벨링':act['plus_level'],
                              '데미지증가':round(dam, 2),
                              '쿨타임':round(cooltime, 1),
                              '원계수':round(factor),
                              '스킬계수':round(fdeal),
                              '지속계수':round(ldeal),
                              'requiredLevel': int(lv),
                              'invest': act['invest'],
                              'coolfixed':coolFixed
                              }
                    if act.get('cool') is not None:
                        skill_data['쿨타임 증감'] = round(act['cool'], 4)
                except:
                    print(skname)
                    raise
                        
                skill_list.append(skill_data)

        skill_list.sort(key=(lambda x: len(x['invest'])), reverse=True)

        act_cool_mean = self.inner_data['평균쿨감'] 

        point_skill = 3
        for act in skill_list:
            deal_time = ori_deal_time
            active_rate = ori_active_rate

            name = act['이름']
            cooltime = act['쿨타임']
            factor = act['스킬계수']
            longterm = act['지속계수']
            lv = act['requiredLevel']

            if cooltime != 0:
                if self.owner.classname == '크리에이터':
                    if name in ['빙하시대', '링크', '아이스 스톤', '플레임 허리케인', '윈드 스톰', '윈드 프레스', '운석 낙하', '파이어 월']:
                        cooltime /= 2
                        if name != '플레임 허리케인':
                            factor /= 2

                if deal_time <= 30:
                    if self.owner.jobname in ['眞 메카닉', '眞 소울브링어', '眞 스핏파이어', '眞 카오스'] or self.owner.classname in ['크리에이터']:
                        time = deal_time

                    elif self.owner.jobname not in ['眞 엘븐나이트', '眞 그래플러', '眞 아수라', '眞 버서커',  '眞 마도학자', '眞 인파이터', '眞 퇴마사', '眞 어벤저', '眞 빙결사', '眞 팔라딘', '眞 드래곤나이트', '眞 뱅가드', '眞 드래고니안 랜서', '眞 듀얼리스트', '眞 스트라이커', '眞 엘레멘탈마스터', '眞 요원']:
                        if lv >= 80:
                            time = deal_time
                        elif 30 < lv <= 75:
                            time = deal_time * 0.95
                        else:
                            time = deal_time * 0.85
                    else:
                        if lv <= 35:
                            time = deal_time * 0.95
                        else:
                            time = deal_time
                else:
                    if self.owner.jobname in ['眞 메카닉', '眞 소울브링어', '眞 스핏파이어', '眞 카오스'] or self.owner.classname in ['크리에이터']:
                        time = deal_time

                    elif self.owner.jobname not in ['眞 엘븐나이트', '眞 그래플러', '眞 아수라', '眞 버서커',  '眞 마도학자', '眞 인파이터', '眞 퇴마사', '眞 어벤저', '眞 빙결사', '眞 팔라딘', '眞 드래곤나이트', '眞 뱅가드', '眞 드래고니안 랜서', '眞 듀얼리스트', '眞 스트라이커', '眞 엘레멘탈마스터', '眞 요원']:

                        if lv >= 80:
                            time = deal_time
                        elif 30 < lv <= 75:
                            time = deal_time * 0.9
                        else:
                            time = deal_time * 0.8
                    else:
                        if lv <= 35:
                            time = deal_time * 0.9
                        else:
                            time = deal_time

                if act_cool_mean < 0.8 and lv <= 75:
                    if 30 <= lv <= 45:
                        coolf = 4
                    elif lv < 30:
                        coolf = 3
                    else:
                        coolf = 4.5

                    diff = 1 - act_cool_mean
                    diff /= coolf
                    coolcut = 1 - diff

                    time = time * coolcut

                if lv not in [50, 85, 100] and point_skill != 0:
                    if point_skill == 3:
                        tmargin = 0.1
                    else:
                        tmargin = 0.5

                    #if deal_time == 25 and cooldown != 20:
                    #    print(deal_time, time, math.ceil(deal_time / cooltime), math.ceil(time / cooltime),cooltime, name)
 
                    if math.ceil((deal_time - tmargin) / cooltime) != math.ceil(time / cooltime):
                        #print(deal_time, time, math.ceil((deal_time - tmargin) / cooltime), math.ceil(time / cooltime),cooltime, name)
                        time = deal_time - tmargin
                        point_skill -= 1

                if self.owner.jobname == '眞 검귀' and name == '귀신보':
                    cooltime -= self.inner_data['악귀현신']
                
                deal_count = math.ceil(time / cooltime)

                if active_rate != 1 and deal_count > 2:
                    _ar = 1 - active_rate
                    _ar *= (math.ceil((deal_count - 1)/5))

                    active_rate = 1 - _ar

                    time *= active_rate

                    deal_count = math.ceil(time / cooltime)

                #print(name, deal_count)
            else:
                deal_count = 0
                time = deal_time * 0.95 * active_rate 
                
            time = math.ceil(time*10) / 10

            #print(name, time)
            if self.owner.jobname == '眞 런처' and self.owner.classname == '거너(여)':
                if name == 'FSC-7':
                    deal_count += count_add

            elif self.owner.jobname == '眞 검귀':
                if name == '귀신보':
                    deal_count += count_add

            elif self.owner.jobname == '眞 배틀메이지':
                if name == '쇄패':
                    deal_count += count_add

            elif self.owner.jobname == '眞 스트리트파이터' and self.owner.classname == '격투가(남)':
                if name == '바늘 투척':
                    deal_count += (3 * math.ceil(deal_time/35))
            
            elif self.owner.jobname == '眞 스핏파이어': #and self.owner.classname == '거너(남)':
                if name.find('류탄') >= 0:
                    deal_count = min(5 * math.ceil(deal_time/35), deal_count)

            elif self.owner.jobname == '眞 웨펀마스터':

                plimit = self.owner.char_stat['패시브']['극한의 경지']['데미지증가']

                if name.find('류심') >= 0: 
                    deal_count = min(4 * math.ceil(deal_time/35), deal_count)
                    #factor /= (1 + plimit/100)
                    factor *= 1.1111
                elif name == '발도':
                    deal_count = min(3 * math.ceil(deal_time/26), deal_count)
                #elif name == '환영검무':
                #    deal_count = min(1 * math.ceil(deal_time/26), deal_count)

                if name in ['환영검무', '극 귀검술 : 유성락', '극 귀검술 : 심검', '맹룡단공참', '차지 크래시']:
                    factor /= (1 + plimit/100)

            elif self.owner.classname == '다크나이트':
                s_tal_list = self.owner.char_stat['탈리스만스킬']
                talSel = self.owner.char_stat.get('탈선착용')

                if name == '일루젼 슬래쉬':
                    deal_count = math.floor(deal_time/11)
                    factor *= 2
                elif name in ['다크 웨이브 폴', '차지 익스플로전', '다크 버스트', '다크 플레임 소드']:
                    if talSel is not None:
                        if name in s_tal_list[:-1]:
                            if (s_tal_list.index(name)) == 0:
                                _cooltime = cooltime * 0.3
                            else:
                                _cooltime = cooltime * 0.4
                            deal_count = math.ceil(time/_cooltime)
                    else:
                         if name in s_tal_list:
                            deal_count = math.ceil(deal_time/11)
                    factor *= 2
                elif name in ['웨이브 스핀', '다크 소드', '다크 레이브']:
                    factor *= 2
                elif name in ['다크 브레이크', '디아볼릭 슬래쉬']:
                    deal_count = math.floor(deal_time/22)
                    factor *= 2
                elif lv in [85, 100]:
                    factor *= 2
                """
            elif self.owner.jobname == '眞 쿠노이치':
                if name in ['야마타오로치', '마환 풍마수리검', '아마테라스', '비기 : 염무개화', '두꺼비유염탄' '열화천도']:
                    deal_count = min(2 * math.ceil(deal_time/35) , deal_count)
                """

            elif self.owner.jobname == '眞 메카닉' and self.owner.classname == '거너(여)':
                if name == 'G-S.P. 팔콘':
                    deal_count += 2
            elif self.owner.jobname == '眞 뱅가드':
                if name == '임팩트 스매쉬':
                    pass
                    #deal_count *= 2
            elif self.owner.jobname == '眞 소환사':
                if name == '채찍질':
                    deal_count = 3

            if def_dual is not None:
                ef_max, ef_min = def_dual

                if deal_count > 0:
                    max_count = math.ceil(deal_count / 2)
                    min_count = math.floor(deal_count / 2) 

                    if max_count == min_count:
                        max_count += 0.5
                        min_count -= 0.5

                    e_avg = (ef_max * max_count + ef_min * min_count)/deal_count

                    #print (name, ef_max, ef_min, e_avg, max_count, min_count, deal_count)

                    countf = (1 + e_avg/100)

                    timef = (1 + ((ef_max * 3 + ef_min * 2) / 5) / 100)
            else:
                countf = timef = 1

            if self.owner.jobname == '眞 소환사':
                """
                if name in ['썬더콜링(글레어린)', '화염폭검술(플레임 헐크)', '식선(라모스)', '헵타 아이스(아퀘리스)', '블랙 스웜(데드 멀커)', '식락', '필살검 천귀살']:
                    countf *= 1.15
                elif name in ['전설소환 : 월영', '포식의 델라리온']:
                    countf *= 0.957
                elif name == '초고밀도 레이저(에체베리아)':
                    countf *= 1.3
                elif name == '채찍질':
                    countf *= 0.68
                elif name == '지고의 정령왕':
                    countf *= 1.3

                if name in ['전설소환 : 갈애의 라모스', '계약소환 : 정복자 카시야스']:
                    timef *= 1.15
                elif name in ['정령소환 : 글레어린', '정령소환 : 데드 멀커', '정령소환 : 아퀘리스', '정령소환 : 플레임 헐크']:
                    timef *= 1.725
                elif name == '정령소환 : 정령왕 에체베리아':
                    timef *= 1.95
                elif name in ['계약소환 : 기갑 호도르', '계약소환 : 프리트', '계약소환 : 검은기사 산도르', '계약소환 : 루이즈 언니!', '계약소환 : 타우킹 쿠루타']:
                    timef *= 1.5
                """
                if name not in ['포식의 델라리온', '채찍질', '정령 희생']:
                    countf *= 1.045
                    timef *= 1.045

            elif self.owner.jobname == '眞 메카닉' and self.owner.classname == '거너(남)':
                if name in ['메카 드롭', 'Ez-10 카운터어택', 'TX-45 A-Team', 'RX-60 트랩러너', 'Ez-8 카운트다운', 'RX-78 랜드러너', '공중 전투 메카 : 템페스터']:
                    countf *= 1.4
                elif name == '스패로우 팩토리' and self.has_skill(self.owner.sk_dict['skill']['style']['passive'], '솔라 모듈 시스템') is False:
                    countf *= 1.4
            
            elif self.owner.jobname == '眞 메카닉' and self.owner.classname == '거너(여)':
                if name in ['Ez-8 카운트다운', 'RX-78 랜드러너', 'Ez-10 카운터 어택']:
                    countf *= 1.4
                elif name in ['트랜스폼 : G-2 롤링썬더', 'G 마그네틱']:
                    countf *= 0.76923

            deal = deal_count * factor * countf + time * longterm * timef

            if self.owner.jobname == '眞 다크템플러':
                if name.find('리버레이트') >= 0:
                    ves = self.inner_data['베스퍼스']
                    deal /= ves
 
            elif self.owner.jobname == '眞 로그':
                hitend = self.inner_data['히트엔드']
                if name == '데스 허리케인':
                    deal *= (0.92 + (0.08 * hitend/100))
                else:
                    deal *= (0.8 + (0.2 * hitend/100))
            elif self.owner.jobname == '眞 사령술사':
                if name != '니콜라스 강령':
                    deal *= 1.2

            elif self.owner.jobname == '眞 쿠노이치':
                mirage = self.inner_data['잔영']
                if name != '쿠사나기의 검':
                    deal *= (1 + mirage/100)

                if name in ['야마타오로치', '마환 풍마수리검', '아마테라스', '비기 : 염무개화', '두꺼비유염탄', '열화천도']:
                    record = min(deal_count, math.ceil((ori_deal_time - 10) / 25))
                    
                    """
                    if (ori_deal_time == 25 and cooldown == None):
                        print(name, record, deal_count, (ori_deal_time - 10) / 25)
                    """

                    deal += (deal/deal_count * 0.8) * record

            elif self.owner.jobname == '眞 넨마스터' and self.owner.classname == '격투가(남)':
                if name in ['사자후', '기공장', '기호지세', '금뇌호 : 심판의 넨수', '넨 스피어', '광호천지파', '기공환', '제황나선격']:
                    deal *= 1.6

            elif self.owner.jobname == '眞 엘븐나이트':
                chainrush, nature = self.inner_data['체인러쉬']

                if name == '체인 스트라이크':
                    deal *= (1 + (chainrush+30)/100)
                elif lv not in [50, 85, 100]:
                    deal *= (1 + chainrush/100)

            elif self.owner.jobname == '眞 스트리트파이터' and self.owner.classname == '격투가(남)':
                if name in ['니들 스핀', '천붕지괴', '더티 배럴', '광폭혈쇄']:
                    tpas = self.inner_data['천수천안']
                    ori = tpas - 14.5

                    deal /= (1 + ori/100)
                    deal *= (1 + tpas/100)
                """
            elif self.owner.jobname == '眞 스트라이커' and self.owner.classname == '격투가(남)':
                deal *= self.inner_data['화각스증']
                """
            elif self.owner.jobname == '眞 그래플러' and self.owner.classname == '격투가(여)':
                if name in ['자이언트 스윙', '싸이클론 어택', '와일드 캐넌 스파이크']:
                    deal *= 1.6
            
            elif self.owner.jobname == '眞 스핏파이어':
                if name in ['버스터 샷', '네이팜 탄', '피스톨 카빈', '교차 사격']:
                    md = self.inner_data['사격강화']
                    deal *= (1 + md/100)

                elif name in ['G-18C 빙결류탄', 'G-35L 섬광류탄', 'G-14 파열류탄']:
                    fd = self.inner_data['류탄강화']
                    deal *= (1 + fd/100)
            elif self.owner.jobname == '眞 마도학자':
                if name in ['플로레 컬라이더', '반중력 기동장치']:
                    deal *= (1 + (self.inner_data['현자의 돌'] - 5)/100)

                elif name in ['메가 드릴', '성난 불길 가열로', '용암지대 생성물약']:
                    deal *= (1 + (self.inner_data['현자의 돌'] + 68)/100)

                else:
                    deal *= (1 + self.inner_data['현자의 돌']/100)
            elif self.owner.jobname == '眞 데몬슬레이어':
                if name in ['검마격살', '혈화난무']:
                    deal /= (1 + self.inner_data['탐욕의 번제']/100)

            elif self.owner.jobname == '眞 빙결사':
                if name in ['샤드 매그넘', '핀포인트 러시', '아이스 빅 해머', '아이스 크래시', '회전투창', '크리스탈 블레이드', '설화연창']:
                    deal *= self.inner_data['얼음창']

            elif self.owner.jobname == '眞 레인저' and self.owner.classname == '거너(여)':
                if name == '소닉 스파이크':
                    deal /= self.inner_data['체인 인라이튼']
            elif self.owner.jobname == '眞 소드마스터':
                if name == '반월':
                    deal *= 1.23

                elif name == '섬광':
                    deal *= 1.073
            elif self.owner.jobname == '眞 퇴마사':
                if name not in ['무쌍격', '거선풍', '단층지격', '공참타']:
                    deal *= 1.18

            #print(deal, f, round(deal * f))

            act['최종계수'] = round(deal)
            act['적용패시브'] = pf
            act['점수기준'] = round(deal * pf * f)
            act['데미지'] = round(deal * pf * f * 1.5 * (1 - d/100))
            act['사용횟수'] = deal_count
            act['적용딜타임'] = time

        """
        if deal_time == 25 and cooldown == 20:
            for skill in skill_list:
                if skill['이름'] in ['낙뢰부', '오망성진','오행(五行):벽천지격']:
                    print(skill)
        """

        return skill_list

    def calculate_deal(self, d_info, synergy):
        char_stat = self.owner.char_stat

        add_stat = 0
        s_inc = 1
        if synergy is not None:
            for k, v in synergy.items():
                if k in ['증추', '크증추', '모공', '추댐', '힘지', '물마독공']:
                    char_stat[k] += v
                elif k == '스탯':
                    add_stat = v
                elif k == '시너지':
                    s_inc *= 1.34
                elif k == '시너지스공' and char_stat['char_type'] == '시너지':
                    s_inc *= v

        else:
            s_inc = 1.34

        #TODO: 증추 크증추 계산은 다른데서 한번만
        if char_stat.get('증추') is not None and char_stat.get('크증추') is not None:
            char_stat['증댐'] += char_stat['증추']
            char_stat['크증댐'] += char_stat['크증추']
            del char_stat['증추']
            del char_stat['크증추']

            char_stat['스공'] = round((char_stat['스공'] - 1),2) * 100

        main_stat = max([char_stat['힘'], char_stat['지능']])
        base_stat = self.owner.base_stat

        if self.inner_data.get('수문장모드') == 'dual':
            elem_list = [char_stat['화속성강화'], char_stat['명속성강화'], char_stat['수속성강화'], char_stat['암속성강화']]
            elem_list.sort()

            elem_max = sum(elem_list[2:]) / 2
            elem_min = sum(elem_list[:2]) / 2

            elem_max_inc = (1 + (elem_max + 11 - (d_info['몹속저'] - d_info['버퍼속저깍'])) * 0.0045)
            elem_min_inc = (1 + (elem_min + 11 - (d_info['몹속저'] - d_info['버퍼속저깍'])) * 0.0045)

            #print (elem_max, elem_min)

            ef_max = (elem_max_inc - 1) * 100
            ef_min = (elem_min_inc - 1) * 100

            ef = 0
            char_stat['듀얼수문장'] = (ef_max, ef_min)
            char_stat['속강딜증가'] = ef_max + ef_min / 2
            char_stat['적용속강'] = (elem_max_inc + elem_min_inc) / 2
        else:
            elem_cur = max([char_stat['화속성강화'], char_stat['명속성강화'], char_stat['수속성강화'], char_stat['암속성강화']])
            elem_inc = (1 + (elem_cur + 11 - (d_info['몹속저'] - d_info['버퍼속저깍'])) * 0.0045)
            ef = char_stat['속강딜증가'] = (elem_inc - 1) * 100
            char_stat['적용속강'] =  elem_cur

        if self.owner.classTypeNeo is False:
            if self.owner.bonus_disable is False:
                type_inc = d_info['비진각보정']
            else:
                type_inc = 1
        else:
            type_inc = 1

        #print('type_inc', type_inc)

        char_dam_type = self.owner.inner_data.get('dam_type')
        char_dam = char_stat[char_dam_type]

        if char_dam > 5000:
            #API 오류 방지
            char_dam = 0

        if self.owner.buffer is None:
            buff_dam = d_info['축공격력']
        else:
            buff_dam = 0
        
        self.inner_data['적용공격력'] = char_dam + buff_dam

        sf = self.inner_data['적용공격력'] * type_inc * (1 + char_stat['스공']/100)
        sf *= (1 + char_stat['증댐']/100) * (1 + char_stat['크증댐']/100)
        sf *= (1 + char_stat['추댐']/100) * (1 + char_stat['모공']/100)
        sf *= (1 + char_stat['물마독공']/100) * (1 + char_stat['지속댐']/100)
        #sf *= (1 + char_stat['패시브딜증가']/100)
        sf *= (1 + ef/100)
        if d_info.get('지역버프') is not None:
            self.inner_data['지역버프'] = int((main_stat - base_stat) * d_info['지역버프']['factor'] + d_info['지역버프']['inc'])
        d_result = char_stat[d_info['name']+'분석결과'] = {}
        for key, val in d_info['공격유형'].items():
            f = sf
            d_result[key] = {}

            dstat = 0
            for typ in val['반영스탯']:
                dstat += d_info[typ]

            d_result[key]['캐릭터공격력'] = char_dam
            d_result[key]['버프공격력'] = buff_dam
            d_result[key]['적용공격력'] = char_dam + buff_dam
            d_result[key]['지역버프스탯'] = self.inner_data['지역버프']
            d_result[key]['버퍼버프스탯'] = dstat

            if self.owner.buffer is None:
                d_result[key]['적용스탯'] = dstat + self.inner_data['지역버프'] + main_stat + add_stat
            else:
                d_result[key]['적용스탯'] = main_stat + self.inner_data['지역버프']
            
            f *= (1 + ((1 + char_stat['힘지']/100) * d_result[key]['적용스탯']/250)) * s_inc

            if self.inventory.inner_data.get('정령왕') is True:
                pinc = val['정령왕']
            else:
                pinc = 1

            damp = val.get('투함포')
            if damp is not None:
                pinc += (damp - 1)

            f *= pinc

            addf = val.get('추가딜증')
            if addf is not None:
                f *= addf

            if self.owner.jobname == '眞 스트리트파이터' and self.owner.classname == '격투가(여)':
                pf = self.inner_data['패시브총합']
            else:
                f *= (1 + char_stat['버프'][2]/100)
                pf = self.inner_data['패시브총합']

            cooldown = val.get('쿨감')

            d_result[key]['스킬'] = self.calculate_skills(val['시간'], cooldown, pf,  f, val['방어력'], char_stat.get('듀얼수문장'), exclude = val['제외스킬'], active_rate = val['가동률'])
            d_result[key]['스킬'].sort(key=(lambda x: x['최종계수']), reverse=True)

            total_deal = sum(sd['데미지'] for sd in d_result[key]['스킬'])
            total_factor = sum(sd['점수기준'] for sd in d_result[key]['스킬'])

            awkd = 0
            if self.owner.classTypeNeo is True:
                if self.owner.classname == '다크나이트' or self.owner.classname == '크리에이터':
                    for sd in d_result[key]['스킬']:
                        if sd['requiredLevel'] == 85 and sd['사용횟수'] > 0:
                            total_deal -= sd['데미지']
                            total_factor -= sd['점수기준']
                        elif sd['requiredLevel'] == 100 and sd['사용횟수'] > 0:
                            awkd += sd['데미지']
                else:
                    for sd in d_result[key]['스킬']:
                        if sd['requiredLevel'] == 50 and sd['사용횟수'] > 0:
                            total_deal -= sd['데미지']
                            total_factor -= sd['점수기준']
                        elif sd['requiredLevel'] in [85, 100] and sd['사용횟수'] > 0 and sd['coolfixed'] is False:
                            awkd += sd['데미지']
 
            #print(total_factor)
            d_result[key]['기준점수'] = round(total_factor / 100000000000)
            d_result[key]['기준딜'] = round(total_deal)

        for key, val in d_info['공격유형'].items():
            _formula = val['계산식']

            formula = _formula.split('+')

            score = 0
            deal = 0
            for _f in formula:
                f = _f.split('*')
                if f[0] == _f:
                    score += d_result[f[0]]['기준점수']
                else:
                    score += d_result[f[0]]['기준점수'] * float(f[1])

                deal += d_result[f[0]]['기준딜']

            d_result[key]['점수'] = score
            d_result[key]['총합딜'] = deal

        score_list = {}
        total_score = 0
        for key, val in d_info['공격유형'].items():
            ratio = val['반영률']

            total_score += (d_result[key]['총합딜'] * ratio)
            score_list[key] = round(d_result[key]['총합딜'])

        #score_list['총점'] = round(total_score)

        d_result['점수표'] = {'scores': score_list}

        if self.owner.isBuffer is False and d_info['name'] == '시로코':
            vsum = 0

            d = {}
            d2 = {}

            for k, v in score_list.items():
                if k == '지속딜':
                    vsum += (v / 10000000000000 / 40)
                    #d[k] = v / 4000000000000
                    #d2[k] = (v - awkd) / 4000000000000
                    std = d[k] = v / 4000000000000
                    std2 = d2[k] = (v - awkd) / 4000000000000
                elif k == '지속정자극딜':
                    vsum += (v / 10000000000000 / 48)
                elif k == '그로기딜':
                    vsum += (v / 10000000000000 / 25)
                    d[k] = v / 2500000000000
                    d2[k] = (v - awkd) / 2500000000000
                elif k == '정자극딜':
                    vsum += (v / 10000000000000 / 30)
                elif k == '80초딜':
                    d[k] = v / 8000000000000
                    d2[k] = (v - awkd) / 8000000000000
                elif k == '60초딜':
                    d[k] = v / 6000000000000
                    d2[k] = (v - awkd) / 6000000000000

            if char_stat['char_type'] == '시너지':
                vsum *= 1.0816

            namep = char_stat.get('모험가명성')
            if namep is not None:
                char_stat['points'] = (namep-6068)/15

            char_stat['points'] += vsum * 500
            
            d3 = {}
            for k, v in d.items():
                d3[k] = d[k]/d2[k]

            for k, v in d.items():
                d[k] /= std
                d2[k] /= std2
 
            #print(d)
            #print(d2)
            #print(d3)
            m1 = mean(d2.values())
            m2 = mean(d3.values())
            #print(m1)
            #print(m2)
            m3 = m2 - m1

            if m3 < 0:
                m3 = 0
            elif m3 > 1:
                m3 = 1
            #print(m3)

            char_stat['딜밸런스'] = m3

            del d_result['80초딜']
            del d_result['60초딜']

    def calculate_buff(self):
        buff_type = self.buffoption['type']
        buff_name = self.buffoption['name']
        buff_base = self.buffoption['base']
        main_stat_type = self.inventory.main_stat['type']

        #print (buff_type, buff_name, 'buffoption', self.buffoption)

        d_result = self.owner.char_stat['버프분석결과']
        if buff_type == '아포':
            si = self.get_skill('skills', buff_name, req = 50)

            apod = data = si[0]
            lv = si[1] + si[2]
            alv = lv

            v = data['values'][lv]
            v += self.buffoption['계수']
            v *= self.buffoption['힘지']

            s = self.owner.char_stat[main_stat_type]

            #print ('마을힘', s, '추정치', self.inventory.main_stat['value'], '아포레벨', lv, si[2])

            s = self.inventory.main_stat['value']

            res = v * (1 + s/buff_base)

            #d_result[buff_type].append((50, buff_name, math.ceil(v), s, res))

            sl = self.get_skills_by_level('skills', 100)
            si = sl[0]

            data = si[0]
            lv = si[1] + si[2]
            name = data['name']

            res1 = round(res * (1 + (lv + 23)/100))
            res2 = round(res * (1 + (lv + 9)/100))

            d_result[buff_type] = {'name':name, '계수':math.ceil(v), '적용스탯':{'type':main_stat_type, 'value':s}, 'value':res1, 'level':alv, 'level100':lv, 'value2':res2, 'factors': apod['values'], 'buffopts':self.buffoption}
        else:
            d_result[buff_type] = {}
            sl = self._get_skill_instance_all('skills', buff_name, req = 30)

            for si in sl:
                data = si[0]
                lv = si[1] + si[2]

                if data['type'] == '축공격력':
                    v = data['values'][lv]
                    v *= self.buffoption['물공']

                    s = self.inventory.main_stat['value']
                    
                    res = v * (1 + s/buff_base)

                    if self.owner.classname == '프리스트(여)':
                        res *= 1.15
                    elif self.owner.classname == '마법사(여)':
                        res *= (1.15 * 1.25)

                    res = round(res)

                    d_result[buff_type]['공'] = {'name':buff_name, '계수':math.ceil(v), '적용스탯':{'type':main_stat_type, 'value':s}, 'value':res, 'level':lv, 'factors': data['values'], 'inc':self.buffoption['물공']}

                else:
                    v = data['values'][lv]
                    v *= self.buffoption['힘지']

                    s = self.inventory.main_stat['value']
                    
                    res = v * (1 + s/buff_base)
                    
                    if self.owner.classname == '프리스트(여)':
                        res *= 1.15
                    elif self.owner.classname == '마법사(여)':
                        res *= (1.15 * 1.25)

                    res = round(res)

                    d_result[buff_type]['힘지'] = {'name':buff_name, '계수':math.ceil(v), '적용스탯':{'type':main_stat_type, 'value':s}, 'value':res, 'level':lv, 'factors': data['values'], 'inc':self.buffoption['힘지'], 'buffopts':self.buffoption}

        if '보조스킬' in self.buffoption.keys():
            d_result['보조스킬'] = self.buffoption['보조스킬']                

