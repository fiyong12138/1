# coding: utf-8
import requests
import sys
import json
import psutil
import time
import schedule
import numpy
from configparser import ConfigParser

config = ConfigParser()  # 传入读取文件的地址，encoding文件编码格式，中文必须
config.read('ini.config', encoding='UTF-8')  # 读取配置文件
token = config['default']['token']
max_cpu = config['mess']['max_cpu']
max_mem = config['mess']['max_mem']

def check_config():  # 验证配置文件格式
    flag = 0
    ini = ['default', 'mess']
    for i in ini:
        if i in config:
            if config['default']['token'] and config['mess']['max_cpu'] and config['mess']['max_mem']:
                continue
            else:
                print("配置文件格式错误1，请从新获取")
                flag = 1
        else:
            print("配置文件格式错误，请从新获取")
            flag = 1
    return flag


def config_set(max_cpu1=50, max_mem1=50):  # 修改警告峰值
    path = 'ini.config'
    config1 = ConfigParser()
    config1.read(path, encoding='UTF-8')
    config1['mess']['max_cpu'] = max_cpu1
    config1['mess']['max_mem'] = max_mem1
    fo = open(path, 'w', encoding='UTF-8')
    config1.write(fo)
    fo.close()


def push_post(token1="", title1="测试token", content1=""):  # 推送微信
    url = 'http://pushplus.hxtrip.com/send'
    data = {'token': token1, 'title': title1, 'content': content1, 'template': 'json'}
    print(content1)
    res1 = requests.post(url=url, data=json.dumps(data), timeout=10)
    print(res1.text)  # 回应内容
    # print(res1.status_code)#发送状态
    return res1.text[8]


def check_token(token1=""):  # 检测token
    resn2 = push_post(token1=token)
    if resn2 == "2" or "6":
        flag = 0
    else:
        print("token无效，请检查配置文件")
        flag = 1
    return flag


def cpu_info():  # 获取cpu使用率
    cpu = psutil.cpu_percent(1)
    time.sleep(0.1)
    cpu2 = psutil.cpu_percent(1)
    time.sleep(0.1)
    cpu3 = psutil.cpu_percent(1)
    cpus = [cpu, cpu2, cpu3]
    cpu = numpy.average(cpus)
    return cpu


def mem_info():  # 获取内存使用率
    mem = psutil.virtual_memory()
    info1 = {'mem_total': mem[0], 'mem_free': mem[1], 'mem_percent': mem[2], 'mem_used': mem[3]}
    return info1


def disk_info():  # 获取硬盘使用率
    disk = psutil.disk_usage('/')
    info2 = {'total': disk[0], 'used': disk[1], 'free': disk[2], 'percent': disk[3]}  # 同样写入一个字典
    return info2


def check_max(m_cpu, m_mem, m_disk):
    t_res = ""
    if m_cpu > 50:
        t_res = "cpu警告"
    if m_mem['mem_percent'] > 50:
        t_res = t_res + "内存警告"
    if m_disk['percent'] > 70:
        t_res = t_res + "硬盘警告"
    return t_res


# def ckeck_


def main():
    if check_config() == 1:
        sys.exit(1)
    if check_token(token) == 1:
        sys.exit(1)
    time.sleep(0.001)
    m_cpu = cpu_info()
    m_mem = mem_info()
    m_disk = disk_info()  # 将各个分函数的调用结果当作函数体输入
    maxs_cpus = []
    maxs_mem = []
    maxs_disk = []

    t_res = check_max(m_cpu, m_mem, m_disk)
    msg = '''{'cpu使用率':'%s%%','内存总量':'%dM','内存使用率':'%s%%','内存使用量':'%dM','磁盘总量':'%sGB','磁盘使用量':'%sGB','磁盘使用率':'%s%%'}''' % (
        m_cpu, int(m_mem.get('mem_total') / 1024 / 1024), m_mem['mem_percent'],
        int(m_mem['mem_used'] / 1024 / 1024), int(m_disk['total'] / 1024 / 1024 / 1024),
        int(m_disk['used'] / 1024 / 1024 / 1024), m_disk['percent'])
    push_post(token1=token, title1=t_res, content1=msg)


if __name__ == '__main__':
    main()
