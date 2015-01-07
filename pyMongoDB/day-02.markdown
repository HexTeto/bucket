# MongoDB Day 2

<br>
<br>

## Bulk Operations

`Bulk()` 批量操作构建器为 MongoDB 提供了批量操作的支持,

```js
// instantiate the ordered builder
db.collection.initializeOrderedBulkOp()
// or instantiate the unordered builder
db.collection.initializeUnorderedBulkOp()
```

需要注意的是, MongoDB 对于单次批量操作的操作数量以及文档大小等都有相应的限制,
参考 [MongoDB Limits and Thresholds](http://docs.mongodb.org/manual/reference/limits/).

#### Ordered Operations

对于有序操作, 当前版本中的做法是将一系列操作根据类型和顺序关系进行分组然后执行,
即相同类型的连续操作将被分为一组依序执行.

```js
var bulk = db.items.initializeOrderedBulkOp();
bulk.insert( { item: "abc123", defaultQty: 100, status: "A", points: 100 } );
bulk.update( { item: "abc123", defaultQty: 100, status: "P", points: 0} );
bulk.insert( { item: "ijk123", defaultQty: 200, status: "A", points: 200 } );
bulk.insert( { item: "mop123", defaultQty: 0, status: "P", points: 0 } );
bulk.execute();
```

对于上边这个例子, 有 `insert0, update0, insert1, insert2` 4 个有序操作,
则 MongoDB 会将它们分为三组, 分别是 `(insert0), (update0), (insert1, insert2)`.
对于每一个组允许最多 1000 个操作, 对于超过这个限制的一组操作将不断被拆分为多个组直到满足条件.

通常来说, 有序批量操作都是要慢于无序操作的, 因为每个操作都必须要等待它上一个操作完成才会执行.
所以更多情况下, 使用无序批量操作的场景会更多.

#### Unordered Operations

无序操作可以并行执行, 且不会依照固定顺序. MongoDB 同样会将操作分组,
与有序操作不同的是因为没有固定顺序要求, 所以操作将会被重新排序再按照类型来分组以提高执行效率.
因此对于无序操作, 应该是应用于那些对于顺序没有依赖的操作.

对于操作的数量无序操作同样是限制每组最多 1000 个操作.
可以在 `Bulk.execute()` 函数之后调用 `Bulk.getOperations()` 函数来查看操作如何被分组.

#### Error Handling

在有序批量操作中, 因为所有的操作都是串联的, 所以如果某一操作出现了错误, 那么后续的操作将不会被执行;
而在无序批量操作中, 某个操作出现错误将不会影响其它操作.

#### Bulk Update or Remove

`Bulk.find()` 方法提供了一个批量选择器, 可以指定一个查询条件,
然后对匹配的所有文档执行以下操作.
- `Bulk.find.removeOne()`
- `Bulk.find.remove()`
- `Bulk.find[.upsert()].replaceOne()`
- `Bulk.find[.upsert()].updateOne()`
- `Bulk.find[.upsert()].update()`

这其中后三项都是更新或替换操作, 它们还支持搭配 `upsert()` 选项.
当 `upsert()` 被指定时 (其默认处于 `true` 状态), 如果不存在匹配条件的文档,
则更新或替换行为将会变为 `insert` 操作.

```js
var bulk = db.items.initializeUnorderedBulkOp();

bulk.find( { status: "D" } ).remove();
bulk.find( { status: "P" } ).upsert().update( { $set: { points: 0 } } );
bulk.find( { status: "K" } ).upsert().replaceOne(
    // sets the value of 'defaultQty' field if this update operation results in insert,
    // has no effect on modify existing document.
    $setOnInsert: { defaultQty: 0, inStock: true },
    // sets the value of 'lastModified' field to current date
    $currentDate: { lastModified: ture },
    $set : { points: 0 }
);
bulk.execute();
```

_要匹配所有文档可以传递一个空文档_ (`{}`) _作为参数_

关于更多批量操作参考 [Bulk Operation Methods](http://docs.mongodb.org/manual/reference/method/js-bulk/)

#### Modifier

MongoDB 内置了很多方便的修改器帮助完成相关操作:
- `$set` : 指定键如果不存在则创建
- `$inc` : 指定键如果不存在则创建, 存在则在原值上相加
- `$push` : 用来修改数组, 指定键不存在则创建, 存在则在末尾添加一个元素
- `$each` : 在数组操作中允许一次 `$push` 修改多个元素
- `$slice` : 限制数组长度, 必须是负整数, 表示数组中最后加入的 `n` 个元素
- `$sort` : 根据指定键的值对数组中的元素排序
- `$ne`, `$addToSet` : 将数组作为数据集使用, 避免插入重复元素
- `$pop` : 根据 index 移除数组中的元素
- `$pull` : 根据 value 移除数组中的元素
- [etc.](http://docs.mongodb.org/manual/reference/operator/)

<br>
<br>

## GridFS

GridFS 用来存储和检索超过 BSON Document 大小限制 (16MB) 的文件,
它将大文件分为若干 Chunks 并将它们作为单独的文件存储, 默认情况下 chunk 大小限制为 256k.
GridFS 使用两个集合存储数据: `chunks` 存储拆分后的数据块, `files` 存储文件的元数据.

```
# files collection

{
    "_id" : <an unique ObjectId for this document>,
    "length" : <size of the document in Bytes>,
    "chunkSize" : <size of each chunk, default is 256 Kilobtyes>,
    "uploadDate" : <date that document was first stored by GridFS>,
    "md5" : <a hash string>,

    "filename" : <a human-readable name for the document, optional>,
    "contentType" : <a valid MIME type for the document, optional>,
    "aliases" : <an array of alias strings, optional>,
    "metadata" : <any additional information you want to store>,
}


# chunks collection

{
    "_id" : <an unique ObjectId for this chunk>,
    "files_id" : <the "_id" field of the "parent" document, as specified in the files collection>,
    "n" : <the sequence number of the chunk. GridFS numbers all chunks, starting with 0>,
    "data" : <the chunk's payload as a BSON binary type>
}
```

#### When should I use GridFS?

 - If your filesystem limits the number of files in a directory, you can use GridFS to store as many files as needed.
 - When you want to keep your files and metadata automatically synced and deployed across a number of systems and facilities. When using geographically distributed replica sets MongoDB can distribute files and their metadata automatically to a number of mongod instances and facilities.
 - When you want to access information from portions of large files without having to load whole files into memory, you can use GridFS to recall sections of files without reading the entire file into memory.

#### mongofiles

`mongofiles` 工具提供了命令行接口与 GridFS 进行交互.
[完整参考手册](http://docs.mongodb.org/manual/reference/program/mongofiles/)

#### GridFS APIs

以 [Python Driver](http://api.mongodb.org/python/current/api/gridfs/index.html?highlight=gridfs#module-gridfs) 为例.

```py
from pymongo import MongoClient
import gridfs

db = MongoClient().test
fs = gridfs.GridFS(db)

file_id = fs.put('Hello, World', filename='hello.txt')
fs_list = fs.list()

content = fs.get(file_id).read()

print fs_list
# [u'hello.txt']
print content
# 'Hello, World'
```
