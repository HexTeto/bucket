# MongoDB Day 14

<br>
<br>

## Shard Key Selection

如何选择一个适合的 shard key 是 sharding 中最重要也最困难的问题.
不同的 shard key 会对整个数据库性能产生非常大的影响.

#### hashed shard key

Hashed shard key 依赖于 hashed index (计算一个字段的散列值作为索引) 来分发数据.
选择一个拥有较高基数的单调递增字段作为 hashed shard key 通常是一个不错的主意,
因此像 `ObjectId` 这样的对象就非常适合作为 hashed key.

```js
db.demo.ensureIndex({"_id": "hashed"})
sh.shardCollection("app.demo", {"_id": "hashed"})
// { "collectionsharded" : "app.demo", "ok" : 1 }
```

如果在一个空的集合上使用 hashed key 创建分片, MongoDB 会自动创建并迁移一些空文件块使每个分片都持有两个空文件块.
这个过程可以通过 `sh.shardCollection()` 的 `numInitialChunks` 参数来控制初始的文件块数量.
该参数必须传递一个小于 `8192` 的值, 且如果集合非空则该参数不会产生任何效果.

```js
db.runCommand({"shardCollection": "app.demo", "key": {"_id": "hashed"}, "numInitialChunks": 4})
```

注意使用 hashed shard key 时会有一些限制:
- 不能够使用 `unique` 参数
- 不能选择数组字段
- 计算浮点数的散列值时, 浮点数会先被取整, 所以 `1` 和 `1.99` 得到的散列值是相同的
- 不能够使用大于 `2^53` 的浮点数

#### shard key on GridFS

在 GridFS 中, 因为 GridFS 本身就会将文件分块, 而 sharding 也会将集合分块, 同样是 "chunks" 要注意二者区别.

对于 GridFS 的 `files` 集合, 通常该集合很小, 因为它仅用来存储元数据, 所以分片对于它来说并不是必须的.
如果一定要对其分片, 应搭配 `_id` 字段. 对于生产环境, `files` 集合应该保证被存放在一个 replica set 中.

对于 `chunks` 集合, 它目前只支持 `{files_id: 1, n: 1}` 和 `{files_id: 1}`

```js
db.fs.chunks.ensureIndex({"files_id": 1, "n": 1})
db.runCommand({"shardCollection": "app.fs.chunks", "key": {"files_id": 1, "n": 1}})
// or
db.runCommand({"shardCollection": "app.fs.chunks", "key": {"files_id": 1}})
```

#### shard tag

利用标签可以关联 shard key 的一定范围内的块到特定分片或其子集.

在连接到 `mongos` 后, 可以使用 `sh.addShardTag()` 和 `sh.removeShardTag()` 来给指定分片添加或移除标签.
一个分片可以拥有多个标签, 多个分片也可以拥有相同的标签.

```js
// add tag
sh.addShardTag("sh0", "nrt")
sh.addShardTag("sh0", "nyc")
sh.addShardTag("sh1", "sfo")
// remove tag
sh.removeShardTag("sh0", "nrt")
```

对于拥有了标签的分片, 可以使用 `sh.addTagRange()` 方法将一个 shard key 中特定范围内的文件块分配给指定分片.
给定 shard key 的某个范围只能分配给它一个标签, 范围定义之间不能有重叠, 且不可多次标记相同的范围.
边界的定义同样是包括 lower boundary 但是不包含 upper boundary.

```js
sh.addTagRange("app.users", {"zipcode": "10001"}, {"zipcode": "10281"}, "nyc")
sh.addTagRange("app.users", {"zipcode": "11201"}, {"zipcode": "11240"}, "nyc")
sh.addTagRange("app.users", {"zipcode": "94102"}, {"zipcode": "94135"}, "sfo")
```

一个 shard key range 是不能通过辅助函数来删除的, 如果要移除一个范围就必须到 `config.tags` 这个集合中删除对应的文档.

```js
use config
db.tags.remove({"_id": {"ns": "app.users", "min": {"zipcode": "10001"}}, "tag": "nyc"})
```

<br>

## Administration

