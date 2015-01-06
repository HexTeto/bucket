# MongoDB Day 8

<br>
<br>

[agg-fun]:http://docs.mongodb.org/manual/reference/method/db.collection.aggregate/#db.collection.aggregate
[agg-cmd]:http://docs.mongodb.org/manual/reference/command/aggregate/#dbcmd.aggregate
[agg-op]:http://docs.mongodb.org/manual/reference/operator/aggregation/#aggregation-pipeline-operator-reference
[cmd-mr]:http://docs.mongodb.org/manual/reference/command/mapReduce/#dbcmd.mapReduce
## Aggregation

#### Aggregation pipelines

MongoDB 提供了 [aggregate][agg-cmd] 和 [db.collection.aggregate()][agg-fun]
两种接口来实现聚合操作, 文档中分别列出了一系列例子来说明如何使用.

需要注意的是, 在 v2.6+ 版本中 [aggregate()][agg-fun] 默认总是返回一个指针,
而较早的版本中返回的是一个文档数组.
它们的区别是, 返回指针可以不受到 BSON 文档 16 MB 的大小限制.

#### Operators

在聚合操作中会使用到一系列诸如 `$project`, `$group` 等操作符,
每个操作符都会接收多个文档并进行相应操作然后将这些文档传递给下一个操作符
(对于最后一个操作符而言则是将结果集保存或返回给客户端).
不同的管道操作符可以按任意顺序组合, 且可以重复使用.

有关操作符参考文档 [aggregation pipeline operator][agg-op].

#### Pipeline operators and Indexes

诸如 `$match` 和 `$sort` 这样的管道操作符,
当它们作为第一个管道操作符时可以受益于索引来提高效率.
`$getNear` 这样的地理操作符同理, 也可以受益于地理空间索引.
不过即使使用索引, 聚合操作依旧需要访问实际文档, 因此索引并不能完全覆盖聚合管道.

因此当只需要提取集合数据中的某个子集时,
应尽量首先使用索引配合 `$match` 操作符来进行过滤,
这样可以只扫描集合中匹配条件的文档.

#### MapReduce

MapReduce 经常用来完成一些非常复杂以至于很难使用聚合框架来实现的逻辑,
而这种强大逻辑表达能力的代价就是在 MongoDB 中 MapReduce 非常的慢.

和普通聚合操作一样, map-reduce 同样可以将结果集保存至集合或返回给客户端,
当返回至客户端时, map-reduce 返回的是 BSON 文档, 因此不能超过 16 MB.

MongoDB 提供了 [mapReduce][cmd-mr] 命令来执行 MapReduce 操作,
"mapper" 和 "reducer" 通过 javascript 函数实现.

```js
db.runCommand({
    mapReduce: <collection>,
    map: <mapper func>
    reduce: <reducer func>
    finalize: <finalize func>
    out: <where to output>
    query: <doc>
    sort: <doc>
    limit: <number>
    scope: <doc>
    jsMode: <boolean>
    verbose: <boolean>
})
```

文档中提供了一系列例子来说明如何使用,
其中要注意 "mapper" 函数中 `this` 即为当前引用文档,
以及 "mapper" 必须使用 `emit()` 来传递键值对.

#### Single Purpose Aggregation Operations

尽管多数聚合操作现在都通过 aggregation pipeline 来实现,
但 MongoDB 中还是保留了一些语义简洁明确的函数用来完成部分聚合操作而无需使用框架.

- `count()`: 返回集合中匹配查询条件的文档数量
- `distinct()`: 返回集合中指定键的差异值
- `group()`: 根据查询条件将文档分组, 通常用来配合其它更复杂的聚合操作

```js
/*
db.demo.find()

{x: 1, y: 0}
{x: 1, y: 1}
{x: 1, y: 2}
{x: 1, y: 3}
{x: 2, y: 0}
{x: 2, y: 1}
*/

db.demo.count()            // 6
db.demo.count({"x": 2})    // 2

db.demo.distinct("x")      // [1, 2]
db.demo.distinct("y")      // [0, 1, 2, 3]

db.demo.group({
    key: {"x": 1},    // 指定根据 "x" 键进行分组
    cond: {"x": 2},   // 只分组 "x" 键的值为 2 的文档
    reduce: function(cur, res) {res.y += cur.y},  // 累加每个文档的 "y" 键的值
    initial: { "y": 0}    // 初始化从 0 开始, 该值作为初始文档传递给 reducer
})    // [ { "x" : 1, "y" : 6 } ]
```
