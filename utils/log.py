# !/usr/bin/env python
# -*- coding:utf-8 -*-
# project name: DNSAutoSwitch
# author: "Lei Yong"
# creation time: 2022/8/10 3:22 PM
# Email: leiyong711@163.com

import os
import time
import sys
from pathlib import Path
from loguru import logger as lg


BASE_DIR = Path(os.path.dirname(__file__)).parent

lg.remove()  # 删除import logger之后自动产生的handler, 不删除会出现重复出现的现象
handler_id = lg.add(sys.stderr, level="DEBUG")  # 添加一个可以修改控制的handler

# INFO级日志模板初始化配置
lg.add(f"{BASE_DIR}/logs/info_log_{time.strftime('%Y_%m_%d')}.log",
    level="INFO",
    format='{time:YYYY-MM-DD HH :mm:ss.SSS} - {level} - {file} - {function} - {line} - {message}',
    rotation="00:00",  # 文件过大就会重新生成一个新文件  "12:00"# 每天12点创建新文件
    encoding="utf-8",
    enqueue=True,  # 异步写入
    serialize=False,  # 序列化为json
    retention="10 days",  # 一段时间后会清空
    compression="zip"  # 保存为zip格式
)

# ERROR级日志模板初始化配置
lg.add(f"{BASE_DIR}/logs/error_log_{time.strftime('%Y_%m_%d')}.log",
    level="ERROR",
    format='{time:YYYY-MM-DD HH :mm:ss.SSS} - {level} - {file} - {function} - {line} - {message}',
    rotation="00:00",  # 文件过大就会重新生成一个新文件  "12:00"# 每天12点创建新文件
    encoding="utf-8",
    enqueue=True,  # 异步写入
    serialize=False,  # 序列化为json
    retention="10 days",  # 一段时间后会清空
    compression="zip"  # 保存为zip格式
)

# WARNING级日志模板初始化配置
lg.add(f"{BASE_DIR}/logs/warning_log_{time.strftime('%Y_%m_%d')}.log",
    level="WARNING",
    format='{time:YYYY-MM-DD HH :mm:ss.SSS} - {level} - {file} - {function} - {line} - {message}',
    rotation="00:00",  # 文件过大就会重新生成一个新文件  "12:00"# 每天12点创建新文件
    encoding="utf-8",
    enqueue=True,  # 异步写入
    serialize=False,  # 序列化为json
    retention="10 days",  # 一段时间后会清空
    compression="zip"  # 保存为zip格式
)

# DEBUG级日志模板初始化配置
lg.add(f"{BASE_DIR}/logs/debug_log_{time.strftime('%Y_%m_%d')}.log",
    level="DEBUG",
    format='{time:YYYY-MM-DD HH :mm:ss.SSS} - {level} - {file} - {function} - {line} - {message}',
    rotation="00:00",  # 文件过大就会重新生成一个新文件  "12:00"# 每天12点创建新文件
    encoding="utf-8",
    enqueue=True,  # 异步写入
    serialize=False,  # 序列化为json
    retention="10 days",  # 一段时间后会清空
    compression="zip"  # 保存为zip格式
)
