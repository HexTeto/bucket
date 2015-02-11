# MongoDB Day 16

<br>
<br>

[local]:http://docs.mongodb.org/manual/core/authentication/#localhost-exception

## Security

#### Authentication

MongoDB 中, 每个数据库实例都可以配置任意个数的用户. 启动认证功能后, 只有通过身份验证的用户才能对数据库进行读写.

`admin` 和 `local` 是两个特殊的数据库, 它们当中的用户可以对任何数据库进行操作,
即分配至这两个数据库的用户为 administrator.

- 对于一个新部署的集群, 通常可以先在不开启认证的情况下启动集群
```sh
mongod --port 27017 --dbpath /data/db1
```
- 登录 shell, 并创建管理员
```js
use admin
db.createUser(
    {
        user: "siteAdmin",
        pwd: "mysecret",
        roles: [{role: "userAdminAnyDatabase", db: "admin"}]
    }
)
```
- 配置好管理员后, 使用 `--auth` 选项开启认证模式重启集群
```sh
mongod --auth --config /etc/mongodb/mongodb.conf
```

如果系统中还不存在管理员的情况下就已经启动了 MongoDB 实例,
那么 MongoDB 将会启动 [localhost exception][local] 机制, 它允许从本机发起的连接拥有全部的数据库操作权限,
依旧能够使用类似的方式创建管理员和普通用户. 一旦系统拥有了一个管理员后, localhost exception 机制将不再生效.

如果要关闭认证功能, 只需要重启实例且不使用上述参数即可.

在分片集群中启用身份认证时, 必须分别地在集群中所有的组件包括配置服务器和副本集成员上都启动身份认证,
且必须决定一种验证机制, 多数情况下普遍使用 `keyfile` 即秘钥文件, 需要注意保持用于身份验证的秘钥文件全局一致.

- 可以使用 `OpenSSL` 创建一个秘钥
```sh
openssl rand -base64 741 > mongKeyfile
chmod 600 mongoKeyfile
```
- 使用 `--keyFile` 参数指向 `keyfile` 启动实例
```sh
mongod --auth --keyFile /private/var/keyfile
```
- 也可以直接修改配置文件来指定 `keyFile` 字段的值为秘钥文件
```yaml
security:
    keyFile: /private/var/keyfile
```


#### Authorization

注意 Authorization 和 Authentication 的区别, 身份验证是用来验证客户端的合法身份,
而授权则用于访问控制, 它决定通过验证的用户可以访问和操作哪些资源.

MongoDB 采用 "Role-Based Access Control (RBAC)" 来控制访问权限.
默认情况下 authorization 处于关闭状态, 它会随着身份验证系统而启动.
对于一个单独的实例, 使用 `--auth` 选项很方便, 对于副本集和分片集群则需要指定一个一致的 `keyFile`.

此外, 在分片中 `admin` 这个库是保存在 config server 上的, 所以应该只允许客户端访问 `mongos` 实例.
