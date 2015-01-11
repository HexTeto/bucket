# MongoDB Day 10

<br>
<br>

[deploy-arch]:http://docs.mongodb.org/manual/core/replica-set-architectures/
[conf-opt]:http://docs.mongodb.org/manual/reference/configuration-options/

## Replication

在 MongoDB 中定义一个 "replica set" 为一组存储相同数据的 `mongod` 实例的集合.
其中 "primary" 接受来自客户端的写请求, 其它所有实例称为 "secondaries" 作为数据副本.
和其它数据库类似, 当主数据库离线, 会自动从副本集中提升一个节点成为新的主数据库.
副本集为从主数据库发送的读请求提供严格一致性 (strict consistency).

#### Deployment

通常来说, "一备二" 的模式所提供的冗余能力已经可以满足大多数应用场景, 也足以支撑分布式的读操作.
更多的架构方案参考 [replica set deployment architectures][deploy-arch].

实验中三个节点分别作如下配置

```json
{ "host": ["rs0", "rs0.mdb.org"], "addr": "10.10.10.10" }
{ "host": ["rs1", "rs1.mdb.org"], "addr": "10.10.10.11" }
{ "host": ["rs2", "rs2.mdb.org"], "addr": "10.10.10.12" }
```

首先为每个成员节点进行相关配置, 完整参数配置参考文档 [configuration file options][conf-opt].
副本集可以通过 `new ReplSetTest({"nodes": <num>})` 或 `mongod --replSet <name>`
两种不同的方式来部署, 因为官方文档中已经有关于 `mongod` 的介绍, 笔记记录第一种方式部署.

1. 使用 `mongo --nodb` 在不连接任何数据库的情况下登录 shell;
2. 通过 `replSet = new ReplSetTest({"nodes": 3})` 创建一个包含 3 个节点的副本集;
3. 启动 3 个 `mongod` 进程 `replSet.startSet()`;
4. 配置副本集 `replSet.initiate()`;

至此副本集实例就已经启动了, 在创建副本集后会返回相关信息,
其中可以找到 3 个 `mongod` 实例各自运行的端口, 默认情况下是从 `31000` 开始递增.
此时连接到运行在 `31000` 的实例, 就已经可以看到 shell 提示符变成了 `testReplSet:PRIMARY>`.
它们分别表示了副本集名称和当前成员状态.

连接其中一个成员, 可以通过 `db.isMaster()` 获取副本集相关信息:

```js
conn = new Mongo("rs0:31000")
pdb = conn.getDB("test")
pdb.isMaster()
/*
{
    "setName" : "testReplSet",
    "ismaster" : true,
    "secondary" : false,
    "hosts" : [
      "rs1:31001"
      "rs2:31002"
    ],
    "primary" : "rs0:31000",
    "me" : "rs0:31000",
    "maxBsonObjectSize" : 1677216,
    "localTime" : ISODate("2015-01-12T02:42:53.031Z"),
    "ok" : 1
}
*/
```

从返回结果中可以看到, 当前连接到的恰好就是主数据库, 副本集中其它成员还有 `rs1, rs2`.
我们测试一些写入操作观察结果.

```js
// 插入 1000 个文档
for (i=0; i<1000; i++) {
    pdb.demo.insert({"count": i})
}
// 检查集合内文档数量
pdb.demo.count()
// 1000
// 连接至任意 secondary 上检查刚才的写入是否同步
conn1 = new Mongo("rs1:31001")
sdb = conn1.getDB("test")
sdb.demo.find()
// error: { "$err" : "not master and slaveok=false", "code" : 13435 }
// 返回错误是因为 MongoDB 为了防止 secondaries 拿到未同步的过期数据默认拒绝查询.
// 因此要从备份节点上直接读取数据需要先对 sdb 这个连接设置 slaveok=true.
sdb.setSlaveOk()
sdb.demo.find()
/*
{ "_id" : ObjectId(...), "count" : 0 }
{ "_id" : ObjectId(...), "count" : 1 }
......
如果备份已经结束, 就可以获得相应结果.
当然也可能由于数据还尚未备份完成而得不到结果.
*/

// 关闭位于 rs0 的主数据库以模拟主节点离线
pdb.adminCommand({"shutdown" : 1})
sdb.isMaster()
/*
此时从返回结果中就可以看到 "primary" 字段已经指向了 "rs1:31001".
*/
```

实验结束, 返回配置副本集使用的 shell 执行 `replSet.stopSet()` 关闭副本集.
