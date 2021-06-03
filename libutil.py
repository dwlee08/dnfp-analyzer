#!/usr/bin/python3
#-*- coding:utf-8 -*-

import os
from json import loads
import json
import urllib.request
from urllib import parse as urlparse
import time
import numpy as np
import random
from io import BytesIO
from parse import compile
import sys
import subprocess
import math
import re
import datetime
from time import sleep

from time import (
    process_time,
    perf_counter,
    sleep,
)

#item_stat_type = ["이동속도", "공격속도", "물리크리티컬히트", "마법크리티컬히트", "모든속성강화", "모든속성저항", "캐스트속도"]

class LibUtil():
    parser = [
        compile("물리공격력+{깡물공:g}("),
        compile("마법공격력+{깡마공:g}("),
        compile("독립공격력+{깡독공:g}("),
        compile("모든스탯+{깡스탯:g}("),
        compile("모든스탯+{깡스탯:g}증가("),
        compile("힘지능체력정신력{깡스탯:g}증가"),
        compile("모든직업{}Lv스킬공격력{}%증가"),
        compile("{}레벨액티브스킬공격력{}%증가"),
        compile("도적{}레벨모든스킬공격력{}%증가"),
        compile("물리크리티컬히트{물리크리티컬:g}%마법크리티컬히트{마법크리티컬:g}%증가"),
        compile("크리티컬공격시데미지{크증댐:g}%증가"),
        compile("크리티컬공격시데미지증가{}{크증추:g}%추가증가"),
        compile("크리티컬공격시데{}지{크증추:g}%추가증가"),
        compile("공격시데미지{증댐:g}%증가"),
        compile("공격시데미지증가{}{증추:g}%추가증가"),
        compile("공격시{추댐:g}%추가데미지"),
        compile("모든공격력{모공:g}%증가"),
        compile("모든직업{:d}~{:d}레벨모든스킬쿨타임{:d}%감소({}제외"),
        compile("모든직업{minLevel:d}~{maxLevel:d}레벨모든스킬쿨타임{스킬쿨감:g}%감소"),
        compile("모든직업{레벨:d}레벨모든스킬공격력{스킬증댐:g}%증가"),
        compile("모든직업{:d}~{:d}레벨모든스킬Lv+{:d}({}제외"),
        compile("모든직업{minLevel:d}~{maxLevel:d}레벨모든스킬Lv+{스킬레벨:d}"),
        compile("스킬공격력{스공:g}%{}가"),
        compile("스킬공격력+{스공:g}%"),
        compile("물리마법독립공격력{물마독공:g}%"),
        compile("물리마법독립공격력+{물마독깡:g}증가"),
        compile("물리마법독립공격력{물마독깡:g}증가"),
        compile("물리마법독립공격력증가량{물마독공:g}%"),
        compile("{속추댐:g}%속성추가데미지"),
        compile("{속추댐:g}%{속성종류}속성추가데미지"),
        compile("적에게입힌피해의{지속댐:g}%만큼{지속:g}초동안지속피해발생"),
        compile("공격시{지속:g}초동안적에게입힌피해의{지속댐:g}%만큼지속피해발생"),
        compile("피격시데미지감소{피격뎀감소:g}%"),
        compile("피격시데미지{피격뎀:g}%{증감}"),
        compile("피격데미지{피격뎀:g}%증가"),
        compile("물리마법크리티컬히트{물마크:g}증가"),
        compile("힘지능{힘지:g}%공격속도{공속:g}%증가"),
        compile("힘지능+{힘지:g}%증가"),
        compile("힘지능+{힘지깡:g}"),
        compile("힘지능{힘지깡:g}증가"),
        compile("힘지능{힘지:g}%"),
        compile("모든속도{공이캐속:g}%"),
        compile("공격속도이동속도캐스트속도{공이캐속:g}%증가"),
        compile("공격속도+{공속:g}%이동속도+{이속:g}%캐스트속도+{캐속:g}%"),
        compile("공격속도{공속:g}%이동속도{이속:g}%캐스트속도{캐속:g}%증가"),
        compile("공격속도{공속:g}%이동속도{이속:g}%캐스트속도{캐속:g}%{증감}"),
        compile("공격속도{공속:g}%이동속도{이속:g}%증가"),
        compile("공격속도{공속:g}%캐스트속도{캐속:g}%증가"),
        compile("공격속도{공속:g}%증가캐스트속도{캐속:g}%증가"),
        compile("공격속도{공속:g}%증가및캐스트속도{캐속:g}%증가"),
        compile("공격속도이동속도{공이속:g}%증가"),
        compile("공격속도{공속:g}%증가"),
        compile("공격속도+{공속:g}%"),
        compile("Y축이동속도{:g}%증가"),
        compile("이동속도{이속:g}%증가"),
        compile("이동속도+{이속:g}%"),
        
        compile("공격속도-{공속감소:g}%"),
        compile("적이동속도{:g}%감소"),
        compile("이동속도-{이속감소:g}%"),
        compile("캐스트속도{캐속:g}%증가"),
        compile("공격속도{:g}%감소"),
        compile("이동속도{:g}%감소"),
        compile("캐스트속도{캐속감소:g}%감소"),
        compile("캐스트속도+{캐속:g}%"),
        compile("캐스트속도-{캐속감소:g}%"),
        compile("물리크리티컬히트{물리크리티컬:g}%증가"),
        compile("마법크리티컬히트{마법크리티컬:g}%증가"),
        compile("모든속성강화{모속강:g}증가"),
        compile("모든속성저항{모속저:g}증가"),
        compile("모든속성저항{모속저감소:g}감소"),
        compile("모든속성저항{증감}{모속저:g}"),
        compile("힘지능증가량{힘지:g}%증가"),
        compile("{속성종류1}속성저항{속성종류2}속성저항{속성종류3}속성저항{속저감소:g}감소"),
        compile("{속성종류}속성저항{증감}{속저:g}"),
        compile("5초마다단일속성강화+{수문장}"),
        compile("{속성종류}속성강화+{속강:g}"),
        compile("마을적용옵션+{깡모속:g}")
    ]

    # 30Lv버프스킬힘지능증가량{}%증가
    # 30Lv버프스킬물리마법독립공격력증가량{}%증가
    # 30Lv버프스킬물리공격력증가량{}%증가
    # 30Lv버프스킬마법공격력증가량{}%증가
    # 30Lv버프스킬독립공격력증가량{}%증가
    # 50Lv액티브스킬힘지능증가량{}증가
    # 50Lv액티브스킬힘지능증가량{}%증가
