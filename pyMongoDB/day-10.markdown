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

依次启动副本集成员:

```js
rs.initiate()
```

使用 `rs.conf()` 得到副本集配置信息如下:

```json
{
    "_id" : "rs0",
    "version" : 1,
    "members" : [
        {
            "_id" : 1,
            "host" : "rs0.mdb.org:27017"
        }
    ]
}
```

可以看到, 目前 `members` 字段中已经存在了当前节点, 使用 `rs.add()` 继续添加其它节点:

```js
rs.add("rs1.mdb.org")
rs.add("rs2.mdb.org")
```

完成添加后, `rs.status()` 可以获得当前副本集状态信息.
