# MongoDB Day 3

<br>
<br>

## Advanced Queries

#### Null

在 MongoDB 中, `null` 类型和它在 javascript 中的作用有些差别,
它不仅会匹配自身, 还会匹配不包含这个键的文档.

```javascript
// db.demo.find()
{'_id': ObjectId('***'), 'x': 1, 'y': null}
{'_id': ObjectId('***'), 'x': 4, 'y': 8}
{'_id': ObjectId('***'), 'x': 8}

// db.demo.find({'y': null})
{'_id': ObjectId('***'), 'x': 1, 'y': null}
{'_id': ObjectId('***'), 'x': 8}
```

如果想仅匹配 `null`, 可以通过 `$exists` 条件判定键值对是否存在.

```javascript
db.demo.find( { 'y' : { '$in' : [null], '$exists' : true } } )
```

因为没有 `$eq` 操作符, 所以这条查询语句使用 `$in` 代替, 而查询的序列只有一个元素 `null`.
所以效果上来说是一样的.


#### Regular Expression

MongoDB 在查询时支持通过正则表达式来灵活匹配字符串, 它使用的是 Perl 兼容的 PCRE 库来匹配正则表达式.

```javascript
// "/.../i" 是正则表达式标识符, 可以省略
db.demo.find( { 'name' : /joey?/i } )
// 正则表达式可以匹配自身
db.demo.find( { 'bar' : /baz/ } )   // 匹配结果 { "_id" : ObjectId(...), "bar" : /baz/ }
```

#### Array

查询数组中的元素和查询标量值的语法是一样的.

```javascript
// db.demo.insert( { "fruit" : [ "apple", "banana", "peach" ] } )
db.demo.find( { "fruit" : "banana" } )
```

对于存在重复元素的多个数组, 可以使用 `$all` 来匹配多个元素.

```javascript
// db.demo.insert( { "id" : 1, "fruit" : [ "apple", "banana", "peach" ] } )
// db.demo.insert( { "id" : 2, "fruit" : [ "apple", "kumquat", "orange" ] } )
// db.demo.insert( { "id" : 3, "fruit" : [ "cherry", "banana", "apple" ] } )
// 找到既有苹果又有香蕉的文档
db.demo.find( { "fruit" : { $all : [ "apple", "banana" ] } } )
```

需要注意的是在上边的查询例子中, 顺序都是无关紧要的,
但是当使用整个数组进行精确匹配时就需要注意元素顺序.

对于数组这样一个有序序列来说, 也可以通过 `key.index` 索引值来查询特定位置的元素.
比如下面这条语句只会匹配 `fruit` 数组中下标 `2` 的元素为 `peach` 的文档.

```javascript
db.demo.find( { "fruit.2" : "peach" } )
```

此外, 基于数组的自身特性还可以实现很多其它方便的查询方法,
比如使用 `$size` 就可以查询指定长度的数组, 它可以配合加法器 `$inc` 来实现一个随着更新而自增的 "size" 键

```javascript
db.demo.update( criteria, { "$push" : { "fruit" : "strawberry" }, "$inc" : { "size" : 1 } } )
```

上例就可以实现每次插入元素时 "size" 键的值就对应增加.
使用 `$size` 的缺点就是这种表达式无法和其它查询条件比如 `$gt` 以及诸如 `$addToSet` 这样的操作符同时使用.

需要注意的是关于 `$slice` 切片操作符的语法上有点特殊, 不同于以往在 Python 中的使用习惯.

```javascript
// 返回符合条件的文档中的 "comments" 数组的前 10 个元素.
db.demo.find( criteria, { "comments" : { "$slice" : 10 } } )
// 返回符合条件的文档中的 "comments" 数组的 # 第 11 ~ 20 个 # 元素,
// 从语法上表示为 [10, 10], 即跳过前 10 个元素, 返回从第 11 个元素开始的 10 个元素.
db.demo.find( criteria, { "comments" : { "$slice" : [10, 10] } } )
```

#### $where

键值对是一种表达能力非常好的查询方式, 但是依然有些需求它无法表达.
对此, `$where` 很好地填补了这部分的空缺.
使用 `$where` 可以在查询语句中执行任意的 JavaScript 脚本, 这样就能在查询语句中做几乎任何事情.
因此, 大多数情况下 `$where` 在很多客户端中都是被禁止使用的.
尽管如此, 使用 `$where` 有些时候可以大大降低查询的复杂度.

```javascript
// 查询两个不同键具有相同值的文档
db.demo.find({"$where" : function() {
    for (var current in this) {
        for (var other in this) {
            if (current != other && this[current] == this[other]) {
                return true
            }
        }
    }
    return false
}});
```

`$where` 的速度要比常规查询慢很多, 原因是每个文档都要从 BSON 对象转换成 JavaScript 对象,
并且 `$where` 不能使用索引, 所以如果一定要使用它的话应该先使用常规查询进行过滤以降低性能损失.