集群所有相关的配置信息都会保存在配置服务器上 `config` 数据库的集合中.
正常情况下永远不应该直接访问这个数据库中的数据. 应该连接到 `mongos`, 然后在访问 `config` 数据库.
通过 `mongos` 修改的配置数据将同步到所有的配置服务器, 同时还可以有效防止危险操作.

在 `config` 下有若干集合分别存储不同的配置信息:

- `config.shards` 记录所有分片的信息
  ```js
  db.shards.findOne()
  {
      "_id": "replSetName",
      "host": "replSetName/server-1:27017, server-2:27017, server-3:27017",
      "tags": [
          "us-east",
          "64gbm",
          "cpu3"
      ]
  }
  ```
  分片的 `_id` 来自于副本集名称, 所以集群中副本集名称必须是唯一的.
- `config.databases` 记录数据库信息, 包括没有被分片的数据库
  ```js
  db.databases.findOne()
  {"_id": "admin", "partitioned": true, "primary": "config"}
  {"_id": "app", "partitioned": true, "primary": "sh0"}
  ```
  如果在数据库上启用了分片, `partitioned` 值为 `true`;
  `primary` 的值为 primary shard.
- `config.collections` 记录所有所有分片集合的信息, 不包括没有分片的集合.
  ```js
  db.collections.findOne()
  {
      "_id": "app.demo",
      "lastmod": ISODate("1970-01-16T17:53:52.934Z"),
      "dropped": false,
      "key": {"x": 1, "y": 1},
      "unique": true
  }
  ```
  该集合中文档的 `_id` 字段为集合的完整命名空间; `key` 为 shard key.
- `config.chunks` 记录文件块信息
  ```js
  {
      "_id": "app.hashy-user_id_-1034308116544453153",
      "lastmod": {"t": 5000, "i": 50},
      "lastmodEpoch": ObjectId("50f5c648866900ccb6ed7c88"),
      "ns": "app.hashy",
      "min": {"user_id": NumberLong("-1034308116544453153")},
      "max": {"user_id": NumberLong("-732765964052501510")},
      "shard": "app-rs1"
  }
  ```
  该集合中 `ns` 的为文件块所属的集合的完整命名空间; `lastmod` 和 `lastmodEpoch` 记录文件块版本,
  其中键 `t` 和 `i` 分别表示 "major" 和 "minor" 两个版本: 主版本在块迁移至新分片时改变, 副版本在块拆分时改变
- 出上边列出的集合, 还有已经学习过的 `config.settings`, `config.tags` 和 `config.changelog`.

#### network connection

一个 shard cluster 内存在大量的网络连接, 要查看 `mongos` 和 `mongod` 之间的连接信息,
可以在分片集群内的任意 `mongos` 或 `mongod` 上使用 `db.adminCommand({"connPoolStats": 1})`.

当有客户端连接到 `mongos` 时, `mongos` 会创建一个连接, 该连接应至少连接到一个分片上,
以便将客户端请求发送给分片. 因此, 每个连接到 `mongos` 的客户端都会至少产生一个 `from mongos to shard` 的连接.
那么如果有更多的 `mongos` 进程时, 就会产生更多的连接, MongoDB 显然不会允许连接数量无限增长.
当前版本默认每个 `mongos` 和 `mongod` 进程最多允许 `20000` 个连接, 我们可以配置 `maxConns` 参数来定义最大连接数.
如何计算一个适合的最大连接限制可以参考以下公式:

```
maxConns = 2000 - (numMongos * 3) - (numMembers * 3) - others
```

- `numMongos`: 每个 `mongos` 进程会创建 3 个连接, 他们分别用于转发客户端请求, 监控副本集状态和追踪错误信息.
- `numMembers`: primary 会向每个 secondary 创建 1 个连接, 每个 secondary 会向 primary 创建 2 个连接.
- `others`: 通常除了主要应用外, 还会存在少量其它连接, 比如管理员用 shell 登录到集群.

`maxConns` 只会阻止 `mongos` 创建过多的连接, 但不会解决连接耗尽的问题.
一旦连接耗尽, 请求就会发生阻塞等待有连接被释放. 因此必须防止应用程序使用超过 `maxConns` 数量的连接,
尤其是在 `mongos` 进程数量不断增加时更需要严密的监控手段来保障.

