# !/usr/bin/env python
# -*- coding:utf-8 -*-
# project name: DNSAutoSwitch
# author: "Lei Yong"
# creation time: 2022/8/10 3:21 PM
# Email: leiyong711@163.com

import re
import traceback
import requests
from utils.log import lg
from tcping import Ping


class DNSAutoSwitch:

    def __init__(self, password):
        self.stok = ''
        self.url = "http://tplogin.cn"
        self.key = "RDpbLfCPsJZ7fiv"
        self.long_key = 'yLwVl0zKqws7LgKPRQ84Mdt708T1qQ3Ha7xv3H7NyU84p21BriUWBU43odz3iP4rBL3cD02KZciXTysVXiV8ngg6vL48rPJyAUw0HurW20xqxv9aYb4M9wK1Ae0wlro510qXeU07kV57fQMc8L6aLgMLwygtc0F10a0Dg70TOoouyFhdysuRMO51yY5ZlOZZLEal1h0t9YQW0Ko7oBwmCAHoic4HYbUyVeU3sfQ1xtXcPcf1aT303wAQhv66qzW'
        self.password = self.password = self.encrypt_passwd(self.key, password, self.long_key)
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json; charset=UTF-8',
            'Origin': 'http://tplogin.cn',
            'Referer': 'http://tplogin.cn/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.login_status = False
        self.login()

    def encrypt_passwd(self, a, b, c):
        """
        密码加密，参考 https://blog.csdn.net/weixin_34059951/article/details/92585312
        :param a:
        :param b:
        :param c:
        :return:
        """
        e = ''
        f, g, h, k, l = 187, 187, 187, 187, 187
        n = 187
        g = len(a)
        h = len(b)
        k = len(c)
        if g > h:
            f = g
        else:
            f = h

        for p in list(range(0, f)):
            n = l = 187
            if p >= g:
                n = ord(b[p])
            else:
                if p >= h:
                    l = ord(a[p])
                else:
                    l = ord(a[p])
                    n = ord(b[p])
            e += c[(l ^ n) % k]
        return e

    def login(self):
        """
        登陆后台
        :return:
        """
        try:
            params = {
                "method": "do",
                "login": {
                    "password": self.password
                }
            }

            resp = requests.post(url=self.url, headers=self.headers, json=params).json()
            if resp.get('error_code') == 0 and resp.get('stok'):
                self.stok = resp.get('stok')
                self.login_status = True
        except:
            lg.warning(f"路由器登陆异常,原因\n: {traceback.format_exc()}")

    def ping(self, ip, port=80, verifi_count=3, time_out=5):
        """
        ping ip
        :param ip:
        :param port:
        :param verifi_count: Ping次数
        :param time_out: 单次超时时间
        :return:
        """
        ping = Ping(ip, port, time_out)
        average = 0
        try:
            ping.ping(verifi_count)
            ret = ping.result.rows
            lg.debug(f"Ping {ip}[{port}]结果"
                     f"成功次数: {ret[0].successed}\n"
                     f"失败次数: {ret[0].failed}\n"
                     f"成功率: {ret[0].success_rate}\n"
                     f"最小延迟: {ret[0].minimum}\n"
                     f"最大延迟: {ret[0].maximum}\n"
                     f"平均延迟: {ret[0].average}\n")
            average = re.findall(r'\d+\.\d+', ret[0].average)[0]
        except:
            lg.error(f"无法连接到 {ip}")
        return average

    def ip_status(self):
        """
        获取路由器所有已连接设备信息
        :return:
        """
        path = f'/stok={self.stok}/ds'
        params = {
            "hyfi": {
                "table": ["connected_ext"]
            },
            "hosts_info": {
                "table": "online_host",
                "name": "cap_host_num"
            },
            "method": "get"
        }
        try:
            resp = requests.post(url=self.url + path, headers=self.headers, json=params).json()
            if resp.get('error_code') == 0 and resp.get('hosts_info'):
                online_host = resp['hosts_info'].get('online_host')
                if online_host:
                    # for i in online_host:
                    #     if i.get('hostname'):  # 名称
                    #     if i.get('mac'):  # mac
                    #     if i.get('ip'):  # ip
                    return online_host
            lg.warning(f"获取路由器所有IP状态失败,响应:\n{str(resp)}")
            return []
        except:
            lg.error(f"获取路由器所有IP状态异常,原因:\n{traceback.format_exc()}")
            return []

    def get_dns_info(self):
        """
        获取当前 DNS 配置
        :return:
        """
        path = f'/stok={self.stok}/ds'
        params = {
            "dhcpd": {
                "name": ["udhcpd"],
                "table": ["dhcp_clients"]
            },
            "network": {
                "name": ["lan"]
            },
            "function": {
                "name": ["new_module_spec"]
            },
            "method": "get"
        }
        try:
            resp = requests.post(url=self.url + path, headers=self.headers, json=params).json()
            if resp.get('error_code') == 0 and resp.get('dhcpd'):
                udhcpd = resp['dhcpd'].get('udhcpd')
                if udhcpd:
                    return udhcpd
            lg.error(f"获取当前网关失败,响应:\n{str(resp)}")
            return {}
        except:
            lg.error(f"获取当前网关异常,原因:\n{traceback.format_exc()}")
            return {}

    def reboot(self):
        """
        重启路由器
        :return:
        """
        path = f'/stok={self.stok}/ds'
        params = {
            "system": {
                "reboot": None
            },
            "method": "do"
        }
        try:
            resp = requests.post(url=self.url + path, headers=self.headers, json=params).json()
            if resp.get('error_code') == 0 and resp.get('wait_time'):
                lg.info(f"正在重启路由器, 请稍等 {resp.get('wait_time')} s ...")
            else:
                lg.error(f"重启路由器失败,响应:\n{str(resp)}")
        except:
            lg.error(f"重启路由器异常,原因:\n{traceback.format_exc()}")

    def set_dns(self, ip):
        """
        设置DNS、网关
        :param ip:
        :return:
        """
        udhcpd = self.get_dns_info()
        if not udhcpd:
            lg.warning("未获取到当前 DNS 配置")

        path = f'/stok={self.stok}/ds'
        params = {
            "dhcpd": {
                "udhcpd": {
                    "auto": int(udhcpd.get('auto', '1')),
                    "pool_start": udhcpd.get('pool_start'),
                    "pool_end": udhcpd.get('pool_end'),
                    "lease_time": int(udhcpd.get('lease_time', '7200')),
                    "gateway": ip,  # 网关
                    "pri_dns": ip,  # 首选DNS
                    "snd_dns": udhcpd.get('snd_dns')  # 备选DNS
                }
            },
            "method": "set"
        }
        try:
            resp = requests.post(url=self.url + path, headers=self.headers, json=params).json()
            if resp.get('error_code') == 0:
                lg.info(f"修改DNS、网关为 {ip} 成功")
            else:
                lg.warning(f"修改DNS、网关为 {ip} 失败\n响应:{str(resp)}")
        except:
            lg.error(f"修改DNS、网关为 {ip} 异常,原因:\n{traceback.format_exc()}")

    def main(self, open_wrt_ip, default_gateway='0.0.0.0'):

        if not self.login_status:
            lg.warning("路由器登陆失败, 可能正在进行重启")
            return

        online_host = self.ip_status()
        open_wrt_status = False  # OpenWRT服务可用状态
        update_text = ''  # OpenWRT服务可用状态
        for ip_info in online_host:

            for k, v in ip_info.items():
                if open_wrt_ip in v.get('ip'):
                    # 获取 OpenWRT IP 延迟
                    average = float(self.ping(open_wrt_ip, port=80, verifi_count=3, time_out=10))
                    if average != 0.0 or average <= 100:
                        update_text = f"OpenWRT IP延迟: {average} ms, 符合阈值 1 - 100ms 范围"
                        open_wrt_status = True

        udhcpd = self.get_dns_info()
        if udhcpd:
            # OpenWRT服务正常 且 当前路由器网关不为OpenWRT IP
            if open_wrt_status and open_wrt_ip not in udhcpd.get('gateway'):
                # 修改网关到OpenWRT
                lg.info(f"正在修改网关到OpenWRT...")
                lg.info(f"修改原因: {update_text}")
                self.set_dns(open_wrt_ip)
                lg.info(f"修改网关到OpenWRT成功")
                self.reboot()  # 重启路由器

            # OpenWRT服务异常 且 当前路由器网关 为OpenWRT IP
            elif not open_wrt_status and open_wrt_ip in udhcpd.get('gateway'):
                # 还原默认网关
                lg.info(f"正在还原默认网关...")
                lg.info(f"修改原因: 未从路由器找到OpenWRT IP")
                self.set_dns(default_gateway)
                lg.info(f"还原默认网关成功")
                self.reboot()  # 重启路由器

            else:
                lg.info(f"无需修改")


if __name__ == '__main__':
    dns = DNSAutoSwitch('123456')
    dns.main('192.168.0.130')