#### Svrscript

JavaScript 相关的安全问题都与用户在服务器上提供的程序有关,
如果希望避免这些风险, 那么就要确保不能直接将用户输入传递给 `mongod`.

```javascript
name = "'); db.dropDatabase();"
func = "function() { print('Hello, " + name + "!'); }"
// → "function() { print('Hello, '); db.Database(); print('!'); }"
```

上边的例子中可以看到, 当我们在 MongoDB 中使用一些脚本的时候,
用户传入的变量是非常危险的, 执行上边这段代码的结果就是整个数据库被删除.
避免这种情况的方法是使用 _作用域_ 来传递变量.

```py
func = pymongo.code.Code("function() { print('Hello, ' + username + '!'); }", {"username" : name})
```

由于代码实际上可能是字符串和作用域的混合体, 所以大多数驱动程序都有一种特殊类型用于向数据库传递代码.
作用域是用于表示变量名和值的映射的文档.
此外可以在启动 MongoDB 守护进程时指定 `mongod --noscripting` 完全关闭 JavaScript 执行.

#### Cursor

数据库使用指针返回查询结果, 根据客户端对指针的实现以对查询结果加以控制.

```javascript
for (idx=0; idx<100; idx++) {
    db.collection.insert({ x : idx });
}

var cursor = db.collection.find();
```

通过赋值给一个局部变量的方法来创建指针是比较常见的做法, 指针使用 `next` 方法来进行迭代.

```javascript
// hasNext 方法查看指针是否还有可迭代项
while (cursor.hasNext()) {
    obj = cursor.next();
    // do sth ...
}

var cursor = db.demo.find();
cursor.forEach(function(x) {
    print(x.name);
});
```

调用 `find` 时 shell 并不立即查询数据库, 而是等待真正开始要求获得结果时才发送查询
(和 Python 中的 generator 同理), 在执行查询之前就可以给查询附加各种额外的选项.
常用的附加选项有:
- limit : 限制结果数量上限
- skip : 忽略最开始的若干结果
- sort : 接受一个键值对对象作为参数, { "some key in document" : 1 (ascending) or -1 (descending)}, 如果指定了多个键则按照这些键被指定的顺序逐个排序.

```javascript
// 返回最多 3 个结果, 如果结果不足 3 个则返回匹配数量的结果
db.demo.find().limit(3)
// 忽略前 3 个匹配的结果
db.demo.find().skip(3)
// 按照 "price" 键降序输出结果
db.demo.find().sort( { "price" : -1 } )
```

_这三个方法可以组合使用且没有顺序要求_

前边提到过 MongoDB 中一个键的值可能是多种数据类型, 对于不同的数据类型排序其优先级从小到大依次是:
1. minimum
2. null
3. numeric
4. string
5. object / document
6. array
7. binary
8. ObjectId
9. boolean
10. Date
11. time stamp
12. regularExp
13. maximum

另在使用 `skip` 方法时应避免忽略大量结果,
因为要先找到需要被忽略的数据然后在抛弃这些数据, 会导致处理过程非常低效.
那么对于存在大量结果的分页显示时, 如果后端查询使用 `skip` 有时候就会导致上述情况发生.
所以很多时候实现分页查询可以利用上一次的查询结果定义下一次查询.

```javascript
var first = db.demo.find().sort({"date": -1}).limit(50)
var latest = null;

while (first.hasNext()) {
    latest = first.next();
    display(latest);
}

var second = db.demo.find({"date": {"$gt": latest.date}});
second.sort({"date": -1}).limit(50);
```

#### Stochastic Queries

对于从集合中随机查询一个文档的应用场景,
最笨的办法就是计算文档总数, 然后根据结果生成一个随机数进行一次 `find` 查询.
这种方法无疑效率是非常低的.
在数据库中查找随机数据的方法非常多, 比如在建模时为每个文档都添加一个随机键,
通常是一个随机数. 这样在随机查询时只需要生成一个随机数并将其作为查询条件进行查询就好了.

```javascript

for (idx=0; idx<1000; idx++) {
    db.demo.insert({"index": idx, "random": Math.random()});
}


var rand = Math.random();
res = db.demo.findOne({"random": {"$gt": rand}});
if (res == null) {
    res = db.demo.findOne("random": {"$lt": rand});
}
```

#### Wrapped Query

所谓 "wrapped query" 就是将 "plain query" 中的查询条件封装在一个更大的文档中传递给数据库.
上文提到的 `limit`, `skip`, `sort` 这类查询方法都属于封装查询.
比如 `db.demo.find({"foo": "bar"}).sort({"date": -1})`
实际是将 `{"foo": "bar"}` 这个查询条件封装成 `{"$query": {"foo": "bar"}, "$orderby": {"date": -1}}`
再传递给数据库.
