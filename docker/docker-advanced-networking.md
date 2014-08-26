#### Network Configuration

Docker 默认会在宿主机创建一个名为 `docker0` 的虚拟网络接口,
它会随机选择一个宿主机上没有被使用的地址段.

`docker0` 实际上是一个虚拟网桥, 它自动将数据包转发给其它网卡以实现容器和宿主机以及容器之间的通信.
每次创建容器时, Docker 会自动创建一对 "peer" 接口就好像管道的两端,
其中一端会绑定给所创建容器的 `eth0` 上, 另一端则随机生成一个类似 `veth****` 的唯一名称保存在宿主机的 `namespace` 中.
通过绑定这些 `veth*` 到 `docker0` 网桥上来实现供容器和宿主机以及容器之间通信的虚拟网络.
可以通过 `$ sudo brctl show` 命令查看这些接口.

通过 `dockuer --help` 可以看到 `docker` 命令本身也有很多选项.
整理其中网络相关选项如下:

1. 以下参数只可以在 Docker server 启动时设置, 一旦开始运行就无法更改:
 - `-b BRIDGE`, `--bridge=BRIDGE`
 - `--bip=CIDR`
 - `-H SOCKET`, `--host=SOCKET` _此选项与容器无关, 是用来指定 Docker 接受命令的通道_
 - `--icc=true|false`
 - `--ip=IP_ADDRESS`
 - `--ip-forward=true|false`
 - `--iptables=true|false`
 - `--mtu=BYTES`
2.  以下参数可以随时指定, 可以被比如 `docker run --dns=0.0.0.0` 命令精确指定的值覆盖:
 - `--dns=IP_ADDRESS`
 - `--dns-search=DOMAIN`
3. 这里还有一些针对容器修改的参数只可以在调用 `docker run` 时指定:
 - `-h HOSTNAME`, `--hostname=HOSTNAME`
 - `--link=CONTAINER_NAME:ALIAS`
 - `--net=bridge|none|container:NAME_or_ID|host`
 - `-p SPEC`, `--publish=SPEC`
 - `-P`, `--publish-all=true|false`

#### Configuring DNS

Docker 可以使用同一个镜像为不同的容器提供各自的主机名和 DNS 配置,
其实现方法是覆盖容器中的 `/etc/hostname`, `/etc/hosts` 和 `/etc/resolv.conf` 这三个文件.
如果在容器中调用 `mount` 就会发现, 挂载的文件中会有这三个文件:

```
$ mount
[...]
/dev/disk/by-uuid/1fec...ebdf on /etc/hostname type ext4 ...
/dev/disk/by-uuid/1fec...ebdf on /etc/hosts type ext4 ...
tmpfs on /etc/resolv.conf type tmpfs ...
[...]
```

在上文提到的 `-h`/ `--hostname` 选项就是用来修改容器的 `/etc/hostname` 和 `/etc/hosts` 文件的.
但是它对于容器的修改既不会体现到 `docker ps` 中, 也不会被添加到其它容器的 `/etc/hosts` 文件中.

`--link=CONTAINER_NAME:ALIAS` 选项在 "working with multiple containers" 中简单介绍过用法,
它的原理是给容器的 `/etc/hosts` 文件一个指向 `CONTAINER_NAME` 这个容器的 IP 地址的入口 `ALIAS`.
这样新容器中的进程就可以连接到 `ALIAS` 指向的主机而不必知道其 IP 地址.

`--dns=IP_ADDRESS` 和 `--dns-search=DOMAIN` 都是用来修改容器的 `/etc/resolv.conf` 文件的,
它们分别对应 `server` 行和 `search` 行. 当容器中进程访问一个不存在于 `/etc/hosts` 中的主机名时,
则通过端口 53 访问指定的 `IP_ADDRESS` 上的地址服务;
对于搜索域的指定基本同理, 比如指定了`example.com`, 则容器进程搜索 `host` 时也会搜索 `host.example.com`.

> 默认情况下 Docker 会使用 docker daemon 所在主机上的 `/etc/resolv.conf` 中的配置.

#### Communication between containers

容器之间是否能够通信在操作系统层面上受到以下三个因素制约:
1. 默认情况下 Docker 会将所有的容器附加到 `docker0` 网桥上, 但也还是存在其它复杂的拓扑结构的,
要保证物理网络拓扑结构连接了容器的网络接口.
2. 依赖于宿主机的 `ip_forward` 参数, 该参数的值为 `1` 时表示开启转发功能. `$ sudo echo 1 > /proc/sys/net/ipv4/ip_forward`
3. 当修改 `--iptables=false` 时, Docker 不会修改系统中 `iptables` 的规则.
否则默认情况下 Docker 会在 `--icc=true` 时向 `FORWARD` 链添加 `ACCEPT` 规则, 而 `--icc=false` 时则添加 `DROP` 规则.

`iptables` 和 `--icc` 提供给我们一个很好的机制来限制容器的访问以达到安全防护的目的,
当 `--icc=false`, `--iptables=true` 时, 我们还是可以利用 `--link` 选项连接信任的容器.
此时 Docker 会添加指定容器的 `ACCEPT` 规则. 但注意与之前使用 `--link` 不同的是这样的用法需要两个容器都有暴露的端口.

#### Binding container ports to the host

默认情况下, Docker 容器可以访问外部网络, 但是外部网络却无法访问到容器.
很容就想到这也是靠 `iptables` 来实现的, 于是要想将 Docker 容器的端口映射到宿主机以提供被访问的能力自然而然也就要通过 `iptables` 来实现.
当然并不是每次创建容器都要手动去添加 `iptables` 规则, `-p port:port`/ `-P` 就帮我们完成了同样的工作.
当暴露了某个端口后, 可以在 `iptables` 的 `nat` 表中查看到相应的规则.

#### Customizing docker0

前文提到默认情况下 Docker 会创建 `docker0` 网桥来负责容器的通信.
除了网络地址外, 我们还可以指定一些额外的参数:
- `--mtu=BYTES`: 修改 "Maximum transmission unit, MTU" 最大传输单元, 默认为 1500bytes.
- `--bip=CIDR`: 指定地址给 `docker0`, 比如 `192.168.0.1/24`.

#### Building your own bridge

如果希望使用特别指定的网桥代替 `docker0`, 可以在启动 docker deamon 时使用 `-b`/ `--bridge` 选项.

```bash
# 关闭 docker daemon 并删除 docker0 网桥
service docker stop
ip link set dev docker0 down
brctl delbr docker0

# 创建新的网桥
brctl addbr bridge0
ip addr add 192.168.9.1/24 dev bridge0
ip link set dev bridge0 up

# 更新 docker 设置并启动 docker daemon
echo 'DOCKER_OPTS="--bridge=bridge0"' >> /etc/default/docker
service docker start
```
