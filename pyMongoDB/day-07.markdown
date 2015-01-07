# MongoDB Day 7

<br>
<br>

## 特殊的索引和集合

#### TTL Indexes

"Time To Live" 在 MongoDB 中属于一种比较特殊的索引,
它用来定期从数据库中自动移除被索引的文档.
通常是用来定期清理像日志文件等数据.

TTL 索引不支持 compound indexes 且其索引字段 __必须__ 是一个日期类型.
如果索引字段包含一个数组且其中有多个日期类型数据, MongoDB 将会匹配最早的一个日期移除数据.

至于过期文档的移除操作, MongoDB 的后台任务会每分钟检查一次过期文档,
并且移除操作的耗时也要取决于当前服务器的负载, 所以过期文档通常会存在一个移除延迟,
这个时间可能会超过 1 分钟.

除了以上限制外, TTL 索引和普通索引没任何区别, 也可以用来进行查询.

```js
// 建立一个 TTL 索引, 确定索引键为日期类型并使用 expireAfterSecs 指定老化时间
db.demo.ensureIndex({"date": 1}, {"expireAfterSecs": 86400})
// 也可以随时修改这个时间阈值
db.runCommand({"collMod": "demo.date", "expireAfterSecs": 43200})
```

#### Text Indexes

使用文本索引可以非常快速地搜索文档中的文本内容, 效率高于精确匹配和正则表达式.
创建一个文本索引的开销很高, 不建议在正在提供服务的实例上创建.
同时文本索引对性能的影响也更加明显, 因为所有字符串都需要被分词后保存.
因此拥有文本索引的集合的写入性能会比其它集合要差.

笔记记录的版本为 `2.6`, MongoDB 从 `2.4` 版本开始默认开启文本索引功能,
创建一个文本索引也是使用 `ensureIndex()`,
它和普通索引唯一的区别就是索引字段的值为 `"text"`, 表示这是一个文本索引.
需要注意的是:
- 一个集合最多只能有一个文本索引, 但它可以有多个键.
- 被索引的字段应该是字符串类型, 或者以字符串为元素的数组.
- 和普通索引不同, 多键文本索引中键的顺序并不重要, 可以使用权重来控制字段的相对重要性.
- 文本索引除了英语外还有限支持常见的印欧语系语言.
- 养成为索引修改名称的习惯, 便于管理也有效避免索引名长度超过限制.
- 文本索引默认就是稀疏的, 所以当一个文档缺少索引键或值为 `null` 的时候, 它不会被索引.

