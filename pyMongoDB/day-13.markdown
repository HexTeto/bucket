# MongoDB Day 13

<br>
<br>

## Sharding

分片用来将数据拆分以便于分散存放在不同节点上.
这样的存储方式使我们可以用更廉价的服务器就能够部署大规模的数据集, 并提供更高的吞吐量.
每一个分片都可以作为一个独立的副本集存在.

决定何时分片是一个值得权衡的问题, 分片要求做出设计决策, 一旦决定后整个数据库部署就很难再变动.
系统运行很长一段时间积累了大量数据后再进行分片也是不明智的, 因为在一个过载系统上不停机进行分片非常困难.
通常分片被用来:
- 增加可用内存
- 增加可用空间
- 减轻单台服务器负载
- 处理单个 `mongod` 实例无法承受的数据吞吐

因此, 良好的监控对于决定应该何时进行分片是十分重要的.
随着分片数量不断增加, 系统性能会线性增长. 但如果一个尚未分片的系统创建了少量分片,
则此时性能通常会有所下降. 由于迁移速度, 维护元数据, 路由等开销,
仅包含少量分片的系统相当于额外增加了服务器的工作量, 因此至少应该要创建 3 个以上的分片.

#### shared cluster components

一个 shared cluster 由以下几个部分组成:
- shards : 一个 `mongod` 实例, 它持有集合中数据的某个子集.
- config servers : 一个 `mongod` 实例, 它持有分片集群的元数据. 这些元数据用来映射 chunks 到 shards.
- routing instances : 一个 `mongod` 实例, 它接受读写请求并将其路由到目标分片.

注意区分 shards 和 replica set 的区别, shards 是用多台服务器存储一个数据实体的不同子集,
而 replica set 是用多台服务器存储相同的数据. 所以每一个 shard 都可以组成一个 replica set.

<br>

## Tutorials

#### start the config server database instances

首先为所有的 config server 创建数据目录, 默认情况下为 `/data/configdb`.

```sh
mkdir /data/configdb
```

之后启动所有 config server 实例:

```sh
mongod --configsvr --dbpath /data/configdb --port 27019
```

#### start the mongos instances

启动 `mongos` 实例, 并指定 `--configdb <configDB string>` 参数连接到 config server 实例.
注意当有多个 `mongos` 实例时, 必须保持 `configDB` 顺序一致.

```sh
mongos --configdb sh0.mdb.org:27019,sh1.mdb.org:27019,sh2.mdb.org:27019
```

#### add shards to the cluster

如果 shard 是一个 replica set, 则必须按照 `<replName>/<member0>, <member1>, ... <memberX>`
的格式指定所有副本集成员.

```js
sh.addShard("rs/rs0.mdb.org:27017, rs1.mdb.org:27017, rs2.mdb.org:27017")
```

#### enable sharding for a database

首先连接到已经启动的的 `mongos` 实例.

```sh
mongo --host <hostname of machine running mongos> --port <port mongos listens on>
```

然后使用 `sh.enableSharding(dbName)` 指定要启动分片的数据库.

```js
sh.enableSharding("demo")
// or
db.runCommand( {enableSharding : demo } )
```

数据库启动分片功能后, 此时就已经存在了一个 "primary shard", 它持有目前数据库中所有数据.

#### enable sharding for a collection

对集合进行分片使用 `sh.shardCollection("dbName.collection", shard-key-pattern)` 函数.

```js
sh.shardCollection("demo.users", {"id": 1, "name": 1})
```

从上边的例子看到字符串 `dbName.collection` 是要启动分片的集合和它所属数据库的完整名称.
`shard-key-pattern` 从格式上看是一个索引,
在这里它表示将根据 `id` 字段的值来分发文档到不同的块,
如果有若干文档拥有相同的值, 则再根据 `name` 字段的值来分割文档.
也可以指定 `{"_id" : "hashed"}` 这样的 shard key 来计算唯一值.

注意对于已有数据的集合, 如果不存在和 shard key 相同的索引, 则必须使用 `ensureIndex()`
创建一个对应的索引. 而对于空的集合, 创建索引的过程会自动在 `sh.shardCollection()` 中完成.
具体关于如何选择一个适合的 `shard-key-pattern`, 见 `Day 14`.

