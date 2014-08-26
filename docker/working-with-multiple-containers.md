## Linking Containers Together

使用 `docker run --link` 选项来连接多个容器让它们可以互相通信.

```bash
# 首先创建一个后台运行的数据库容器
$ docker run -d --name database training/postgres
# 创建一个应用容器连接到数据库
$ docker run -d -P --name app --link database:db training/webapp python app.py 
```

`--link` 选项的格式为 `--link name:alias`.
其中 `name` 为我们已经创建了的要连接到的目标容器的名称, `alias` 则是这个链接的别名.
使用 `docker ps` 可以看到我们创建的容器 `database` 和 `app`,
并且可以看到在 `NAMES` 列下有 `database, app/db`,
它的意思是 `app` 容器被连接到了 `database` 容器, 他们的关系是 "parent/child".
此时父容器 `app` 可以访问子容器 `database` 中的数据.

Docker 通过创建一条安全通道实现容器之间的连接, 不需要使用外部网络端口.
所以在上边的例子中可以看到在创建 `database` 时并没有暴露任何网络端口.

Docker 将父容器的连接信息暴露给子容器通过以下两种途径实现:
- 环境变量
- `/etc/hosts`

## Managing Data in Containers

#### Data volumes

挂载一个数据卷使用 `docker run -v` 选项, 可以指定挂载多个卷.

```bash
$ docker run -d -P --name app -v /app training/webapp python app.py
```

这个操作会在容器中创建一个新的数据卷 `/app`, 如果我们要挂载一个主机上的目录到容器中,
只需要将上边的命令改为:

```bash
$ docker run -d -P --name app -v /srv/app:/app training/webapp python app.py
```

这样我们就将宿主机上的 `/srv/app` 这个目录挂载到了容器的 `/app` 位置.
需要注意的是宿主机上的目录必须用 __绝对路径__ 指定, 如果路径不存在则会自动创建该目录.

默认情况下, 容器对挂载的卷具有读写权限, 可以使用`/hostPath:/containerPath:ro`
将目录设置为只读.

此外, 我们还可以挂载单个文件到容器, 和挂载目录的方法一样, 只需要将目录改为具体的文件即可.
不过很多文本编辑工具比如 `sed` 在操作文件时会导致它的索引节点 (inode) 发生变化,
在 Docker v1.1.0 的版本中这会导致一个错误 `Device or resource busy`.
解决方法是将文件所在的目录挂载到容器即可.

#### Data Volume Container

如果需要共享一些持久数据到容器, 创建 Data Volume Container 是一个很好的解决方案.

```bash
$ docker run -d -v /data --name database training/postgres echo "Data-only container for postgres"
```

该命令创建了一个 `database` 容器运行 Postgres, 并创建了一个数据卷 `/data`.
有了这个数据容器, 我们就可以使用 `--volumes-from` 选项来挂载这个 `/data` 卷到任意容器:

```bash
$ docker run -d --volumes-from database --name db_cdn training/postgres
$ docker run -d --volumes-from database --name db_backup training/postgres
# 也可以链式的挂载
$ docker run -d --volumes-from db_cdn --name db_backup2 training/postgres
```

当我们删除挂载 `/data` 的容器 (包括初始的 `database` 容器) 时,
`/data` 是不会被删除的. 除非不再有任何容器引用这个卷, 否则它将一直存在.

#### Backup, restore, or migrate data volumes

我们可以利用 `--volumes-from` 实现数据的备份, 恢复和迁移.
比如下面这个例子:

```bash
$ docker run --volumes-from database -v $(pwd):/backup busybox tar cvf /backup/backup.tar /data
```

在这个例子中, 我们运行一个新的容器从 `database` 中挂载 `/data`, 并挂载宿主机的当前目录到新容器的 `/backup`,
然后通过 `tar` 工具打包 `/data` 到 `/backup/backup.tar`. 于是我们在宿主机的当前目录下就会得到一个数据的备份.

这个备份文件就可以用于恢复数据或迁移到其它地方.

```bash
$ docker run -d -v /data --name db_new training/postgres
$ docker run --volumes-from db_new -v $(pwd):/backup busybox tar xvf /backup/backup.tar
```
