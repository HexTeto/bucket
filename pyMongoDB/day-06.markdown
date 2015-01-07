# MongoDB Day6

<br>
<br>

## 获取更多信息来优化查询

之前已经使用过 `explain()` 来显示查询的详细信息,
这些信息可以说是 MongoDB 中最重要的诊断工具之一.

`explain()` 对于不同类型的查询返回的信息字段大致如下:
- `cursor : BasicCursor / BtreeCursor`, 反应查询是否使用了索引,
如果使用了多键索引或者对结果逆序遍历, 还会看到 `multi` 和 `reverse` 等值;
- `isMultiKey : <boolean>`, 多键索引标签;
- `allPlans : <integer>`, 本次查询存在的可用查询方案数量;
- `n : <integer>`, 本次查询返回的文档数量;
- `nscannedObjects : <integer>`, 根据索引指针查找实际文档的次数;
- `nscanned : <integer>`, 查找过的索引项数量 (不使用索引的话就是检查过的文档数量);
- `scanAndOrder: <boolean>`, 是否在内存中对结果集进行了排序;
- `indexOnly : <boolean>`, 是否只使用索引就完成了此次查询;
- `nYields : <integer>`, 在查询过程中为了等待写操作而暂停的次数;
- `millis : <integer>`, 执行查询消耗的时间 (ms);
- `indexBounds : <multi>`, 这个字段描述了索引的查询范围, 可以看到索引是如何遍历文档的;

有的时候可能会需要让 MongoDB 使用指定的索引来进行查询,
可以使用 `hint()` 来强制指定索引:

```js
db.books.find({"date": 20141222, "author": /.*/}).hint({"date": 1, "author": 1})
```

使用 `hint()` 会带来一个问题就是当指定了一个不恰当的索引时,
MongoDB 不知道该如何去使用这个索引进行查询, 于是就导致查询效率甚至不如不用索引来得快.
为了避免这种情况, 在调试过程中就要配合 `explain()` 来检查各查询.

MongoDB 的查询优化器在选择索引时大致依照如下规则:
1. 如果恰好有一个索引可以精确匹配一个查询则使用;
2. 如果存在多个可用的索引, 将会产生多个并行的查询计划,
采用最早返回 100 个结果的索引并终止其它查询.
被采用的查询计划会被缓存,
之后每次查询都会采用它直到集合数据发生较大变动或执行 1000 次查询后, 再重复该过程.
`explain()` 输出信息中的 `allPlans` 就显示了本次查询共有多少种查询计划.

_此外需要注意的是_ `explain()` _只能放在查询语句的最后调用._

#### 何时不应该使用索引?

提取较小的子数据集时索引非常高效, 而当结果集在原数据集中所占比例越大时, 索引效率就越低.
这是因为索引会先查找对应索引条目, 再根据索引指针去查找实际文档,
所以如果要返回集合内全部文档时, 使用索引会比全表扫描的效率低得多.

然而没有一个严格的规则告诉我们如何有效判断是否应该使用索引,
所以在调试过程中利用 `explian()` 比较各种查询的耗时非常重要.

通常来说, 索引适用于在较大数据集中选择性查询少量数据,
而对于较小的数据集或非选择性查询则应该使用全表扫描.

<br>
<br>

## Index Properties

#### Unique Indexes

唯一索引可以确保集合的每一个文档的指定键都有唯一值.

```js
db.users.ensureIndex({'username': 1}, {'unique': true})

// 此时如果向该集合内插入键重复文档则会抛出异常
db.users.insert({'username': 'bob'})
db.users.insert({'username': 'bob'})

/*
WriteResult({
"nInserted" : 0,
"writeError" : {
"code" : 11000,
"errmsg" : "insertDocument :: caused by :: 11000 E11000 duplicate key error index: demo.users.$username_1  dup key: { : \"bob\" }"
}
})
*/
```

唯一索引通常用来应对写操作中偶尔可能会出现的键重复问题,
而不是在程序运行时用来对重复键进行过滤.

MongoDB 本身的 `_id` 键就是一个唯一索引, 它和其它用户创建的唯一索引的区别是它不能被删除,
而用户创建的唯一索引是可以删除的.

> MongoDB 的 "Index bucket" 严格限制索引条目的大小不得超过 1024 个字节,
> 如果某个索引条目超过了它的限制该条目就不会被包含在索引里,

此外, 唯一索引也可以创建复合索引. 创建复合索引时单个键的值可以相同,
但所有键的组合值必须是唯一的.

```js
db.users.ensureIndex({'username': 1, 'age': 1}, {'unique': true})
// 对于上边这个在 'username' 和 'age' 上创建的复合索引, 以下插入都是合法的
db.users.insert({'username': 'bob'})
db.users.insert({'username': 'bob', 'age': 24})
db.users.insert({'username': 'fred', 'age': 24})
```

GridFS 是 MongoDB 默认的用来分片存储大文档的文件系统,
其中就用到了复合唯一索引.
存储文件内容的集合有一个 `{ 'files_id' : 1, 'n' : 1 }` 上的复合唯一索引,
因此一个大文档可能就是 `n` 个具有相同 `files_id` 的子文档.

#### Sparse Indexes

唯一索引会将 `null` 视为一个实值而不是 "空",
所以无法将多个缺少唯一索引中的键的文档插入到集合中.
假设有一个字段未必集合中所有文档都会包含, 但当它存在时该字段就一定是唯一的,
这时就需要搭配使用 `unique` 和 `sparse` 选项创建一个唯一的稀疏索引
(当然也可以单独使用 `sparse` 创建非唯一的稀疏索引).

在 MongoDB 中, 稀疏索引的概念和关系型数据库中的稀疏索引是完全不同的概念,
MongoDB 中的稀疏索引只是不需要将每个文档都作为索引条目,
它会跳过不包含被索引字段的文档.

```js
// 为 users 集合添加一个可选的 email 字段, 当该字段存在时它必须是唯一的.
db.users.ensureIndex({'email': 1}, {'unique': true, 'sparse': true})
```

根据是否使用稀疏索引, 同一个查询返回的结果可能会不同.

```js
db.foo.find()
/*
{ "_id" : 0 }
{ "_id" : 1, "x" : 1 }
{ "_id" : 2, "x" : 2 }
{ "_id" : 3, "x" : 3 }
*/
db.foo.find({'x': {'$ne': 2}})
/*
{ "_id" : 0 }
{ "_id" : 1, "x" : 1 }
{ "_id" : 3, "x" : 3 }
*/
db.demo.ensureIndex({'x': 1}, {'sparse': 1})
db.demo.find({'x': {'$ne': 2}})
/*
{ "_id" : 1, "x" : 1 }
{ "_id" : 3, "x" : 3 }
*/
```

在上边这个例子中可以看到, 在添加了稀疏索引后不包含 `x` 键的文档被忽略了,
即使用稀疏索引时会忽略不包含指定键的文档.
如果要结果包含被忽略的结果则可以使用 `hint()` 强制全表扫描.
