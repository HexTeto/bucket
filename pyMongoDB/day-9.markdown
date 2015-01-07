# MongoDB Day 9

[data-design]:http://docs.mongodb.org/manual/core/data-model-design/
<br>
<br>

## Application Design

#### Normalization && Denormalization

Normalization 即将数据分散到多个不同的集合, 相互之间可以引用.
虽然很多文档可以引用某一块数据, 但是这块数据只存储在一个集合中.
故而如果要修改这块数据, 只需要修改保存它的那个文档即可.
但是因为 MongoDB 没有提供连接 (join) 工具, 所以在不同集合之间执行连接查询需要进行多次查询.

Denormalization 则相反, 将每个文档所需的数据都嵌入在文档内部. 每个文档都拥有自己的副本,
而不是所有文档共同引用同一个数据副本. 这样如果数据发生变化, 那么所有相关文档都需要更新,
但是在执行查询时只需要一次查询就可以得到所有数据,
这样的数据模型在 MongoDB 中也称作 "Embedded Data Models".

由上有结论: 标准化数据模型可以提高写速度, 而嵌入式数据模型可以提高读速度.
那么采取何种模型就要根据应用需求来决定了.

通常以下情况选择 embedded data:

- 数据实体之间存在 "one-to-one" 关系

```js
// patron document
{
    _id : "joe",
    name : "Joe Bookreader"
}

// address document
{
    patron_id : "joe",
    street : "123 Fake Street",
    city : "Faketon",
    state : "MA",
    zip : "12345"
}
```

在这个 "one-to-one" 的例子中, "address document" 中的数据实体作为
"patron document" 的 "context" 而存在, 即二者属于从属关系.
在上边的标准化模型中, "address document" 中的 `patron_id : "joe"` 就是一个引用.
如果应用频繁使用 `name` 字段来检索地址信息, 则需要发出多个查询.
所以对着这种关系的数据就更加适用于嵌入式模型.

```js
{
    _id : "joe",
    name : "Joe Bookreader",
    address : {
                street : "123 Fake Street",
                city : "Faketon",
                state : "MA",
                zip : "12345"
              }
}
```

- 数据实体之间存在 "one-to-many" 的关系

```js
// patron document
{
    _id : "joe",
    name : "Joe Bookreader"
}

// address documents
{
    patron_id : "joe",
    street : "123 Fake Street",
    city : "Faketon",
    state : "MA",
    zip : "12345"
}

{
    patron_id : "joe",
    street : "1 Some Other Street",
    city : "Boston",
    state : "MA",
    zip : "12345"
}
```

在上边这个 "one-to-many" 的例子中, 如果频繁使用 `name` 字段来检索地址信息,
则出现和之前例子相同的问题. 同样转为嵌入式模型.

```js
{
    _id : "joe",
    name : "Joe Bookreader",
    address : [
                {
                  street : "123 Fake Street",
                  city : "Faketon",
                  state : "MA",
                  zip : "12345"
                },
                {
                  street : "1 Some Other Street",
                  city : "Boston",
                  state : "MA",
                  zip : "12345"
                }
              ]
}
```

对于以下情况, 则应选择 normalized data:

- 嵌入式会导致数据重复且读性能的提高收益不会超过重复带来的影响
- 要描述较为复杂的 "many-to-many" 关系
- 大型的分层结构数据集

当然, 两种数据模型也可以混合使用, 将不同类型数据区分开分别建模以获得读写性能的平衡.
通常来说, 我们归纳以下参考规则:
- 子文档较小适合内嵌, 子文档较大则适合引用
- 数据不会经常变动适合内嵌, 数据频繁更新则适合引用
- 数据要求最终一致适合内嵌, 数据要求全局一致适合引用
- 数据通常需要二次查询获得适合内嵌, 数据通常不包含在返回结果内适合引用
- 文档数据增速较慢适合内嵌, 文档数据增速较快适合引用
- 要求快速读适合内嵌, 要求快速写适合引用


#### Cardinality

之前在索引部分的笔记提到过基数的概念.

> 在索引中基数指的是集合中某个键拥有的不同值的数量, 基数越高索引收益就越大.

