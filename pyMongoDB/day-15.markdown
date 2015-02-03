# MongoDB Day 15

<br>
<br>

[curop]:http://docs.mongodb.org/manual/reference/method/db.currentOp/#db.currentOp
[slowms]:http://docs.mongodb.org/manual/tutorial/manage-the-database-profiler/#database-profiling-specify-slowms-threshold

## Monitoring and Analysis

#### check current operations

在进行性能分析时, 先看一看当前正在进行的操作不失为一种简单有效的方法.
可以使用 `db.currentOp()` 查看正在进行中的操作,
参考[文档][curop]我们可以使用一般查询语句来过滤条件以找出影响性能的操作.
比如下面这个例子会查找 `app.demo` 中所有运行时间超过 5 秒的操作:

```js
db.currentOp({"active": true, "secs_running": {"$gt": 5}, "ns": "app.demo"})
```

#### terminates an operation

当想要终止一个操作时, 可以通过 `db.currentOp()` 返回目标操作的 `opid` 字段,
然后将其作为参数传递给 `db.killOp(<opid>)` 来终止操作.
注意使用 `db.killOp()` 时应该只用它来终止客户端发起的操作, 而永远不要终止数据库的内部操作.

此外并非所有的操作都能被终止. 正占用锁或等待其它操作交出锁的操作通常是无法终止的.

#### system profiler

比起 `db.currentOp()`, 系统分析器可以反馈关于耗时操作更详尽的信息, 但同时会带来更高的系统负载.
因此, 通常只需要定期使用系统分析器对操作进行分析.

默认情况下系统分析器处于关闭状态, 在 shell 中执行 `db.setProfilingLevel(<was>, <slowms=100>)` 来开启分析器.
参数 `was` 为监控级别, 接收下面三个整形参数:
- `0`, 关闭分析器.
- `1`, 只记录执行时间超过 `100ms` 的缓慢操作, 可以通过 `slowms` 参数修改, [参考文档][slowms]
- `2`, 收集所有信息.

```js
db.getProfilingStatus() // > { "was" : 0, "slowms" : 100 }
db.setProfilingLevel(2, 300) // > { "was" : 0, "slowms" : 100, "ok" : 1 }
db.getProfilingStatus() // > { "was" : 0, "slowms" : 300 }
```

注意通常情况下不要将 `slowms` 的值设定过小, 即使 profiler 处于 `0` 时该阈值依旧会对 `mongod` 产生影响,
因为它决定了哪些操作将被视为 "缓慢操作" 而记录到日志中.

当不存在 `system.profile` 集合时, MongoDB 会自动为它创建一个固定集合, 如果该集合的大小不能满足记录要求,
则需要关闭系统分析器后将该集合删除并重新创建一个同名的固定集合.

#### space consumption

查询文档占用的磁盘空间大小:

```js
Object.bsonsize({"_id": ObjectId(12345)})
Object.bsonsize(db.demo.findOne())
```

该方法的参数只要可以指向文档, 并不限制是什么特定类型. 它会返回文档在磁盘上占用的字节数 (bytes),
但并不包括随之产生的 padding 和 indexes 所占用的空间.

查询集合则使用之前使用过的 `db.collection.stats()` 方法返回集合信息,
它会返回集合的主要信息, 其中 `size == avgObjSize * count`, `size` 即集合中每个文档的 `bsonsize` 之和,
它与 `avgObjSize` 平均对象大小与对象数量之积相等. 同样的, `size` 并不是集合实际的大小,
在返回信息中还会有 `storageSize` 字段, 它反映的就是将文档和索引等所有数据相加之后的空间占用.

对于索引而言, 通常它们会占用很多空间, 且其中包含大量空闲空间. 一般来说:
- 右平衡索引包含的空闲空间最小;
- 随机分布的索引通常会有 50% 左右的空闲空间;
- 升序索引包含 10% 左右的空闲空间.

随着集合不断增长, `db.collection.stats(<factor>)` 返回的巨大字节数将难以辨识,
因此可以向其传入比例因数来控制显示单位:

```js
// KB
db.demo.stats(1024)
// MB
db.demo.stats(1024*1024)
// etc.
```

至于查询数据库的空间占用和集合的方法类似, 使用 `db.stats()` 返回数据库信息后,
其中有 `fileSize` 字段反应了数据库文件在磁盘上占用的空间, 它应该总是最大的.
之后便是 `storageSize`, 它和 `fileSize` 的差值部分一般是那些被 `0` 填充的预留空间.
此外该方法同样可以接受比例因数来控制单位.
