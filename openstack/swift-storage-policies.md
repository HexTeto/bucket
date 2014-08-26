##Introducing Storage Policies

在大规模部署中, 用户往往希望数据不是简单的随机分布在整个集群中的.
他们可能需要一部分特定数据存储在快速的SSD设备中,
一部分数据存储在不同的数据中心或者地区,
还有一些数据可能会需要不同的存储后端.

应对这种需求, 在刚刚发布的Swift2.0版本中, 存储策略的定制包括:

1. 根据用户对数据持久性和可用性的需求来定义复制级别
2. 根据用户对成本和性能的需求使用不同的存储设备
3. 控制数据存储在特定的地区或数据中心

我们知道在Swift中,集群通过构建3个散列环(Ring)来映射数据的存储位置, 它们包括:

- account-ring
- container-ring
- object-ring

在1.x版本中, 一个存储策略只允许存在一个对象环, 它们是完全一致的.
在2.0版本中通过"Storage Policies"允许在一个存储策略下定义多个对象环,
从而使一个单一集群内可以存在多个独立的对象存储以实现刚才提到的三个主要功能:

1. Different levels of replication: 在一个集群内实现不同的副本策略.
2. Performance: 根据存储设备划分多个对象环, 比如SSD-only object ring.
3. Collecting nodes into group: 可以根据区域或机房划分不同的对象环, 从而使数据始终保持在指定区域或数据中心(和affinity原理不同, affinity可以配合使用精确控制数据副本存储在独立的故障域内).
4. Different Storage implementations: 允许兼容多个不同的后端存储架构.

##Adding a new Storage Policy

每个存储策略都通过`[storage-policy:{n}]`来定义, "n"即为该策略的"storage policy index".
Swift识别策略只依赖于这些索引标号而不依赖于策略名称. 定义它们时需遵循以下规则:

- 如果`[storage-policy:0]`未声明的并且没有其它策略存在, Swift将自动生成一个默认策略.
- "storage policy index"必须是一个__非负整数__.
- 如果没有定义默认策略, 则默认使用`[storage-policy:0]`.
- 所有的策略索引值必须是唯一的.
- 必须定义策略名称`name={...}`; 名称不区分大小写; 只能包含字母, 数字或"-".
- 策略名称必须是唯一的.
- 策略名"Policy-0"只能用于`[storage-policy:0]`.
- 存在多个策略是必须要声明其中一个为缺省值.
- `deprecated`和`default`不能被同时定义在一个策略中.
- __一旦一条存储策略生效, 它的"storage policy index"就不可再更改了.__

####How-To

假设有两个位于不同地区的数据中心, 它们使用"geo-replicated setup",
即至少会有一个副本存储在不同的数据中心里.
如果需要将所有的数据规定只存储在各自临近的数据中心内, 就需要创建两个新的环对应两个数据中心,
它只包括目标数据中心内的节点:

- 原有的默认环, 包括两个数据中心内的所有节点.
- 新创建的环, 只包括数据中心A内的节点.
- 新创建的环, 只包括数据中心B内的节点.

__Ⅰ. 添加存储策略__

编辑`/etc/swift/swift.conf`:

```
[storage-policy:0]
name = original
default = yes

[storage-policy:1]    // 用于数据中心A的新策略
name = A

[storage-policy:2]    // 用于数据中心B的新策略
name = B
```

__Ⅱ. 构建环__

```
swift-ring-builder object-1.builder create 18 3 1
swift-ring-builder object-2.builder create 10 2 1
swift-ring-builder object-1.builder add z1-10.0.0.1:6000R10.0.1.1:6003/sdb1 100
swift-ring-builder object-2.builder add z2-10.0.0.2:6000R10.0.1.2:6003/sdb1 100
swift-ring-builder object-1.builder rebalance
swift-ring-builder object-2.builder rebalance
```

复制`object-1.ring.gz`和`object-2.ring.gz`到它们各自对应的节点中.

__Ⅲ. 创建容器(假设dA=beijing, dB=shanghai. PUT和POST方法都可以):__

```
swift -H "X-Storage-Policy: A" post beijing
swift -H "X-Storage-Policy: B" post shanghai
```

__Ⅳ. 通过`swift stat`来验证策略是否生效:__

```
$ swift stat beijing
[...]
X-Storage-Policy: A

$ swift stat shanghai
[...]
X-Storage-Policy: B
```

##Deprecating Policies

同样还是修改`/etc/swift/swift.conf`:

```
[storage-policy:0]
name = original
deprecated = yes        // 弃用该策略

[storage-policy:1]
name = A
default = yes           // 该策略设为默认

[storage-policy:2]
name = B
```

####对于弃用的策略:

弃用策略中已经存在的容器并不会丢失, PUT/GET/DELETE/POST/HEAD方法依旧可用.
但试图使用弃用的策略创建新的容器会返回"400 Bad Request".