MongoDB 实例在正常退出时会关闭所有连接, 已经连接到 MongoDB 的成员会立即收到 `socket error` 并刷新连接.
但是如果 MongoDB 实例由于断电或网络原因等问题导致意外离线, 则可能不会主动断开 `socket` 会话.
此时集群内其它成员很可能会认为这个实例仍在正常运行, 但当试图在该实例上进行操作时就会遇到错误继而刷新连接.
连接数量较少时, 可以快速检测到某个实例已离线, 但存在大量连接时, 每个连接都要经历尝试操作检测到失败后重连接的过程,
而此过程也会产生大量的错误. 对于这种大规模的重连接过程, 除了重启进程外没有其它行之有效的解决方案.

#### remove shards

通常来说是不应该删除分片的. 如果经常在集群中添加和删除分片会给系统带来很多不必要的压力.
如果存在删除分片的必要, 首先要确保 balancer 处于开启状态.
在数据排出的过程中, balancer 会自动将待删除分片上的数据迁移至其它分片.
将要删除的分片名称作为参数传给 `removeShard` 命令就会启动数据排出流程.

```js
db.adminCommand({"removeShard" : "sh_demo"})

{
    "msg" : "draining started successfully",
    "state" : "started",
    "shard" : "sh_demo",
    "note" : "you need to drop or movePrimary these databases",
    "dbsToMove" : [
        "blog",
        "music",
        "prod"
    ],
    "ok" : 1
}

// 可以随时再次执行命令查看数据排出的进度

db.adminCommand({"removeShard" : "sh_demo"})

{
    "msg" : "draining ongoing",
    "state" : "ongoing",
    "remaining" : {
        "chunks" : NumberLong(5),
        "dbs" : NumberLong(0)
    },
    "ok" : 1
}
```

如果分片上存在的文件块数量较多或体积较大, 排除数据的过程可能会非常耗时.
如果存在特大块 "jumbo chunk", 可能需要临时提高其它分片的块大小一边能够将其迁移至其它分片.

此外文件块在移动前可能会被拆分, 所以有可能会看到系统中的块数量在排出数据时发生了增长.
比如对于下面这个例子:

```
sh0    10
sh1    10
sh2    10
sh3    11
sh4    11
```

移动前该集群共有 52 个块, 如果删除 `sh3`, 其结果可能是:

```
sh0    15
sh1    15
sh2    15
sh4    15
```

块数量变为 60, 其中 18 个来自 `sh3`, 即有 7 个块是在数据排出时被拆分出来的.

所有的文件块都完成迁移后, 如果仍有数据库将待移除分片作为 primary shard 则需要先将这些数据库移除.
这一步骤并非是必须的, 但是可以确保确实完成了分片的删除. 如果不存在将该分片作为 primary shard 的数据库,
则块迁移完成后即可看到分片删除成功的返回信息.

```js
db.adminCommand({"movePrimary" : "blog", "to" : "sh4"})

{
    "msg" : "removeshard completed successfully",
    "state" : "completed",
    "shard" : "sh4",
    "ok" : 1
}
```

#### modify config servers

> 需要注意, 对于 config servers 的任何修改首先都必须做好备份工作.

对于正常运行的集群, 所有的 `mongos` 进程的 `--configdb` 选项都必须是一致的.
因此要修改 config servers 就必须先关闭所有的 `mongos` 进程, 在完成修改后再传递新的配置重启所有实例.

#### balance

通常来说, MongoDB 会自动完成 balance 的过程.
但是在某些情况下, 比如进行数据库管理操作时, 应该使用 `sh.setBalancerState(false)` 暂时关闭 balancer
以保证系统不会自动启动均衡过程. 但处于执行状态的过程是无法立即终止的,
可以检查 `config.locks` 集合查看是否还存在进行中的均衡过程.

均衡过程会增加系统负载, 尤其是当使用热点 shard key 单点处理写入操作以及集群中添加新分片时, 大量的迁移过程会使负载上升明显.
一种有效的方式是通过修改 `config.settings` 集合来人为设定周期任务以控制均衡发生的时间.

```js
db.settings.update({"_id": "balancer"}, {"$set":{"activeWindow": {"start": "03:00", "stop": "07:00"}}}, true)
```

上面这个例子指定均衡过程只能在凌晨 `03:00 ~ 07:00` 这个时间段触发.

