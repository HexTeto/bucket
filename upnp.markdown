## UPnP

[Universal Plug and Play (UPnP)][upnp] 是由 [The UPnP Forum][forum] 推广的一组网络协议.
该协议的目标是使网络中的设备能够互相无缝建立连接, 并简化相关网络的实现.

UPnP 工作流程有:
- Addressing

  UPnP网络实现的基础依赖于 TCP/IP 协议, 所以每个设备都需要实现一个 DHCP Client 以自动获取 IP 地址.

- Discovery

  当网络中某个设备获取到了有效 IP 地址, 则会通过 [Simple Service Discovery Protocol, (SSDP)][ssdp]
  将自己的基础信息 (网路位置, 标识符, etc.) 发送到网络中的控制器节点.

- Description

  网络控制节点发现了一台设备后, 它将会通过发现过程中设备发送的信息中所包含的网络位置去寻找该设备的描述信息.
  UPnP 的设备描述信息使用 XML 描述, 设备描述文档除了包括制造商相关信息外, 还包括对设备内嵌所有服务的描述,
  该文档的主要作用是描述设备能够响应的各种命令, 参数等信息.

- Control

  了解了设备可以执行的行为后, 控制节点

- Event Notification



- Presentation


[upnp]:http://en.wikipedia.org/wiki/Universal_Plug_and_Play
[forum]:http://www.upnp.org/
[ssdp]:http://en.wikipedia.org/wiki/Simple_Service_Discovery_Protocol