以及当使用 `$text` 操作符进行查询时, 也有一些额外限制,具体参考
[文档](http://docs.mongodb.org/manual/reference/operator/query/text/#op._S_text)

```js
// set the language to spanish
db.demo.ensureIndex({"comments": "text"}, {"default_language": "spanish"})
// multiple keys
db.demo.ensureIndex({"subject": "text", "content": "text"})
// use the wildcard specifier to index all fields
db.demo.ensureIndex({"$**": "text"}, {"name": "textIndex"})
// set weights (default = 1)
db.demo.ensureIndex({"title": "text", "content": "text"},
{"weights": {"title": 1, "content": 2}})
// set weights to "$**"
db.demo.ensureIndex({"whatever": "text"},
{"weights": {"title": 1, "$**": 2, "content": 3}})
// use $text && $search operator
db.demo.find({"$text": {"$search": "DEMO", "$language": "english"}})
db.demo.find({"title": "DEMO", "$text": {"$search": "DEMO"}})
// optimize query
db.demo.ensureIndex({"title": 1, "content": "text"}, {"name": "optIndex"})
// remove index
db.demo.dropIndex("textIndex")
```


#### Capped Collection

MongoDB 中的集合通常都是动态创建的, 而且尺寸也是随着数据增多而动态扩展的.
但很多时候也需要能够严格限制容量的集合,
在 MongoDB 中称这类集合为 "capped collection".

固定集合特殊的地方主要在于:
- 固定集合的实现类似于一个环状队列,
向一个已满地固定集合中插入数据则最早存在的数据将会被删除以释放空间.
- 在固定集合中, 数据被顺序写入磁盘上的固定空间,
因此它们在 "spinning disk" 上的写入速度非常快,
尤其当该集合拥有专用的磁盘时.
- 固定集合必须被显式创建, 而不能随着数据操作动态创建.

```js
// 创建一个大小为 100000 字节, 最多允许 100 个文档的固定集合
db.createCollection("cap_col", {"capped": true, "size": 100000, "max": 100})
```

可以用 `convertToCapped()` 将非固定集合转换为固定集合, 但是固定集合无法转为其它集合.
修改固定集合唯一的方法就是删除之后重建.

#### Natural Sort

由于固定集合中数据都是被顺序写入磁盘的固定空间的, 于是固定集合就存在一种 "自然排序",
即按照磁盘顺序的排序, 也就是按文档被插入的先后顺序进行排序, 可以是正向或反向.

```js
db.cap_col.find().sort({'$natural': 1})
db.cap_col.find().sort({'$natural': -1})
```

#### Tailable Cursor

循环指针是一种特殊的指针, 它不会随着结果集遍历结束后被关闭.
循环指针的设计来自于 `tail -f` 命令, 会尽可能持久地提取结果.
不过由于普通集合并不维护文档的插入顺序, 故而循环指针只能用于固定集合.

```py
import pymongo

client = pymongo.MongoClient()
db = client['test']
coll = db['demo']
cursor = coll.find(tailable=True)
# cursor = coll.find({}, {"tailable": True})
```

- 默认情况下, 如果超过 10 分钟没有新的文档插入循环指针就会被关闭.
所以如果是一个长期持续的查询任务, 应该确保指针被关闭后自动重新执行查询任务.
- 循环指针不使用索引, 返回的结果按照自然排序.
- 因为不使用索引的关系, 所以初次扫描时会较慢.
- 当不存在匹配查询的文档时, 或将指向的文档恰好被删除时都会导致循环指针失效或死亡.
- 不要在已被索引的字段上使用循环指针, 而使用 `{indexedField: {$gt: <lastValue>}}`
来达到类似的效果.

#### Geospatial Index

- Spherical : 使用 `2dsphere index` 索引球形表面类型的坐标数据
- Flat : 使用 `2d index` 索引平面坐标数据.

`2dsphere index` 使用 [GeoJSON](http://geojson.org/) 格式,
支持以下对象:
- Point
- LineString
- Polygon
- MultiPoint
- MultiLineString
- MultiPolygon
- GeometryCollection

```json
{
    "name": "New York City",
    "loc": {
        "type": "Point",
        "coordinates": [50, 2]
    }
}


{
    "name": "Hudson River",
    "loc": {
        "type": "LineString",
        "coordinates": [[0, 0], [5, 5]]
    }
}


{
    "name": "England",
    "loc": {
        "type": "Polygon",
        "coordinates": [[0,0], [3, 3], [6, 0], [0, 0]]
    }
}
```

可以看到多边形和线类似也是用一个坐标数组来表示, 区别是 `type`;
`loc` 这个字段可以任意指定, 但是其中的子对象是由 GeoJSON 指定的, 不可以随意更改.

建立一个地理空间索引和其它索引同样, 索引字段的值为 `2dsphere` 或 `2d` 即可.
并且同样支持复合索引.

```js
db.map.ensureIndex({"loc": "2dsphere"})
db.map.ensureIndex({"loc": "2dsphere", "name": 1})
// compound geospatial index dose not require the field order
db.map.ensureIndex({"name": -1, "loc": "2dsphere"})
```

对于地理空间的查询, MongoDB 支持查找交集 (intersection), 包含 (within)
以及接近 (nearness).
查询时需要将查找的内容用 `{$geometry: geojson_object}` 转换为 GeoJSON 对象.

```js
gtw = {
    "type": "Polygon",
    "coordinates": [[0, 0], [0, 1], [1, 2]]
}
// intersection
db.map.find({"loc": {"$geoIntersects": {"$geometry": gtw}}})
// within
db.map.find({"loc": {"$geoWithin": {"$geometry": gtw}}})
// nearness
db.map.find({"loc": {"$near": {"$geometry": gtw}}})
// for more information
db.map.runCommand({"geoNear": "demo", "near": gtw, spherical: true})
```

需要注意
- `$near` 会对结果进行 "由近到远" 的排序.
- `2d index` 只对点进行索引,
即点集不会被视为线. 在 `$getWithin` 的查询时注意与 `2dsphere index` 的区别.
- `$geoWithin` 和 `$getIntersects` 都不一定需要地理空间索引, 但是使用索引可以明显提高效率.