#### avoid jumbo chunk

文件块中可能没有文档, 也可能存在上百万个文档. 通常越大的文件块迁移速度就越慢,
过大的块在迁移时经常会收到拒绝信息 `chunkTooBig`. 这是因为迁移的块已经超过了系统设定的大小限制.

```js
// 访问 config.settings 集合将 chunksize 调整为 32MB
use config
db.settings.find({"_id": "chunksize"})

/*
{
    "_id" : "chunksize",
    "value" : 24
}
*/

db.settings.save({"_id": "chunksize", "value": 32})

// 尝试迁移文件块
sh.moveChunk("app.users", {"user_id": NumberLong("12345")}, "sh0")

/*
{
    "cause" : {
        "chunkTooBig" : true,
        "estimatedChunkSize" : 4814960,
        "ok" : 0,
        "errmsg" : "chunk too big to move"
    },
    "ok" : 0,
    "errmsg" : "move failed"
}
*/

// 因为该块过大, 需要手动拆分
use chunks
db.chunks.find({"ns": "app.users", "min.user_id": NumberLong("56789")})
/*
{
    "_id" : "app.users-user_id_NumberLong(\"56789\")",
    "ns" : "app.users",
    "min" : { "user_id" : NumberLong("56789") },
    "max"  : { "user_id" : NumberLong("99999") },
    "shard" : "sh1"
}
*/
sh.splitAt("app.users", {"user_id": NumberLong("76543")})
```

通常大部分文件块都可以通过调高 `chunksize` 并拆分为多个小块来进行迁移, 不过还是应该尽可能将大块拆分为更多的小块.
尽管如此, 还是会存在一个过大的文件块不能被拆分这样的情况, 这种块就称之巨大块 ("jumbo chunk").

举个例子, 比如以精确到天的日期作为 shard key 时, 就意味着一天只会创建一个块. 如果单日内出现应用产生大量数据的情况,
就会存在一个明显比普通块要大的块, 且因为它内部所有文档的 shard key 都持有一样的值, 所以该块将无法拆分.
一旦这个块超过了 `chunksize` 的大小, balancer 就无法正常移动它, 要解决这种问题是非常费时费力的.

通常出现巨大块时, 某分片的体积就会明显比其它分块增长得快得多.
通过 `sh.status()` 查看分片状态会发现一旦出现巨大块, 它就会被标记为 `jumbo`.

```js
// connect to mongos and find out the jumbo chunk
sh.status(true)
// disable the balancer process
sh.setBalancerState(false)
// temporary raise chunksize larger than the biggest jumbo chunk
use config
db.settings.findOne({"_id": "chunksize"})
db.settings.save({"_id": "chunksize", "value": 10000})
// use either sh.splitAt() or sh.splitFind() to split the jumbo chunk
sh.splitAt("app.demo", {"x": 3})
db.adminCommand({"moveChunk": "app.demo", "find": {"x": 3}, "to": "sh0", "secondaryThrottle": true})
// resetting chunksize and restart balancer
db.settings.save({"_id": "chunksize", "value": 24})
db.setBalancerState(true)
```

文档中还有另一种更便捷的方法:

```js
sh.setBalancerState(false)
// unset the jumbo flag for the jumbo chunk in config.chunks collection.
db.getSiblingDB("config").chunks.update({"ns": "app.demo", "min": {"x": 3}, "jumbo": true}, {"$unset": {"jumbo": ""}})
sh.setBalancerState(true)
// optional. clear current cluster meta information.
db.adminCommand({"flushRouterConfig": 1})
```

无论何种方法, 一定要先记得备份 `config` 数据库.

```sh
mongodump --db config --port $config_server_port --out $output_file
```

随着集群规模不断扩大, 修复 jumbo chunk 的复杂程度越来越高, 因此应设法尽可能避免产生 jumbo chunk.
根据前边的分析, 我们知道比较常见的导致巨大块出现的原因是 shard key 选择不合理.
在设计 shard key 时, 应尽可能细化粒度, 最优情况是保证每个文档在该字段上都拥有唯一值,
虽然很多情况下不能满足最优情况, 但也至少应该保证 shard key 字段的某个值所包括的数据不要超过 `chunksize` 限制.