<br>

## Sharding Mechanics

#### chunk

MongoDB 会根据给定的 shard key 将文档分组为若干 "chunks",
每一个 chunk 都包含一组满足 shard key 条件的文档,
这样就使得 MongoDB 可以用一个比较小的表来维护 chunks 和 shards 的映射.

例如, 集合 `users` 有 `{ "age" : 1 }` 这样一个 shard key,
其中某 chunk 的值范围为 `chunk0 = {"age": [range(1, 10)]}`.
那么比如 `db.users.find({"age": 5})` 这样一个查询, 它就会被路由到 `chunk0` 这个 chunk 所在的 shard.

在 sharding 中, 一个文档只属于一个唯一的 chunk, 这就意味着 shard key 不能是一个值为数组的字段.

#### chunk range

一个新的分片只有一个块, 它包含所有的文档. 随着通过 shard key 不断划分或 MongoDB 的自动分割,
chunk 的数量会不断增长. 块的描述信息保存在 `config.chunks` 集合中.
可以在 shell 中使用 `db.chunks.find(<criteria>, {"min": 1, "max": 1})` 查看该集合内容.
其中的 `min` 和 `max` 字段就保存了每个 chunk 分割的范围.

```json
{
    "_id": "demo.users-age_1.0",
    "min": {"age": 1},
    "max": {"age": 6}
}

{
    "_id": "demo.users-age_6.0",
    "min": {"age": 6},
    "max": {"age": 11}
}
```

对于上边这个例子, 可以看到在第一个文档中的上限和第二个文档中的下限是相同的值,
这并不是分割错误, 它们分别表示的区间为 `[1, 6)` 和 `[6, 11)`. 称 `6` 这个值为 "split point".

当使用 compound shards 时, 它的工作方式和 compound indexes 相似.
需要注意的是就像使用索引排序时一样, 字段的顺序是很重要的.
比如对于 `{"username": 1, "age": 1}` 这样一个 shard key, 首先使用 `username` 查询会很快,
而首先使用 `age` 查询则会很慢, 要根据 `age` 查询则需要相反的 shard key `{"age": 1, "username": 1}`.

#### chunk split

`mongos` 会记录每个块中有多少数据, 一旦超过 `chunksize` 的限制, 就会自动将其拆分为两个小块.
块的拆分只需要改变其元数据, 数据实体无需移动.
默认情况下 `chunksize` 的大小限制为 `64MB`, 这个配置信息保存在 `config.settings` 集合里,
可以通过修改它的值来变更限制, 范围接受 `[1, 1024] MB`.

```js
use config
db.settings.save({"_id": "chunksize", value: 256})
```

修改 `chunksize` 有一些需要注意的地方:
- 通过 `--chunkSize` 参数修改块尺寸无法作用于已经初始化的集群.
- MongoDB 只会在接受插入或更新操作时才会触发自动分割行为.
- 如果要增加块尺寸, 已有的文件块只会随着插入或更新而继续增长.
- 如果要缩小块尺寸, 可能会需要一段时间来重新分配所有文件块的大小.
- 分割操作不能撤销.
- 当一个文件块中的文档过多时它将无法被移动.

#### cluster balancer

为了防止出现数据分配过于不均, MongoDB 使用 `balancer` 来周期性地检查分片间是否存在不平衡,
并迁移那些分配不均的数据, 使所有数据可以尽量平均分布到成员节点.

虽然通常 `balancer` 被认为是一个单独的实体, 但是 `mongos` 有时候也会扮演 `balancer` 的角色.
任何一个 `mongos` 实例都可以启动一个 "balancing round". 它会检查是否存在活动的 `balancer`,
如果没有其它可用的 `balancer` 则 `mongos` 就会对集群加锁暂时阻止配置服务器对集群的修改行为,
然后执行一次平衡操作. 整个平衡过程不会影响 `mongos` 的正常路由功能, 所以客户端方面不会受到影响.

文件块的迁移过程多少都会有一定的资源开销, 因此 `balancer` 进程做了一些限制来尽可能降低其对数据库性能的影响:
- 同一时间只会移动一个文件块
- 块迁移只有在文件块最多的分片集合和文件块最少的分片集合之间相差超过一定阈值时才会触发.
