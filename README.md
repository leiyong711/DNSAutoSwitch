# DNSAutoSwitch
OpenWRT 容灾 自动切换主路由DNS

###网络拓扑
```python
一级路由器 电信光猫
    二级路由器 TL-WDR7660千兆版
        OpenWRT 服务器
        检查脚本
```

###所用到第三方库
```python
tcping
loguru
requests
```
