# !/usr/bin/env python
# -*- coding:utf-8 -*-
# project name: DNSAutoSwitch
# author: "Lei Yong"
# creation time: 2022/8/10 3:21 PM
# Email: leiyong711@163.com

import re
import os
import yaml
import requests
import traceback
from tcping import Ping
from utils.log import lg
from pathlib import Path

BASE_DIR = Path(os.path.dirname(__file__)).parent


class DNSAutoSwitch:

    def __init__(self, config_path):
        self.config = yaml.load(open(config_path, 'r'), Loader=yaml.FullLoader)
        self.router_password = str(self.config.get('router_password'))  # 路由器管理员密码
        self.default_gateway = self.config.get('default_gateway')  # 默认网关
        self.open_wrt_ip = self.config.get('open_wrt_ip')  # openWRT IP
        self.stok = ''
        self.url = "http://tplogin.cn"
        self.key = "RDpbLfCPsJZ7fiv"
        self.long_key = 'yLwVl0zKqws7LgKPRQ84Mdt708T1qQ3Ha7xv3H7NyU84p21BriUWBU43odz3iP4rBL3cD02KZciXTysVXiV8ngg6vL48rPJyAUw0HurW20xqxv9aYb4M9wK1Ae0wlro510qXeU07kV57fQMc8L6aLgMLwygtc0F10a0Dg70TOoouyFhdysuRMO51yY5ZlOZZLEal1h0t9YQW0Ko7oBwmCAHoic4HYbUyVeU3sfQ1xtXcPcf1aT303wAQhv66qzW'
        self.password = self.password = self.encrypt_passwd(self.key, self.router_password, self.long_key)
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
        self.main()


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
        ping_text = ''
        try:
            ping.ping(verifi_count)
            ret = ping.result.rows
            ping_text = f"Ping {ip}[{port}]结果" \
                        f"成功次数: {ret[0].successed}\t" \
                        f"失败次数: {ret[0].failed}\t" \
                        f"成功率: {ret[0].success_rate}\t" \
                        f"最小延迟: {ret[0].minimum}\t" \
                        f"最大延迟: {ret[0].maximum}\t" \
                        f"平均延迟: {ret[0].average}"
            average = re.findall(r'\d+\.\d+', ret[0].average)[0]
        except:
            lg.error(f"无法连接到 {ip}")
        return average, ping_text

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

    def set_port_mapping(self, default):
        """
        设置端口映射IP
        :param ports:
        :param new_ip:
        :return:
        """
        path = f'/stok={self.stok}/ds'
        params = {
            "firewall": {
                "table": "redirect"
            },
            "method": "get"
        }
        try:
            # 获取端口转发配置
            self.port_mapping_table = self.config.get('port_mapping_table')
            port_list = [i for i in self.port_mapping_table]

            # 获取现有端口转发列表
            resp = requests.post(url=self.url + path, headers=self.headers, json=params).json()
            if resp.get('error_code') != 0 or not resp.get('firewall'):
                lg.warning(f"获取端口映射关系失败\n响应:{str(resp)}")
                return

            if resp['firewall'].get('redirect'):
                for i in resp['firewall'].get('redirect'):
                    for k, v in i.items():
                        src_dport_start = int(v.get('src_dport_start'))
                        if src_dport_start in port_list:
                            server_name = self.port_mapping_table[src_dport_start].get('name')
                            if default:
                                # 还原默认端口转发
                                ip = self.port_mapping_table[src_dport_start]['default'].get('ip')
                                port = self.port_mapping_table[src_dport_start]['default'].get('port')
                            else:
                                # 修改端口转发到openWRT
                                ip = self.port_mapping_table[src_dport_start]['main_election'].get('ip')
                                port = self.port_mapping_table[src_dport_start]['main_election'].get('port')

                            new_ip_info = {
                                "firewall": {
                                    k: {
                                        "proto": "all",
                                        "src_dport_start": src_dport_start,
                                        "src_dport_end": src_dport_start,
                                        "dest_ip": ip,
                                        "dest_port": port
                                    }
                                },
                                "method": "set"
                            }

                            tmp = requests.post(url=self.url + f'/stok={self.stok}/ds', headers=self.headers, json=new_ip_info).json()
                            if tmp.get('error_code') == 0:
                                lg.info(f"端口转发修改成功,服务: {server_name} 外部端口: {src_dport_start},映射IP: {i[k]['dest_ip']}:{i[k]['dest_port']} --> {ip}:{port}")
                            else:
                                lg.info(f"端口转发修改失败,服务: {server_name} 外部端口: {src_dport_start},映射IP: {i[k]['dest_ip']}:{i[k]['dest_port']} --> {ip}:{port}\n原因:\n{tmp}")
        except:
            lg.error(f"设置端口映射IP异常,原因:\n{traceback.format_exc()}")

    def main(self):
        lg.info("开始检查 OpenWRT 状态")
        try:
            if not self.login_status:
                lg.warning("路由器登陆失败, 可能正在进行重启")
                return

            online_host = self.ip_status()
            open_wrt_status = False  # OpenWRT服务可用状态
            update_text = ''  # OpenWRT服务可用状态
            ping_text = ''
            ip = []
            for ip_info in online_host:

                for k, v in ip_info.items():
                    ip.append(v.get('ip'))
                    if self.open_wrt_ip in v.get('ip'):
                        # 获取 OpenWRT IP 延迟
                        temp_average, ping_text = self.ping(self.open_wrt_ip, port=80, verifi_count=3, time_out=10)
                        average = float(temp_average)
                        if average != 0.0 or average <= 100:
                            update_text = f"OpenWRT IP延迟: {average} ms, 符合阈值 1 - 100ms 范围"
                            open_wrt_status = True
                        else:
                            update_text = f"OpenWRT IP延迟: {average} ms, 不符合阈值 1 - 100ms 范围"
                            open_wrt_status = False
            if not open_wrt_status:
                if ip.count('192.168.0.107') > 1 and self.open_wrt_ip not in ip:
                    lg.info(f"无需修改，由于发现多个 192.168.0.107 数据,当前找到的ip: {'、'.join(ip)}")
                    return
                update_text = f"未从路由器找到OpenWRT IP {self.open_wrt_ip},当前找到的ip: {'、'.join(ip)}"

            udhcpd = self.get_dns_info()
            if udhcpd:
                # OpenWRT服务正常 且 当前路由器网关不为OpenWRT IP
                if open_wrt_status and self.open_wrt_ip not in udhcpd.get('gateway'):

                    # 修改端口映射IP
                    self.set_port_mapping(default=False)

                    # 修改网关到OpenWRT
                    lg.info(f"正在修改网关到OpenWRT...")
                    if ping_text:
                        lg.info(ping_text)
                    lg.info(f"修改原因: {update_text}")
                    self.set_dns(self.open_wrt_ip)
                    lg.info(f"修改网关到OpenWRT成功")
                    self.reboot()  # 重启路由器

                # OpenWRT服务异常 且 当前路由器网关 为OpenWRT IP
                elif not open_wrt_status and self.open_wrt_ip in udhcpd.get('gateway'):

                    # 还原端口映射IP
                    self.set_port_mapping(default=True)

                    # 还原默认网关
                    lg.info(f"正在还原默认网关...")
                    lg.info(f"修改原因: {update_text}")
                    self.set_dns(self.default_gateway)
                    lg.info(f"还原默认网关成功")
                    self.reboot()  # 重启路由器

                else:
                    if ping_text:
                        lg.info(ping_text)
                    lg.info(f"无需修改")
        except:
            lg.error(f"检查 OpenWRT 状态异常,原因\n{traceback.format_exc()}")
        finally:
            lg.info("完成 OpenWRT 状态检查")


if __name__ == '__main__':
    DNSAutoSwitch(config_path=f'{BASE_DIR}/DNSAutoSwitch/port_mapping_table.yaml')