#수호의 은총 체력, 정신력 250 증가
#계시 : 아리아, 퍼페티어 지능 173 증가

    b_parser = [
            compile("30Lv버프스킬힘지능증가량{축힘지:g}%증가"),
            compile("30Lv버프스킬물리마법독립공격력증가량{축물마독:g}%증가"),
            compile("30Lv버프스킬물리공격력증가량{축물공:g}%증가"),
            compile("30Lv버프스킬마법공격력증가량{축마공:g}%증가"),
            compile("30Lv버프스킬독립공격력증가량{축독공:g}%증가"),
            compile("50Lv액티브스킬힘지능증가량{포계수:g}증가"),
            compile("50Lv액티브스킬힘지{}{포힘지:g}%증가"),
            #compile("50Lv액티브스킬힘지능{포힘지:g}%증가"), 
            compile("수호의은총체력정신력{체력:g}증가"),
            compile("계시:아리아퍼페티어지능{지능:g}증가"),
            compile("계시:아리아지능{라핌지능:g}증가"),
            compile("퍼페티어지능{카테지능:g}증가"),
            compile("수호의은총계시:아리아퍼페티어스킬Lv+{패시브레벨:g}"), 
            compile("신념의오라체력정신력증가량{체력오라:g}증가"),
            compile("신실한열정소악마힘지능증가량{지능오라:g}증가"),
            compile("모든직업30레벨모든스킬Lv+{축레벨:g}"),
            compile("모든직업50레벨모든스킬Lv+{포레벨:g}"),
            compile("50Lv모든스킬+{포레벨:g}"),
            compile("30Lv모든스킬+{축레벨:g}"),
            compile("30Lv버프스킬레벨+{축레벨:g}"),
            compile("모든직업{min:g}~{max:g}레벨모든스킬Lv+{lv:g}({}제외"),
            compile("모든스탯+{모든스탯:g}(+")
            ]

    s_parser = {}
    s_parser['암속조건'] = [
            compile("암속성저항{v:d}당{option}(최대{max}증가)"),
            compile("암속성저항{v:d}당{option}최대{max}중첩"),
            compile("암속성저항{v:d}이상일때{option:S}")
            ]

    s_parser['개조조건'] = compile("장비개조단계가{step:d}증가할때마다{option:S}(")
    s_parser['강화조건'] = compile("강화증폭수치가{v:d}증가할때마다{option}(최대{max}까지증가)")
    s_parser['착용조건'] = [
            compile("{item}착용시"),
            compile("{item}장착시"),
            compile("{item1}과{item2}장착시")
            ]
    s_parser['주사위'] = compile("주사위눈이{v}일경우{option:S}")
    s_parser['중첩'] = compile("최대{v:d}중첩")
    s_parser['최대'] = compile("(최대{v:g}{}증가)")

    myth_db = {}
    weapon_tree = {}
    set_tree = {}
    item_tree = {}

    convert_list = {}
    
    @staticmethod
    def load_api(URL):
        apikey = 'apikey=NqzICVeo3FesBuq3Gw1CmYhiOiFdYcHr'

        #print('https://api.neople.co.kr/df/'+ URL + apikey)
        max_try = 5
        while True:
            try:
                api_load=urllib.request.urlopen('https://api.neople.co.kr/df/'+ URL + apikey)
                api_dic=loads(api_load.read().decode("utf-8"))
                break
            except:
                max_try -= 1
                if max_try == 0:
                    raise
                sleep(0.5)
                continue

        return api_dic

    @classmethod
    def parse_buff(cls, explain, io, name, skill_db, step = 0):
        #print ("#################################################")
        #print (name)
        explain = explain.replace(' ', '').replace(',','').replace('\n\n', '\n')
        e_list = explain.split('\n')

        for exp in e_list:
            #print(exp)
            if len(exp) <= 0:
                continue

            opt = {}
            for p in cls.b_parser:
                try:
                    result = p.search(exp)
                except:
                    raise
                if result is not None:
                    if step > 0:
                        if step == 10:
                            opt['per-step'] = 1
                        else:
                            opt['step'] = step

                    if len(result.fixed) > 0 and result[0] == '특성스킬':
                        min_lv = int(result['min'])
                        max_lv = int(result['max'])
                        lvup = int(result['lv'])

                        data = {'min':min_lv, 'max':max_lv, 'lvup':lvup}
                        opt['스킬구간'] = data
                        continue

                    for key in result.named.keys():
                        #print(key, result[key])
                        opt[key] = result[key]
                    
                    break

            if len(opt) >= 1:
                io.append(opt)

        """
        opt = {}
        if name == '운명을 가르는 함성 세트' and step == 3:
            data = {'min':30, 'max':50, 'lvup':2}
            opt['스킬구간'] = data
            io.append(opt)
        elif name == '운명의 주사위 세트' and step == 2:
            data = {'min':30, 'max':48, 'lvup':1}
            opt['스킬구간'] = data
            io.append(opt)
        elif name == '운명의 주사위 세트' and step == 3:
            data = {'min':30, 'max':50, 'lvup':2}
            opt['스킬구간'] = data
            io.append(opt)
        elif name == '영보 : 세상의 진리 세트' and step == 2:
            data = {'min':30, 'max':50, 'lvup':1}
            opt['스킬구간'] = data
            io.append(opt)
        elif name == '시간전쟁의 잔해 세트' and step == 2:
            data = {'min':1, 'max':30, 'lvup':1}
            opt['스킬구간'] = data
            io.append(opt)
        elif name == '전설의 대장장이 - 역작 세트' and step == 3:
            data = {'min':30, 'max':50, 'lvup':2}
            opt['스킬구간'] = data
            io.append(opt)
        elif name == '전설의 대장장이 - 역작 세트' and step == 5:
            data = {'min':30, 'max':48, 'lvup':2}
            opt['스킬구간'] = data
            io.append(opt)
            opt = {}
            opt['축힘지'] = 6
            io.append(opt)
            opt = {}
            opt['포힘지'] = 7
            io.append(opt)
            opt = {}
            opt['포계수'] = 20
            io.append(opt)
        elif name == '메마른 사막의 유산 세트' and step == 2:
            data = {'min':1, 'max':30, 'lvup':1}
            opt['스킬구간'] = data
            io.append(opt)
        elif name == '메마른 사막의 유산 세트' and step == 3:
            data = {'min':30, 'max':48, 'lvup':2}
            opt['스킬구간'] = data
            io.append(opt)
        elif name == '메마른 사막의 유산 세트' and step == 5:
            data = {'min':30, 'max':50, 'lvup':2}
            opt['스킬구간'] = data
            io.append(opt)
        elif name == '열대의 트로피카 세트' and step == 3:
            data = {'min':1, 'max':48, 'lvup':2}
            opt['스킬구간'] = data
            io.append(opt)
        elif name == 'A.D. P 슈트 세트' and step == 5:
            data = {'min':1, 'max':50, 'lvup':2}
            opt['스킬구간'] = data
            io.append(opt)
        elif name == '죽음을 자아내는 그림자 세트' and step == 5:
            data = {'min':1, 'max':48, 'lvup':2}
            opt['스킬구간'] = data
            io.append(opt)
        elif name == '천상의 무희 세트' and step == 5:
            data = {'min':1, 'max':48, 'lvup':2}
            opt['스킬구간'] = data
            io.append(opt)
        """
           
        return io;

    @classmethod
    def parse_explain(cls, explain, io, name, skill_db, step = 0, iid = None):
        if explain is None:
            return

        explain = explain.replace('힘, 지능', '힘/지능')
        explain = explain.replace('물리, 마법, 독립', '물리/마법/독립')
        explain = explain.replace('물리, 마법', '물리/마법')
        explain = explain.replace('레벨,', '레벨/')
        explain = explain.replace('\n(', '(')
        explain = explain.replace('/','').replace(',','').replace(' ','')
        explain = explain.replace('캐스팅','캐스트').replace('피격시받는','피격시')
        explain = explain.replace('크리티컬데미지','크리티컬공격시데미지')
        explain = explain.replace('불카누스의힘으로','')
        e_list = explain.split('\n')

        condition = {}
        step_fixed = False
        for exp in e_list:
            e_matched = False
            if len(exp) <= 0:
                continue

            if exp.find("해당효과는화수암명순서로순환됩니다") >= 0:
                break

            if exp.find("던전입장시파티원이2명이") >= 0:
                break
            
            if exp[0] != '-':
                if step_fixed is False:
                    condition = {}
            else:
                exp = exp[1:]

            if exp.find('주사위') >= 0:
                p = cls.s_parser['주사위']
                result = p.search(exp)
                if result is not None:
                    condition['조건'] = {'type':'주사위', 'cond':result['v']}
                    exp = result['option']

            if exp.find('암속성') >= 0:
                for p in cls.s_parser['암속조건']:
                    result = p.search(exp)
                    #print(exp, result)
                    if result is not None:
                        limit = result.named.get('max')
                        condition['조건'] = {'type':'암속저', 'per-val':result['v'], 'max':limit}
                        exp = result['option']
 

            if exp.find('최대') >= 0:
                p = cls.s_parser['중첩']
                result = p.search(exp)
                if result is not None:
                    condition['중첩'] = result['v']
                
                elif exp.find('강화증폭') >= 0:
                    p = cls.s_parser['강화조건']
                    result = p.search(exp)
                    if result is not None:
                        condition['조건'] = {'type':'강화증폭', 'per-val':result['v'], 'max':result['max']}
                else:
                    p = cls.s_parser['최대']
                    #print(exp)
                    result = p.search(exp)
                    if result is not None:
                        condition['최대'] = result['v']
                    #print(condition)

            if exp.find('착용') >= 0 or exp.find('장착'):
                if exp.find('보조무기로') < 0:
                    for p in cls.s_parser['착용조건']:
                        result = p.search(exp)
                        if result is not None:
                            required = []
                            for r in result.named:
                                required.append(result[r])

                            condition['조건'] = {'type':'착용', 'required':required}

            if exp.find('개조') >= 0:
                if exp == '[개조단계별옵션]':
                    condition['조건'] = {'type':'개조', 'per-step':1}
                    step_fixed = True
                else:
                    p = cls.s_parser['개조조건']
                    result = p.search(exp)
                    if result is not None:
                        condition['조건'] = {'type':'개조', 'per-step':result['step']}
                        exp = result['option']
            if exp == '[검은마물의정원전용옵션]':
                break
            elif exp.find('캐릭터이동속도에따라다음효과') >= 0:
                break

            opt = {}
            for p in cls.parser:
                try:
                    result = p.search(exp)
                except:
                    raise
                if result is not None:
                    for key in result.named.keys():
                        if '스킬증댐' in result.named.keys():
                            #print ('스킬증댐', name)
                            v = result['스킬증댐']
                            lvl = result['레벨']
                            opt['스킬'] = [{'job': '공통', 'jid': None},
                                            [{'minLevel':lvl, 'maxLevel':lvl,'damup':v}]
                                           ]
                            break
                        elif '스킬쿨감' in result.named.keys():
                            #print ('스킬쿨감', name)
                            minlvl = result['minLevel']
                            maxlvl = result['maxLevel']
                            v = result['스킬쿨감']
                            opt['스킬'] = [{'job': '공통', 'jid': None},
                                            [{'minLevel':minlvl, 'maxLevel':maxlvl,'cooldown':v}]
                                           ]
                            break
                        elif '스킬레벨' in result.named.keys():
                            #print ('스킬레벨', name)
                            minlvl = result['minLevel']
                            maxlvl = result['maxLevel']
                            v = result['스킬레벨']
                            opt['스킬'] = [{'job': '공통', 'jid': None},
                                            [{'minLevel':minlvl, 'maxLevel':maxlvl,'value':v}]
                                           ]
                            break

                        v = result[key]
                        if '중첩' in condition:
                            f = condition['중첩']
                            
                            #중첩 횟수가 높을시 보정
                            """
                            if f > 10:
                                df = f - 10
                                df = int(df*0.5)
                                f = df + 10
                            """
                            v *= f
                        elif '최대' in condition:
                            f = condition['최대']
                            v = f
                        
                        #e = result.named.get('e')
                        opt[key] = v
                    break;

            #아이템별 커스텀                           

            if len(opt) >= 1:
                if '조건' in condition:
                    opt['condition'] = condition['조건']

                io.append(opt)
        """
        if step == -2:
            convert = cls.convert_list.get(name)
            if convert is not None:
                io.append({'변환': { 'opts': convert['options'], 'type': convert['type']}})
        """

        if step == -2:
            if name == '데파르망' and iid is not None:
                #print (io, iid, explain)
                try:
                    io.pop(0)
                except:
                    pass

            return io

        if step == -3:
            if name == '데파르망':
                #print (io, iid, explain)
                try:
                    io.pop(1)
                except:
                    pass

        if name.find('사도 강림 플래티넘') >= 0 or name.find('위대한 의지') >= 0 or name.find('강인한 사도') >= 0 or name.find('기사의 위대한 긍지') >= 0:
            p = compile("{}[{lv:d}Lv]")
            result = p.parse(name)
            if result is not None:
                lv = result['lv']
                io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':lv, 'maxLevel':lv, 'damup':10},
                        ]
                      )})
        
        elif step == 0 and name == '퍼펙트 컨트롤':
            """
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':1, 'maxLevel':85, 'value':1},
                            {'minLevel':100, 'maxLevel':100, 'value':1},
                        ]
                      )})
            """
            pass
        elif step == 4 and name == '선지자의 목걸이':
            for opts in io:
                if '속추댐' in opts:
                    opts['속추댐'] *= 0.35
                elif '스공' in opts:
                    if opts['스공'] == 10:
                        opts['스공'] = 10 * 0.35 + 15 * 0.3
                    else:
                        #opts['스공'] *= 0.3
                        del opts['스공']

        elif step == 1 and name == '청면수라의 가면':
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':1, 'maxLevel':85, 'value':2},
                            {'minLevel':100, 'maxLevel':100, 'value':2},
                        ]
                      )})
        elif step == 1 and name == '무념의 의복':
            io.append({'스킬':({'job':'공통','jid':None},
                        [
                            {'minLevel':50, 'maxLevel':50, 'value':2},
                            {'minLevel':85, 'maxLevel':85, 'value':2},
                            {'minLevel':100, 'maxLevel':100, 'value':2},
                        ]
                      )})
        elif step == 1 and name == '무형의 절개':
            io.append({'스킬':({'job':'공통','jid':None},
                        [
                            {'minLevel':50, 'maxLevel':85, 'value':1},
                            {'minLevel':100, 'maxLevel':100, 'value':1},
                        ]
                      )})
        elif step == 1 and name == '무의식의 꽃':
            io.append({'스킬':({'job':'공통','jid':None},
                        [
                            {'minLevel':50, 'maxLevel':50, 'damup':30},
                            {'minLevel':85, 'maxLevel':85, 'damup':25},
                            {'minLevel':100, 'maxLevel':100, 'damup':16},
                        ]
                      )})

        elif (name == '태극천제검'):
            for opts in io:
                if '모공' in opts:
                    opts['모공'] *= 0
                """
                elif '스공' in opts:
                    if opts['스공'] != 30:
                        opts['스공'] *= 1
                elif '공속' in opts:
                    if '증감' in opts:
                        opts['공속'] *= 1
                        opts['이속'] *= 1
                        opts['캐속'] *= 1
                    else:
                        opts['공속'] *= 0
                        opts['이속'] *= 0
                        opts['캐속'] *= 0
                """
        elif (name == '천장군 : 전승의 빛'):
            io.append({'모공':18})

        elif (name == '푸른 생명의 이면'):
            for opts in io:
                if '모공' in opts:
                    opts['모공'] -= 3 #60초쿨 20초 지속 옵션 고려
                elif '모속저' in opts:
                    opts['모속저'] = int(opts['모속저'] * 0.66)
                elif '캐속' in opts:
                    opts['캐속'] *= 0.4
        elif (name == '프로젝트 : 오버코어'):
            io.append({'스킬':({'job':'총검사','jid':cls.get_jobid('총검사', skill_db)},
                        [{'skillId':cls.get_skillid('총검사', '코어 블레이드 마스터리', skill_db),
                          'name':'코어 블레이드 마스터리',
                          'damup':100,
                          'extra':'마법 공격력'
                        }]
                      )})
        elif (name == '핏빛 무도회'):
            io.append({'스킬':({'job':'도적','jid':cls.get_jobid('도적', skill_db)},
                        [
                         {'skillId':cls.get_skillid('도적', '히트엔드', skill_db),
                          'name':'히트엔드',
                          'value':'연계 점수당 공격력 비율'
                        }]
                      )})
        elif (name == '화려한 눈속임'):
            io.append({'스킬':({'job':'도적','jid':cls.get_jobid('도적', skill_db)},
                        [
                            {'minLevel':40, 'maxLevel':40, 'damup':32},
                            {'minLevel':45, 'maxLevel':45, 'damup':32},
                            {'minLevel':70, 'maxLevel':70, 'damup':32},
                            {'skillId':cls.get_skillid('도적', '인법 : 허물 벗기', skill_db),
                             'name':'인법 : 허물 벗기',
                             'cooldown':32,
                             'damdown':32,
                            },
                            {'skillId':cls.get_skillid('도적', '샤이닝컷', skill_db),
                             'name':'샤이닝컷',
                             'cooldown':32,
                             'damdown':32,
                            },
                            {'skillId':cls.get_skillid('도적', '브레이킹 러시', skill_db),
                             'name':'브레이킹 러시',
                             'cooldown':32,
                            },
                            {'skillId':cls.get_skillid('도적', '사이드 스텝', skill_db),
                             'name':'사이드 스텝',
                             'cooldown':32,
                            },
                        ]
                      )})

        elif (name == '도화선'):
            io.append({'스킬':({'job':'도적','jid':cls.get_jobid('도적', skill_db)},
                        [{'skillId':cls.get_skillid('도적', '흉멸인법진', skill_db),
                          'name':'흉멸인법진',
                          'value':2
                        }]
                      )})
        elif (name == '라스트 인파이팅'):
            io.append({'스킬':({'job':'프리스트(남)', 'jid':cls.get_jobid('프리스트(남)', skill_db)},
                        [{'skillId':cls.get_skillid('프리스트(남)', '드라이아웃', skill_db),
                          'name':'드라이아웃',
                          'cooldown':30
                        }]
                      )})
        elif (name == '레볼루션 차지'):
            io.append({'스킬':({'job':'거너(남)', 'jid':cls.get_jobid('거너(남)', skill_db)},
                        [{'skillId':cls.get_skillid('거너(남)', '레이저 라이플', skill_db),
                          'name':'레이저 라이플',
                          'cooldown':30,
                          'damup':20,
                        }]
                      )})
            io.append({'스킬':({'job':'거너(여)', 'jid':cls.get_jobid('거너(여)', skill_db)},
                        [{'skillId':cls.get_skillid('거너(여)', '레이저 라이플', skill_db),
                          'name':'레이저 라이플',
                          'cooldown':30,
                          'damup':20,
                        }]
                      )})
            """
        elif (name == '루나 베네딕티오'):
            io.append({'스킬':({'job':'마법사(남)','jid':cls.get_jobid('마법사(남)', skill_db)},
                        [
                            {'minLevel':50, 'maxLevel':50, 'value':2},
                            {'minLevel':85, 'maxLevel':85, 'value':2},
                            {'minLevel':100, 'maxLevel':100, 'value':2},
                        ]
                      )})
            io.append({'스킬':({'job':'마법사(여)','jid':cls.get_jobid('마법사(여)', skill_db)},
                        [
                            {'minLevel':50, 'maxLevel':50, 'value':2},
                            {'minLevel':85, 'maxLevel':85, 'value':2},
                            {'minLevel':100, 'maxLevel':100, 'value':2},
                        ]
                      )})
            """
        elif (name == '메가쇼크 런처'):
            io.append({'스킬':({'job':'거너(남)', 'jid':cls.get_jobid('거너(남)', skill_db)},
                        [{'skillId':cls.get_skillid('거너(남)', '솔라 모듈 시스템', skill_db),
                          'name':'솔라 모듈 시스템',
                          'damup':20,
                        }]
                      )})
            io.append({'스킬':({'job':'거너(여)', 'jid':cls.get_jobid('거너(여)', skill_db)},
                        [{'skillId':cls.get_skillid('거너(여)', '솔라 모듈 시스템', skill_db),
                          'name':'솔라 모듈 시스템',
                          'damup':20,
                        }]
                      )})
        elif (name == '백호의 울음소리'):
            io.append({'스킬':({'job':'격투가(남)', 'jid':cls.get_jobid('격투가(남)', skill_db)},
                        [{'skillId':cls.get_skillid('격투가(남)', '사자후', skill_db),
                          'name':'사자후',
                          'cooldown':30,
                          'damup':20,
                        }]
                      )})
            io.append({'스킬':({'job':'격투가(여)', 'jid':cls.get_jobid('격투가(여)', skill_db)},
                        [{'skillId':cls.get_skillid('격투가(여)', '사자후', skill_db),
                          'name':'사자후',
                          'cooldown':30,
                          'damup':20,
                        }]
                      )})
        elif (name == '불카누스의 두번째 흔적'):
            io.append({'스킬':({'job':'프리스트(남)', 'jid':cls.get_jobid('프리스트(남)', skill_db)},
                        [{'skillId':cls.get_skillid('프리스트(남)', '무쌍격', skill_db),
                          'name':'무쌍격',
                          'damup':40,
                        }]
                      )})
            io.append({'스킬':({'job':'프리스트(여)', 'jid':cls.get_jobid('프리스트(여)', skill_db)},
                        [{'skillId':cls.get_skillid('프리스트(여)', '참수', skill_db),
                          'name':'참수',
                          'damup':40,
                        }]
                      )})
        elif (name == '블러드 샷 부스터'):
            io.append({'스킬':({'job':'거너(여)', 'jid':cls.get_jobid('거너(여)', skill_db)},
                        [{'skillId':cls.get_skillid('거너(여)', '베일드 컷', skill_db),
                          'name':'베일드 컷',
                          'damup':50,
                          'extra':'출혈'
                        }]
                      )})
        elif (name == '사암주극'):
            io.append({'스킬':({'job':'마창사', 'jid':cls.get_jobid('마창사', skill_db)},
                        [
                            {'minLevel':1, 'maxLevel':48, 'value':2, 'cooldown':20},
                            {'minLevel':60, 'maxLevel':80, 'value':2, 'cooldown':20},
                            {'minLevel':90, 'maxLevel':95, 'cooldown':20},
                            {'skillId':cls.get_skillid('마창사', '임팩트 스매쉬', skill_db),
                             'name':'임팩트 스매쉬',
                             'cooldown':15,
                             'extra':'스택'}
                        ]
                      )})
        elif (name == '사일런트 베놈'):
            io.append({'스킬':({'job':'마창사', 'jid':cls.get_jobid('마창사', skill_db)},
                        [
                            {'skillId':cls.get_skillid('마창사', '멸광천투', skill_db),
                             'name':'멸광천투',
                             'damup':11.4,
                             'extra':'폭발'
                            }
                        ]
                      )})
        elif (name == '기가 드릴러'):
            io.append({'스킬':({'job':'마창사', 'jid':cls.get_jobid('마창사', skill_db)},
                        [
                            {'skillId':cls.get_skillid('마창사', '스파이럴 러쉬', skill_db),
                             'name':'스파이럴 러쉬',
                             'damup':31.5,
                             'extra':'다단히트'
                            },
                            {'skillId':cls.get_skillid('마창사', '흑광폭살', skill_db),
                             'name':'흑광폭살',
                             'damup':14.4,
                             'extra':'꿰뚫는'
                            },
                            {'skillId':cls.get_skillid('마창사', '광폭 : 흑화연창', skill_db),
                             'name':'광폭 : 흑화연창',
                             'damup':13.5,
                             'extra':'어둠의 창'
                            }
                        ]
                      )})
        elif (name == '끊임없는 환영'):
            io.append({'스킬':({'job':'마창사', 'jid':cls.get_jobid('마창사', skill_db)},
                        [
                            {'skillId':cls.get_skillid('마창사', '미라지 스탠스', skill_db),
                             'name':'미라지 스탠스',
                             'cooldown':50,
                            }
                        ]
                      )})
        elif (name == '세계수의 뿌리'):
            io.append({'스킬':({'job':'마법사(남)','jid':cls.get_jobid('마법사(남)', skill_db)},
                        [
                            {'minLevel':1, 'maxLevel':100, 'cooldown':10},
                        ]
                      )})
            io.append({'스킬':({'job':'마법사(여)','jid':cls.get_jobid('마법사(여)', skill_db)},
                        [
                            {'minLevel':1, 'maxLevel':100, 'cooldown':10},
                        ]
                      )})
            io.append({'스킬':({'job':'크리에이터','jid':cls.get_jobid('크리에이터', skill_db)},
                        [
                            {'minLevel':1, 'maxLevel':100, 'cooldown':10},
                        ]
                      )})
            """
        elif (name == '야천도'):
            io.append({'스킬':({'job':'총검사','jid':cls.get_jobid('총검사', skill_db)},
                        [
                            {'minLevel':50, 'maxLevel':50, 'value':2, 'extra':'히트맨'},
                            {'minLevel':85, 'maxLevel':85, 'value':2, 'extra':'히트맨'},
                            {'minLevel':100, 'maxLevel':100, 'value':2, 'extra':'히트맨'},
                        ]
                      )})
            """
        elif (name == '어나이얼레이터'):
            io.append({'스킬':({'job':'마법사(여)', 'jid':cls.get_jobid('마법사(여)', skill_db)},
                        [
                            {'skillId':cls.get_skillid('마법사(여)', '쇄패', skill_db),
                             'name':'쇄패',
                             'damup':50,
                            }
                        ]
                      )})
            io.append({'스킬':({'job':'마법사(남)', 'jid':cls.get_jobid('마법사(남)', skill_db)},
                        [
                            {'skillId':cls.get_skillid('마법사(남)', '팽', skill_db),
                             'name':'팽',
                             'damup':50,
                            }
                        ]
                      )})
        elif (name == '윤회의 고리 : 환룡'):
            io.append({'스킬':({'job':'프리스트(남)', 'jid':cls.get_jobid('프리스트(남)', skill_db)},
                        [

                            {'minLevel':1, 'maxLevel':100, 'cooldown':10},
                            {'minLevel':48, 'maxLevel':80, 'value':1},
                        ]
                      )})
            io.append({'스킬':({'job':'프리스트(여)', 'jid':cls.get_jobid('프리스트(여)', skill_db)},
                        [
                            {'minLevel':1, 'maxLevel':100, 'cooldown':10},
                            {'minLevel':48, 'maxLevel':80, 'value':1},
                        ]
                      )})
        elif (name == '카심의 대검'):
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':1, 'maxLevel':48, 'cooldown':20},
                            {'minLevel':60, 'maxLevel':80, 'cooldown':20},
                            {'minLevel':90, 'maxLevel':95, 'cooldown':20},
                        ]
                      )})
            """
        elif (name == '통곡의 수문장'):
            io.append({'스킬':({'job':'마창사','jid':cls.get_jobid('마창사', skill_db)},
                        [
                            {'minLevel':50, 'maxLevel':50, 'value':2, 'extra':'워로드'},
                            {'minLevel':85, 'maxLevel':85, 'value':2, 'extra':'워로드'},
                            {'minLevel':100, 'maxLevel':100, 'value':2, 'extra':'워로드'},
                        ]
                      )})
        elif (name == '대 마법사 [???]의 로브'):
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':1, 'maxLevel':45, 'value':1},
                        ]
                      )})
        elif (name == '마법사 [???]의 로브'):
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':1, 'maxLevel':45, 'value':1},
                        ]
                      )})
            """
        elif step == 3 and name == '개악 : 지옥의 길 세트':
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':1, 'maxLevel':85, 'value':1},
                            {'minLevel':100, 'maxLevel':100, 'value':1},
                        ]
                      )})
        elif step == 5 and name == '열대의 트로피카 세트':
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':1, 'maxLevel':100, 'cooldown':15},
                        ]
                      )})
            io.append({'공속':5, 'condition':{'type':'착용', 'required':['트로피카:리치']}})
            io.append({'공속':5, 'condition':{'type':'착용', 'required':['트로피카:드레이크']}})


        elif step == 5 and name == '잊혀진 마법사의 유산 세트':
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':1, 'maxLevel':85, 'value':2},
                            {'minLevel':100, 'maxLevel':100, 'value':2},
                        ]
                      )})
        elif step == 5 and name == 'A.D. P 슈트 세트':
            for opts in io:
                if '스공' in opts:
                    #opts['스공'] *= 0.5
                    pass

                elif '공속' in opts:
                    opts['공속'] *= 0.5
                    opts['이속'] *= 0.5
                    opts['캐속'] *= 0.5
            """
            elif name == '낭만적인 선율의 왈츠' or name == '우아한 선율의 왈츠':
                io.append({'스킬':({'job':'공통', 'jid':None},
                            [
                                {'minLevel':1, 'maxLevel':45, 'cooldown':10},
                            ]
                          )})
            elif name == '격렬한 스텝의 자이브':
                io.append({'스킬':({'job':'공통', 'jid':None},
                            [
                                {'minLevel':1, 'maxLevel':30, 'cooldown':15},
                            ]
                          )})
            elif name == '즉흥적인 감각의 탱고':
                io.append({'스킬':({'job':'공통', 'jid':None},
                            [
                                {'minLevel':75, 'maxLevel':80, 'cooldown':15},
                            ]
                          )})
            elif name == '매혹적인 리듬의 룸바':
                io.append({'스킬':({'job':'공통', 'jid':None},
                            [
                                {'minLevel':35, 'maxLevel':45, 'cooldown':15},
                            ]
                          )})
            elif name == '정열적인 흐름의 삼바':
                io.append({'스킬':({'job':'공통', 'jid':None},
                            [
                                {'minLevel':60, 'maxLevel':70, 'cooldown':15},
                            ]
                          )})
            """
        elif step == 5 and name == '베테랑 군인의 정복 세트':
            io.pop(1)
            io[1] = {'추댐': 29}
        elif step == 3 and name == '전설의 대장장이 - 역작 세트':
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':1, 'maxLevel':48, 'cooldown':20},
                            {'minLevel':60, 'maxLevel':80, 'cooldown':20},
                        ]
                      )})
        elif step == 5 and name == '전설의 대장장이 - 역작 세트':
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':50, 'maxLevel':50, 'cooldown':30},
                            {'minLevel':85, 'maxLevel':85, 'cooldown':30},
                            {'minLevel':100, 'maxLevel':100, 'cooldown':17},
                        ]
                      )})
        elif step == 3 and name == '구속의 가시덩굴 세트':
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':1, 'maxLevel':48, 'cooldown':15},
                            {'minLevel':60, 'maxLevel':80, 'cooldown':15},
                            {'minLevel':90, 'maxLevel':95, 'cooldown':15},
                        ]
                        )})
        elif step == 5 and name == '구속의 가시덩굴 세트':
            io.append({'이속':-2})
 
        elif step == 3 and name == '선택의 기로 세트':
            for opts in io:
                if '공속' in opts.keys():
                    if '증감' in opts.keys():
                        opts['공속'] = opts['이속'] = opts['캐속'] = 0
                    else:
                        opts['공속'] = opts['이속'] = 14
                        opts['캐속'] = 21

        elif (name == '지체없는 흐름의 한뉘' or name == '영명한 세상의 순환') and step < 0:
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':45, 'maxLevel':45, 'damdown':30, 'coolrecover':100},
                        ]
                        )})
            io.append({'스킬':({'job':'크리에이터', 'jid':cls.get_jobid('크리에이터', skill_db)},
                        [
                            {'skillId':cls.get_skillid('크리에이터', '웜홀', skill_db),
                             'name':'웜홀',
                             'coolrecover':100, 'damdown':30
                            }

                        ]
                        )})
        elif name == '지체없는 흐름의 미리내' and step < 0:
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':25, 'maxLevel':25, 'damdown':30, 'coolrecover':100}
                        ]
                        )})
        elif name == '지체없는 흐름의 마루' and step < 0:
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':35, 'maxLevel':35, 'damdown':30, 'coolrecover':100}
                        ]
                        )})
        elif name == '지체없는 흐름의 가람' and step < 0:
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':40, 'maxLevel':40, 'damdown':30, 'coolrecover':100}
                        ]
                        )})
        elif name == '지체없는 흐름의 바람' and step < 0:
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':30, 'maxLevel':30, 'damdown':30, 'coolrecover':100}
                        ]
                        )})
            """
        elif step == 2 and name == '영원한 흐름의 길 세트':
             io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':60, 'maxLevel':60, 'damup':20, 'coolup':30}
                        ]
                        )})
        elif step == 3 and name == '영원한 흐름의 길 세트':
             io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':70, 'maxLevel':70, 'damup':20, 'coolup':30}
                        ]
                        )})
            """
        elif name == '임의 선택' and step < 0:
            for opts in io:
                for key in opts:
                    if key in ['증추', '크증추', '모공', '물마독공', '스공']:
                        opts[key] *= 0.2
            
        elif name == '합리적 선택' and step < 0:
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':50, 'maxLevel':50, 'damup':25},
                            {'minLevel':85, 'maxLevel':85, 'damup':45},
                            {'minLevel':100, 'maxLevel':100, 'damup':13},
                        ]
                      )})

        elif step == 3 and name == '먼동 틀 무렵 세트':
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':100, 'maxLevel':100, 'value':1},
                        ]
                      )})

        elif step == 3 and name == '행운의 트라이앵글 세트':
            for opts in io:
                if '스공' in opts.keys():
                    if opts['스공'] == 27:
                        opts['스공'] = 27*0.5 + 31*0.45 + 34*0.05
                    elif opts['스공'] == 31:
                        #opts['스공'] = 0
                        del opts['스공']
                    else:
                        #opts['스공'] = 0
                        del opts['스공']
        elif step == 2 and name == '고대의 술식 세트':
            for opts in io:
                if '이속' in opts.keys():
                    opts['이속'] /= 12

        elif (name == '새벽을 녹이는 따스함' or name == '새벽을 감싸는 따스함') and step < 0:
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            #{'minLevel':1, 'maxLevel':48, 'value':1},
                            {'minLevel':15, 'maxLevel':30, 'coolrecover':30},
                        ]
                      )})
        elif name == '달빛을 가두는 여명' and step < 0:
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            #{'minLevel':50, 'maxLevel':70, 'value':1},
                            {'minLevel':35, 'maxLevel':45, 'coolrecover':30},
                        ]
                      )})
        elif name == '고요를 머금은 이슬' and step < 0:
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            #{'minLevel':75, 'maxLevel':85, 'value':1},
                            {'minLevel':60, 'maxLevel':80, 'coolrecover':30},
                        ]
                      )})
        elif step == 3 and name == '정령사의 장신구 세트':
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':1, 'maxLevel':100, 'cooldown':10},
                        ]
                      )})
        elif step == 3 and name == '영보 : 세상의 진리 세트':
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            #{'minLevel':1, 'maxLevel':85, 'value':1},
                            {'minLevel':100, 'maxLevel':100, 'value':1},
                        ]
                      )})
        elif name == '종말의 시간' and step < 0:
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':1, 'maxLevel':100, 'cooldown':12},
                        ]
                      )})
        elif name == '전자기 진공관' and step < 0:
            for opts in io:
                if '추댐' in opts.keys():
                    opts['condition'] = {'type':'착용', 'required':['제어회로모듈']}
                elif '모속강' in opts.keys():
                    opts['condition'] = {'type':'착용', 'required':['에너지분배제어기']}
        elif name == '플라즈마 초 진공관' and step < 0:
            for opts in io:
                if '추댐' in opts.keys():
                    opts['이속'] = 10
                    opts['condition'] = {'type':'착용', 'required':['제어회로모듈']}
                    opts['모속저'] = 20
                elif '모속강' in opts.keys():
                    opts['condition'] = {'type':'착용', 'required':['에너지분배제어기']}

        elif step == 2 and name == '심연을 엿보는 자 세트':
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':1, 'maxLevel':48, 'value':1},
                        ]
                      ),
                      'condition':{'type':'암속저','per-val':28, 'max':2}
                      })
        elif step == 3 and name == '심연을 엿보는 자 세트':
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':60, 'maxLevel':80, 'value':1},
                        ]
                      ),
                      'condition':{'type':'암속저','per-val':30, 'max':2}
                      })
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':50, 'maxLevel':50, 'value':1},
                            {'minLevel':85, 'maxLevel':85, 'value':1},
                            {'minLevel':100, 'maxLevel':100, 'value':1},
                        ]
                      ),
                      'condition':{'type':'암속저','per-val':61, 'max':None}
                      })
        elif name == '길 안내자의 계절' and step < 0:
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':1, 'maxLevel':48, 'cooldown':10},
                            {'minLevel':60, 'maxLevel':80, 'cooldown':10},
                            {'minLevel':90, 'maxLevel':95, 'cooldown':10},
                        ]
                      ),
                      '이속':10,
                      })
        elif step == 3 and name == '황혼의 여행자 세트':
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':1, 'maxLevel':48, 'cooldown':10},
                            {'minLevel':60, 'maxLevel':80, 'cooldown':10},
                            {'minLevel':90, 'maxLevel':95, 'cooldown':10},
                        ]
                      )})
        elif name == '시간에 휩쓸린 물소 각반' and step < 0:
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':60, 'maxLevel':80, 'cooldown':10},
                        ]
                      )})
        elif name == '시간을 거스르는 자침' and step < 0:
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':50, 'maxLevel':50, 'cooldown':15},
                            {'minLevel':85, 'maxLevel':85, 'cooldown':15},
                        ]
                      )})
        elif name == '시간을 가리키는 지침' and step < 0:
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':50, 'maxLevel':50, 'cooldown':10},
                            {'minLevel':85, 'maxLevel':85, 'cooldown':10},
                        ]
                      )})

        elif name == '시간에 갇혀버린 모래' and step < 0:
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':1, 'maxLevel':45, 'cooldown':10},
                        ]
                      )})

        elif name == '나락으로 빠진 발' and step < 0:
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':1, 'maxLevel':90, 'value':1},
                            {'minLevel':100, 'maxLevel':100, 'value':1},
                        ]
                      ),
                      'condition':{'type':'암속저','per-val':16, 'max':None}
                      })
        elif name == '차원을 걷는 물소 부츠' and step < 0:
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':1, 'maxLevel':45, 'value':1},
                        ]
                      )})
        elif name == '차원을 지나는 자의 인장' and step < 0:
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':60, 'maxLevel':80, 'value':1},
                        ]
                      )})
        elif (name == '차원을 관통하는 초신성' or name == '차원을 맴도는 혜성') and step < 0:
            io.append({'스킬':({'job':'공통', 'jid':None},
                        [
                            {'minLevel':50, 'maxLevel':50, 'value':1},
                            {'minLevel':85, 'maxLevel':85, 'value':1},
                            {'minLevel':100, 'maxLevel':100, 'value':1},
                        ]
                      )})
        elif (name == '무너진 세상의 슬픔' or name == '광란을 품은 자의 종막' or name == '슬픔을 담은 운명') and step < 0:
            for opts in io:
                if '추댐' in opts.keys():
                    if opts['추댐'] == 8 or opts['추댐'] == 12:
                        opts['추댐'] = 0
        elif name == '아린 고통의 비극' and step < 0:
            for opts in io:
                if '추댐' in opts.keys():
                    opts['추댐'] = 5.5
        elif name == '천상의 날개' and step < 0:
            io.append({'이속':25})
        elif step == 3 and name == "열대의 트로피카 세트":
            io.append({'이속':5, 'condition':{'type':'착용', 'required':['트로피카:리치']}})
        elif step == 5 and name == "메마른 사막의 유산 세트":
            for opts in io:
                if '스공' in opts.keys() and opts['스공'] == 4:
                    opts['스공'] = 1
        elif name in ['전쟁의 시작', '오퍼레이션 델타', '퀘이크 프론', '전장의 매', '데파르망'] and iid is not None:
            try:
                io.pop(0)
            except:
                #print (name, io, explain, iid)
                pass

        elif name == '종말의 역전' and step < 0:
            for opts in io:
                if '물마독공' in opts.keys():
                    opts['물마독공'] *= -1
                   
        return io

    @classmethod
    def get_jobid(self, name, skill_db):
        for jid in skill_db.keys():
            if skill_db[jid]['name'] == name:
                return jid

    @classmethod
    def get_skillid(self, jobname, skillname, skill_db):
        for jid in skill_db.keys():
            if skill_db[jid]['name'] == jobname:
                break

        for gid in skill_db[jid].keys():
            if gid == 'name':
                continue
            for skill in skill_db[jid][gid]['skills']:
                if skill['name'] == skillname:
                    return skill['skillId']
    """
    @classmethod
    def parse_stats(cls, stats, io):
        for stat in stats:
            s = stat['name'].replace(' ','').replace('캐스팅', '캐스트')
            if s in item_stat_type:
                v = stat['value']
                print (s, ":", v, None)
                io.append({s:(v, None)})
            #else:
                #io.append({'미분류s':s})

        return io
    """
    @classmethod
    def build_single_item(cls, ids, skill_db, item_db, runtime = True):
        item_ids = ','.join(ids)

        url = "multi/items?itemIds=" + item_ids + "&"
        item_dict = cls.load_api(url)
        #with open("item_dict.json", "w") as f:
            #json.dump(item_dict, f)

        for cur in item_dict['rows']:
            item_id = cur['itemId']
            name = cur['itemName']
            itype = cur['itemType']
            ityped = cur['itemTypeDetail']
            igrade = cur['itemRarity']
            remodel = cur.get('remodelInfo')
            transform = cur.get('transformInfo')
            siroco = cur.get('sirocoInfo')
            status = cur.get('itemStatus')

            if runtime is False:
                if itype == '무기':
                    if cls.weapon_tree.get(itype) is None:
                        cls.weapon_tree[itype] = {}
                        cls.weapon_tree[itype][ityped] = {}
                    else:
                        if cls.weapon_tree[itype].get(ityped) is None:
                            cls.weapon_tree[itype][ityped] = {}

                    cls.weapon_tree[itype][ityped][item_id] = {'name': name, 'rarity': igrade, 'status': status, 'type': ityped}

                    if remodel is not None:
                        cls.weapon_tree[itype][ityped][item_id]['remodel'] = True
                        if transform is not None:
                            cls.weapon_tree[itype][ityped][item_id]['upgrade'] = True
                        else:
                            cls.weapon_tree[itype][ityped][item_id]['upgrade'] = False

                    else:
                        cls.weapon_tree[itype][ityped][item_id]['remodel'] = False

                        cls.weapon_tree[itype][ityped][item_id]['upgrade'] = False

                elif cur.get('setItemId') is None and remodel is not None:
                    if ityped[0] == '천':
                        if cls.item_tree.get(ityped) is None:
                            cls.item_tree[ityped] = {}

                        if transform is not None:
                            upgr = True
                        else:
                            upgr = False

                        cls.item_tree[ityped][item_id] = {'name': name, 'rarity': igrade, 'remodel': True, 'upgr': upgr}
                elif cur.get('setItemId') is None and siroco is not None:
                    _name = name.replace(' ', '').split(':')[1]
                    setName = _name.split('의')[0]

                    if ityped.find(' ') >= 0:
                        slot = ityped.split(' ')[1]
                    else:
                        slot = ityped

                    if cls.set_tree.get(setName) is None:
                        cls.set_tree[setName] = {'name': setName, 'itemList': {}}
                        
                    cls.set_tree[setName]['itemList'][slot] = {'name': name, 'rarity': igrade, 'id': item_id}
                elif ityped == '칭호':
                    if cls.set_tree.get(ityped) is None:
                        cls.set_tree[ityped] = {'name': ityped, 'itemList':[]}

                    cls.set_tree[ityped]['itemList'].append({'name': name, 'rarity': igrade, 'id': item_id})


            item = {}
            item['name'] = name
            item['options'] = []
            item['buffopts'] = []
            #print(name)

            explain = cur['itemExplainDetail']
            #e_origin_list = explain.split('\n')
            #item['origin'] = e_origin_list

            """
            if remodel is not None:
                step_mode = -1
            else:
                step_mode = -2
            """

            cls.parse_explain(explain, item['options'], name, skill_db, step = -1, iid = item_id)

            if explain.find("파티원이 2명") >= 0:
                item['synergy'] = {'깡스탯': 10}

            buffopt = cur.get('itemBuff')
            if buffopt is not None:
                buffexplain = buffopt['explain']
                cls.parse_buff(buffexplain, item['buffopts'], name, skill_db, step = -1)

                skills = buffopt.get('reinforceSkill')
                if skills is not None and len(skills) > 0:
                    for skill in skills[0]['skills']:
                        if skill['name'] in ['마리오네트', '아포칼립스', '크럭스 오브 빅토리아']:
                            odata = {'포레벨':skill['value']}
                        elif skill['name'] in ['영광의 축복', '용맹의 축복', '금단의 저주']:
                            odata = {'축레벨':skill['value']}
                        elif skill['name'] in ['소악마', '신실한 열정', '신념의 오라']:
                            odata = {'오라레벨':skill['value']}
                        else:
                            print(skills)
                            odata = None
                            #raise Exception
                        if odata is not None:
                            item['buffopts'].append(odata)

            skills = cur.get('itemReinforceSkill')
            if skills is not None:
                for s in skills:
                    e = []
                    try:
                        v = {'job':s['jobName'], 'jid':s['jobId']}
                        if 'levelRange' in s.keys():
                            for r in s['levelRange']:
                                e.append(r)
                        if 'skills' in s.keys():
                            for r in s['skills']:
                                e.append(r)
                    except:
                        #print(item_id)
                        #print(skills)
                        raise

                    item['options'].append({'스킬':(v, e)})

            #remodel = cur.get('remodelInfo')
            if remodel is not None:
                _explain = remodel['explain'].split('버퍼 전용')

                explain = _explain[0]
                if len(_explain) == 2:
                    buffExplain = _explain[1]
                else:
                    buffExplain = None
               
                cls.parse_explain(explain, item['options'], name, skill_db)

                if buffExplain is not None:
                    cls.parse_buff(buffExplain, item['buffopts'], name, skill_db, step = 10)

                explain = explain.replace('\n(', '(')
                #e_origin_list = explain.split('\n')
                #item['remodel_origin'] = e_origin_list

                if remodel['stepInfo'] is not None:
                    for step in remodel['stepInfo']:
                        _explain = step.get('explainDetail')
                        if _explain is None:
                            _explain = step.get('explain')
                        _explain = _explain.split("버퍼 전용")

                        explain = _explain[0]
                        if len(_explain) == 2:
                            buffExplain = _explain[1]
                        else:
                            buffExplain = None

                        #print(explain)

                        stepinfo = {}
                        """
                        if step.get('transform') is True:
                            #_explain = explain.replace('%', '')
                            #print(explain, name, item_id)
                            try:
                                expRange = re.findall(r'\(.*?\)', explain)[0][1:-1]
                                _explain_prefix = explain.split('(')[0]
                                _explain_postfix = explain.split(')')[1]

                                if expRange.find('~') < 0:
                                    raise Exception
                            except:
                                __explain_prefix = []
                                __explain_postfix = []
                                expRange_list = explain.split(' ')
                                pre = True
                                for expr in expRange_list:
                                    if expr.find('~') >= 0 and pre is True:
                                        expRange = expr
                                        pre = False
                                    elif pre is True:
                                        __explain_prefix.append(expr)
                                    else:
                                        __explain_postfix.append(expr)

                                _explain_prefix = ' '.join(__explain_prefix)
                                _explain_postfix = ' '.join(__explain_postfix)

                            #print(expRange)

                            expRange = expRange.split('~')

                            #range_min = int(expRange[0])
                            #range_max = int(expRange[1])
                            range_max = expRange[1]

                            explain = _explain_prefix + range_max + _explain_postfix

                            stepinfo['transform'] = True
                        """

                        if step.get('transform') is None:
                            stepinfo['step'] = step['step']
                            stepinfo['options'] = []
                            cls.parse_explain(explain, stepinfo['options'], name, skill_db, step = step['step'])
                            #e_origin_list = explain.split('\n')
                            #stepinfo['origin'] = e_origin_list

                            if buffExplain is not None:
                                stepinfo['buffopts'] = []
                                cls.parse_buff(buffExplain, stepinfo['buffopts'], name, skill_db, step = step['step'])
         
                            item['options'].append(stepinfo)

            """
            transform = cur.get('transformInfo')
            if transform is not None:

                explain = transform['explain']

                topt = []
                if explain.find('모든 직업') >= 0:
                    topt.append({'각성기':2})
                else:
                    if name == '데파르망':
                        cls.parse_explain(transform['explainDetail'], topt, name, skill_db, step = -2, iid = item_id)
                    else:
                        cls.parse_explain(explain, topt, name, skill_db, step = -2, iid = item_id)

                item['options'].append({'transform': topt})
            """

            itemStatus = cur.get('itemStatus')
            if itemStatus is not None and len(itemStatus) > 0:
                item['status'] = itemStatus

            mythInfo = cur.get('mythologyInfo')
            if mythInfo is not None:
                cls.myth_db[item_id] = {'name':name, 'options':[], 'buffOptions':[]}

                mopt = mythInfo['options']
                for o in mopt:
                    mexp = o['explain']
                    fexp = re.sub('\d', '*', mexp)

                    mexpd = o['explainDetail']
                    expRange = re.findall(r'\(.*?\)', mexpd)[0][1:-1]
                    expRange = expRange.split('~')

                    range_min = expRange[0]
                    range_max = expRange[1]
                    
                    cls.myth_db[item_id]['options'].append({'explain':fexp, 'min':range_min, 'max':range_max})

                    mexp = o['buffExplain']
                    fexp = mexp[:2] + re.sub('\d', '*', mexp[2:])

                    mexpd = o['buffExplainDetail']
                    expRange = re.findall(r'\(.*?\)', mexpd)[0][1:-1]
                    expRange = expRange.split('~')

                    range_min = expRange[0]
                    range_max = expRange[1]

                    cls.myth_db[item_id]['buffOptions'].append({'explain':fexp, 'min':range_min, 'max':range_max})
            item_db[item_id] = item

    @classmethod
    def build_set_option(cls, sid, sname, options, skill_db, set_db):
        sopt = {}
        sopt['name'] = sname
        #print(sname)

        for option in options:
            n = option['optionNo']
            sopt[str(n)] = {}
            sopt[str(n)]['options'] = []
            sopt[str(n)]['buffopts'] = []
            
            if 'detailExplain' in option.keys():
                explain = option['detailExplain']
            else:
                explain = option.get('explain')

            #print(n, explain)

            if explain is not None:
                cls.parse_explain(explain, sopt[str(n)]['options'], sname, skill_db, step = n)

                if explain.find("2명 이상인 경우") >= 0:
                    #explain = explain.split("2명 이상인 경우")[1]
                    sopt[str(n)]['synergy'] = sname + '|' + str(n)
           
            itemStatus = option.get('status')
            if itemStatus is not None and len(itemStatus) > 0:
                sopt[str(n)]['status'] = itemStatus
                #for stat in itemStatus:
                #    if stat['name'] in ['지능', '체력', '정신력', '암속성저항']:
                #        sopt[str(n)]['status'].append(stat)

            skill = option.get('reinforceSkill')
            #if skill is not None:
            #    print ('스킬옵션있음', skill)

            buffopt = option.get('itemBuff')
            if buffopt is not None or (sname == '전설의 대장장이 - 역작 세트' and n == 5):
                try:
                    buffexplain = buffopt['explain']
                    isreturn = False
                except:
                    buffexplain = ""
                    isreturn = True

                cls.parse_buff(buffexplain, sopt[str(n)]['buffopts'], sname, skill_db, step = n)

                if isreturn is True:
                    continue

                skills = buffopt.get('reinforceSkill')
                if skills is not None and len(skills) > 0:
                    lv30 = False
                    lv50 = False
                    lv45 = False
 
                    for skill in skills:
                        if skill.get('skills') is not None:
                            for skill in skill['skills']:
                                if skill['name'] in ['마리오네트', '아포칼립스', '크럭스 오브 빅토리아']:
                                    if lv50 is False:
                                        sopt[str(n)]['buffopts'].append({'포레벨':skill['value']})
                                        lv50 = True
                                elif skill['name'] in ['영광의 축복', '용맹의 축복', '금단의 저주']:
                                    if lv30 is False:
                                        sopt[str(n)]['buffopts'].append({'축레벨':skill['value']})
                                        lv30 = True
                                elif skill['name'] in ['소악마', '신실한 열정', '신념의 오라']:
                                    if lv45 is False:
                                        sopt[str(n)]['buffopts'].append({'오라레벨':skill['value']})
                                        lv45 = True
                                else:
                                    print(skills)
                                    raise Exception
                        elif skill.get('levelRange') is not None:
                            for lvRange in skill['levelRange']:
                                min_lv = int(lvRange['minLevel'])
                                max_lv = int(lvRange['maxLevel'])
                                lvup = int(lvRange['value'])

                                data = {'min':min_lv, 'max':max_lv, 'lvup':lvup}
                                sopt[str(n)]['buffopts'].append({'스킬구간': data})

            else:
                pass
                #print(sname)

            #e_origin_list = explain.split('\n')
            #sopt[str(n)].append({'origin':e_origin_list})


            #stats = option.get('status')
            #if stats is not None:
            #    self.parse_stats(stats, sopt[str(n)])

            #print("")

        set_db[sid] = sopt

        #수동 작업 목록

        #아린 혈관파열
        #시간자침(신화) 쿨초
        #세계수의 뿌리 쿨초

        #print(self.set_db)

    @classmethod
    def do_build_set_item(cls, setId, name, skill_db, item_db, set_db, runtime = True):
        url = "setitems/" + setId + "?"
        s_info = cls.load_api(url)

        sitems = s_info['setItems']
        soptions = s_info['setItemOption']

        if runtime is False:
            cls.set_tree[setId] = {'name': name, 'itemList': {}}

        ids = []
        for cur in sitems:
            #print (item['itemName'])

            if runtime is False:
                iname = cur['itemName']
                islot = cur['slotName']
                
                url = "items?itemName="+urlparse.quote(iname)+"&"

                try:
                    i_search = cls.load_api(url)
                except:
                    raise
    
                try:
                    if len(i_search['rows']) > 5:
                        mat_count = {'천':0, '가죽':0, '중갑':0, '경갑':0, '판금':0}

                        for ilist in i_search['rows']:
                            _ityped = ilist['itemTypeDetail']
                            ityped = _ityped.split(' ')[0]
                            
                            mat_count[ityped] += 1

                        if max(mat_count.values()) == 2:
                            oritype = '판'
                        else:
                            for k, v in mat_count.items():
                                if v == 3:
                                    oritype = k[0]

                    else:
                        oritype = None

                    for ilist in i_search['rows']:
                        itemId = ilist['itemId']
                        igrade = ilist['itemRarity']
                        ityped = ilist['itemTypeDetail']

                        if igrade == '신화':
                            url = 'items/' + itemId + '?'
                            itemDetail = cls.load_api(url)

                            status = itemDetail.get('itemStatus')

                            cls.set_tree[setId]['itemList']['신화'] = {'name': iname, 'rarity': igrade, 'id':itemId, 'slot':islot}
                        else:
                            if oritype is not None:
                                if oritype == ityped[0]:
                                    url = 'items/' + itemId + '?'

                                    itemDetail = cls.load_api(url)

                                    remodel = itemDetail.get('remodelInfo')
                                    transform = itemDetail.get('transformInfo')
                                    status = itemDetail.get('itemStatus')

                                    if remodel is not None:
                                        if transform is not None:
                                            cls.set_tree[setId]['itemList']['업글산물-' + islot] = {'name': iname, 'rarity': igrade, 'id':itemId, 'status':status}
                                        else:
                                            cls.set_tree[setId]['itemList']['산물-' + islot] = {'name': iname, 'rarity': igrade, 'id':itemId, 'status':status}
                                    else:
                                        cls.set_tree[setId]['itemList'][islot] = {'name': iname, 'rarity': igrade, 'id':itemId, 'status':status}
                            else:
                                url = 'items/' + itemId + '?'

                                itemDetail = cls.load_api(url)

                                remodel = itemDetail.get('remodelInfo')
                                transform = itemDetail.get('transformInfo')
                                status = itemDetail.get('itemStatus')

                                if remodel is not None:
                                    if transform is not None:
                                        cls.set_tree[setId]['itemList']['업글산물-' + islot] = {'name': iname, 'rarity': igrade, 'id':itemId, 'status':status}
                                    else:
                                        cls.set_tree[setId]['itemList']['산물-' + islot] = {'name': iname, 'rarity': igrade, 'id':itemId, 'status':status}
                                else:
                                    cls.set_tree[setId]['itemList'][islot] = {'name': iname, 'rarity': igrade, 'id':itemId, 'status':status}


                        #print(ilist['itemName'], itemId)
                        ids.append(itemId)

                        if len(ids) >= 15:
                            cls.build_single_item(ids, skill_db, item_db, runtime = False)
                            ids = []
                except:
                    print(ilist)
                    raise

            if len(ids) > 0:    
                cls.build_single_item(ids, skill_db, item_db, runtime = False)
            cls.build_set_option(setId, name, soptions, skill_db, set_db)
            retId = setId

        return retId

    @classmethod
    def build_set_item(cls, name, skill_db, item_db, set_db, runtime = True):
        url = "setitems?setItemName="+urlparse.quote(name)+"&"
        #print(url)
        retId = None
        try:
            s_search = cls.load_api(url)
            print(s_search)
        except:
            url = "setitems?setItemName="+urlparse.quote(name)+"&wordType=full&"
            s_search = cls.load_api(url)
            #print(s_search)
            raise
        try:
            for slist in s_search['rows']:
                setId = slist['setItemId']

                retId = cls.do_build_set_item(setId, name, skill_db, item_db, set_db, runtime)

        except:
            #print(slist)
            raise

        return retId