我们在数据模型中引用索引中基数的思想,
定义为一个集合中包含的对其它集合的引用数量.
集合之间的引用常见有 "one-to-one", "one-to-many" 以及 "many-to-many".
假设在一个博客应用中, 对于每篇文章 (post) 来说:
- 每篇文章都会有一个标题, 那么 `(post, title)` 就是一个 "one-to-one" 的关系.
- 每个作者可能不止会有一篇文章, 那么 `(author, post)` 就是一个 "one-to-many" 的关系.
- 每篇文章可能存在多个标签, 每个标签又可以在多篇文章中出现, 所以 `(post, tag)` 是一个 "many-to-many" 的关系.

在 MongoDB 中, 我们将 "many" 拆分为两个子类: "many" 和 "few".
比如一个网站可能存在上万篇文章, 但是它们都在讨论几个固定的主题, 于是 `(post, tag)` 就是一个 "many-to-few" 的关系.
像这样确定了 "many" 与 "few" 的关系, 就可以比较容易在内嵌模型和引用模型之间进行权衡.
通常来说, "few" 的关系使用内嵌方式会比较好, "many" 的关系使用引用的方式比较好.

<br>
<br>

## SNS Data Models

针对数据模型的设计, 我们以一个社交网站的实例来说明.
社交网站无论是以什么为导向, 最终都是实现人与人之间有选择性的链接,
我们先将这个社交行为简化为一个简单的发布订阅系统,
即定义为一个用户订阅另一个用户发布的消息这样一个概念.

比较常见的实现方式有三种, 第一种是将发布者内嵌在订阅者文档中:

```js
{
    "_id" : ObjectId("abc123"),
    "username" : "batman",
    "email" : "batman@msns.org",
    "following" : [
        ObjectId("bcd234"),
        ObjectId("cde345")
    ]
}
```

对于上边这样的设计, 我们可以通过 `{$in : user['following']}` 来查询一个用户感兴趣的人.
但反过来对于一条消息要找出对这条消息感兴趣的人则必须要查找所有用户的 `following` 字段.

那么第二种设计方式就有了将订阅者内嵌到发布者文档中:

```js
{
    "_id" : ObjectId("cde345"),
    "username" : "joker",
    "email" : "joker@msns.org",
    "followers" : [
        ObjectId("abc123"),
        ObjectId("bcd234")
    ]
}
```

这样当一个新的消息产生后, 只需要一次查询就立刻可以获得所有对这条消息感兴趣的人.
但该设计方式的缺点同样很明显, 如果需要找到一个用户的订阅列表, 就必须查询整个用户集合.

此外, 以上两种方式都存在一个共同的问题就是会导致用户文档变得越来越大且数据变更也随之更加频繁.
我们注意到, 虽然 `following` 和 `followers` 这两个字段的作用是非常核心的,
但是其实对于查询结果来说我们并不需要经常返回它们.
于是进一步就可以采取标准化的模型, 将 "订阅关系" 保存到单独的集合中.

```js
{
    "_id" : ObjectId("abc123"),
    "followers" : [
        ObjectId("bcd234"),
        ObjectId("cde345")
    ]
}
```

无论使用什么样的策略, 内嵌字段只能在子文档或者引用数量不是特别大的情况下有效发挥作用.
对于基数较大的用户, 可能会由于极大的 `followers` 数组导致文档溢出.
对于这种情况的一种有效解决方案是在必要时使用 "连续的" 文档.

```js
{
    "_id" : ObjectId("abc123a"),
    "username" : "wil",
    "email" : "wil@msns.org",
    "tbc" : [
        ObjectId("abc123b")
        ObjectId("abc123c")
    ],
    "followers" : [
        ObjectId("bcd234")
    ]
}

{
    "_id" : ObjectId("abc123b"),
    "followers" : [
        ObjectId("cde345")
    ]
}
```

就像上边这个例子一样, 我们使用 `tbc` 字段指定了关联的文档用来存储过大的 `followers` 字段.
需要注意的是, MongoDB 并没有提供这样的逻辑, 需要我们在程序中自己实现.
