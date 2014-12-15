# MongoDB Day 1

<br>
<br>

## Concept

#### Documents

文档是键值对的 __有序集__.
通常来说, 文档的键是字符串, 值可以是任何数据类型.

- 文档的键通常是字符串, 区分大小写, 且不能包含正则表达式中常用的特殊字符 (`\0`, `$`, `.`)
- 文档的值可以是任意类型.

#### Collections

集合就是一组文档, 如果将文档视为关系数据库中的行, 集合就是表.
集合是动态模式的, 一个集合内可以存在多种类型的文档.
集合使用名称进行标识, 命名需要满足以下要求:
- 集合名称不能是空字符串
- 集合名称不能包含 `\0` 和 `$`
- 集合名称不能以 `system.***` 开头, 这是系统保留前缀.
- 组织集合使用 `.` 分隔不同 namespace 下的子集合

如果集合包含了保留字或者 Javascript 属性名称,
那么在 shell 中调用 `db.collectionName` 是无法正常工作的,
当遇到这样的问题时可以使用 `db.getCollection("collectionName");` 函数.
或者也可以根据 Javascript 语言自身的特性 `x.y == x[y]` 使用数组的语法访问集合.


#### Databases

数据库就是一组集合, 它们有各自的权限, 存放在磁盘的不同文件中.
数据库也是以名称来标识, 命名需满足以下要求:
- 不能是空字符串
- 基本上只能使用 ASCII 中的字母和数字, 绝大多数符号都不可以用来命名数据库
- 数据库名称大小写敏感, 通常约定使用小写
- 数据库名称最长为 64 bytes
- `admin`, `local`, `config` 为系统保留数据库

<br>
<br>

## Installation (Ubuntu)

```bash
# import public key
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
# create source list file
echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' \
| sudo tee /etc/apt/sources.list.d/mongodb.list
# reload local package database
sudo apt-get update
# install mongodb package
sudo apt-get install -y mongodb-org
# run
sudo service mongod start
```

默认情况下, MongoDB 使用 `/var/lib/mongodb` 作为数据存储目录,
并监听 `127.0.0.1:27017`,
可以修改配置文件 `/etc/mongod.conf` 更改相关参数.
如果数据目录不存在或不可写, 以及监听端口被占用, 都会导致服务启动失败.
视安装方式不同, 服务启动前需要确认创建对应目录并分配写权限.
此外, MongoDB 还会启动一个 HTTP 服务, 监听端口比服务端口号高 `1000`,
即默认为 `28017`, 访问该端口可以获取数据库的管理信息.

<br>
<br>

## Mongo Shell

MongoDB 自带一个 Javascript shell 以方便一些简单操作,
它是一个完整的 Javascript 解释器, 可以运行任意 Javascript 程序.
可以通过 `mongo` 登录到 shell,
如果不想连接到默认的服务端或者数据库,
`--nodb` 参数可以在不连接任何数据库的情况下登录 shell.

```js
// $ mongo --nodb
// connect server
conn = new Mongo("10.0.0.10:8888")
// connect database
db = conn.getDB("demo")
```

MongoDB 内置了帮助文档, 可以通过 `help` 命令查看

```js
// help on shell operation
help
// sharding helpers
sh.help()
// help on database methods
db.help()
// help on collection methods
db.collection.help()
// function source, no parentheses
function_name
```

此外, 因为 MongoDB shell 本身就是一个 Javascript 解释器,
所以它也可以支持直接传递 Javascript 脚本.

```bash
# connect to "db" database on remote server and then execute scripts
mongo --quiet 10.0.0.10:8888/db script0.js script1.js script2.js
```

相对的, 在交互式 shell 中也可以使用 `load('script.js')` 执行脚本或使用
`run('cmd')` 执行命令行程序.

同时 MongoDB 为了方便 SQL 用户, 还支持一些非 Javascript 语法的扩展,
比如 `use demo`.

以一个简单的 Blog 数据库来演示数据库的基本 CRUD 操作:

#### Create

```js
// switch database
use demo
// create blog collection
post = {"title": "blog", "content": "post", "date": new Date()}
// insert data
db.blog.insert(post)
// or
db.blog.save(post)
```

#### Retrieve

```js
// read blog collection
db.blog.find()
// read one document in collection
db.blog.findOne('_index')
```

#### Update

```js
// add comments attribute to post object
post.comments = []
// match existing documents and update data
db.blog.update({'title': 'blog'}, post)
```

#### Delete

```js
// remove single document that match condition
db.blog.remove({'title': 'blog'}, 1)
// remove documents that match condition
db.blog.remove({'title': 'blog'})
// or remove all documents
db.blog.remove({})
```

[Complete Reference](http://docs.mongodb.org/manual/reference/)

<br>
<br>

## Data Models

MongoDB 在保留 JSON 基本的 key-value 属性的基础上, 添加了其它一些数据类型.
- null : 表示空值或不存在的字段
- boolean : true / false
- numeric : 64 位浮点数 (default), 4 字节带符号整数 (`NumberInt()`), 8 字节带符号整数 (`NumberLong()`)
- string
- date
- array
- regular expression
- embedded documents : 使得文档可以嵌套文档, 被嵌套的文档作为父文档的值
- object id : uid
- code : Javascript


#### Date

应使用 `new Date()` 来创建日期类型, 如果使用 constructor 作为函数进行调用,
返回的是日期字符串表示而非日期对象, 如果混用两种函数, 不便于根据日期进行相关操作.


#### Embedded Documents

在 MongoDB 中文档自身也支持嵌套, 作为某个文档的键的值.
使用嵌套文档可以使数据组织更加自然.

```
{
    "name" : "tsinghua university",
    "address" : {
        "street" : "college road",
        "city" : "beijing",
        "state" : "haidian"
    }
}
```

#### ObjectId

MongoDB 会为存储的文档添加一个 `_id` 键, 它可以是任何类型, 默认是一个 `ObjectId` 对象.
在一个集合中, 每个文档都拥有唯一的 `_id` 用来标识.

`ObjectId` 使用 12 bytes 的存储空间, 是一个由 24 个十六进制数组成的字符串,
它按照如下方式生成:

```
| 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|  time stamp   |   host    |  pid  |   counter   |
```

根据这样的生成规则
- 从标准纪元开始的时间戳提供了秒级的唯一性
- 时间戳在开头意味着 `ObjectId` 大致会按照插入的顺序排列, 某些情况下可以将其作为粗略索引提高效率
- 主机的唯一标识符通常是主机名称的 hash 值, 这样确保不同主机生成不同的 `ObjectId`
- 使用 `pid` 确保同一主机并发产生的 `ObjectId` 唯一
- 最后一个自动累加的计数器确保同一秒内同一进程产生的 `ObjectId` 也是唯一的, 每秒内最大值 `256^3` 个

<br>
<br>

## mongorc

`$HOME/.mongorc.js` 会在用户登录 shell 时自动执行, 可以使用该脚本创建一些环境变量,
或者重写一些内置函数.

```js
// mongorc.js

print('some information');

// define a "disable" function
var no = function() {
    print("Not on my watch");
};

// disable drop database
db.dropDatabase = DB.prototype.dropDatabase = no;
// disable drop collection
DBCollection.prototype.drop = no;
// disable drop index
DBCollection.prototype.dropIndex = no;
```

重写数据库函数时, 要确保同时对 `db` 变量和 `DB` 原型进行重写.
如果只重写了其中一个, 那么则可能在 `db` 指向其它数据库时失效.
启动 shell 时可以通过 `--norc` 参数禁止加载 `.mongorc.js`.
