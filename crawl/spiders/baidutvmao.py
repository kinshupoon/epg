# -*- coding:utf-8 -*-
import requests, re, datetime, json, os, time
from utils.general import headers
from bs4 import BeautifulSoup as bs

def get_epgs_baidutvmao(channel, channel_id, dt, func_arg):
    epgs = []
    msg = ''
    success = 1
    url = 'https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php?query=%s&resource_id=12520&format=json'%(channel_id)
    try:
        res = requests.get(url, headers=headers,timeout=5)
        res.encoding = 'GBK'  # 尝试使用 GBK 编码
        content = res.content.decode('GBK')  # 手动解码响应内容
        data = json.loads(content)['data'][0]['data']  # 解析 JSON 数据
        for j in data:  
            title = j['title'].strip()
            time_str = j.get('times', '')  # 获取时间字段
            if time_str:
                starttime = datetime.datetime.strptime(time_str, '%Y/%m/%d %H:%M')
                if starttime.date() < dt:
                    continue
                if starttime.date() > dt:
                    continue
                epg = {'channel_id': channel.id,
                    'starttime': starttime,
                    'endtime': None,
                    'title': title,
                    'desc': '',
                    'program_date': starttime.date(),
                    }
                epgs.append(epg)
        epglen = len(epgs)
    except Exception as e:
        success = 0
        spidername = os.path.basename(__file__).split('.')[0]
        msg = 'spider-%s- %s' % (spidername,e)
    ret = {
        'success': success,
        'epgs': epgs,
        'msg': msg,
        'last_program_date': dt,
        'ban':0,
    }
    return ret

def get_channels_baidutvmao():
  url_sort = 'https://www.tvmao.com/program/playing/'
  res = requests.get(url_sort, headers=headers, timeout=5)
  res.encoding = 'utf-8'
  soup = bs(res.text, 'html.parser')
  provinces = {}
  big_sorts = {}
  channels = []
  provinces_more = soup.select('div.province > ul.province-list > li')
  big_sorts_more = soup.select('dl.chntypetab > dd')
  for province_more in provinces_more:
    province = province_more.text.strip().replace('黑龙', '黑龙江')
    province_id = province_more.a['href'].replace('/program/playing/',
                                                  '').replace('/', '')
    province = {
        province: province_id,
    }
    provinces.update(province)
  for big_sort_more in big_sorts_more:
    sort_name = big_sort_more.text.strip()
    url = big_sort_more.a['href']
    sort_id = url.replace('/program/playing/', '').replace('/', '')
    if sort_name in provinces or sort_name == '收藏':
      continue
    big_sorts.update({sort_name: sort_id})
  provinces.update(big_sorts)
  sorts = provinces
  n = 0
  for sort_name in sorts:
    url = 'https://www.tvmao.com/program/playing/%s' % sorts[sort_name]
    time.sleep(0.5)
    res = requests.get(url, headers=headers, timeout=5)
    res.encoding = 'utf-8'
    soup = bs(res.text, 'html.parser')
    channel_trs = soup.select('table.timetable > tr')
    n += 1
    for tr in channel_trs:
      tr1 = tr.td.a
      name = tr1['title']
      href = tr1['href']
      id = href.replace('/program/',
                        '').replace('/',
                                    '-').replace('.html',
                                                 '').replace('-program_', '')
      id = re.sub('-w\d$', '', id)
      res1 = tr1['res']
      channel = {
          'name': name,
          'id': name,
          'url': 'https://m.tvmao.com/program/%s.html' % id,
          'source': 'baidutvmao',
          'logo': '',
          'desc': '',
          'sort': sort_name,
          'res': res1,
      }
      channels.append(channel)
    print('%s,%s,id:%s,共有频道：%s' %
          (n, sort_name, sorts[sort_name], len(channel_trs)))

  return channels
