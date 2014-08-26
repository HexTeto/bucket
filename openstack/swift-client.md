#Object-Storage command-line client

####Usage

`$ swift help COMMAND`

####Subcommands

- __delete__: 删除容器或对象
- __download__: 下载对象
- __list__: 列出account/conatiners 或者 container/objects
- __post__: 更新containers或objects的元数据信息
- __stat__: 显示account, container, object 的状态信息
- __upload__: 上传文件或目录到指定的container
- __capabilities__: 列出可用的集群功能


####Swift examples

```
swift -A https://auth.api.example.com/v1.0 -U user -K api_key stat -v
swift --os-auth-url https://api.example.com/v2.0 --os-tenant-name admin \
    --os-storage-url https://storage_node.com:8080/v1/AUTH_abcd1234efgh5678 \
    list
swift list --lh
```

####Optional arguments

- `--version` : 显示版本信息
- `-h`, `--help` : 显示帮助信息
- `-s`, `--snet` : 使用SERVICENET内部网络
- `-v`, `--verbose` : 显示详细信息
- `--debug` : 显示`curl`命令和所有HTTP查询的结果
- `--info` : 显示`curl`命令和所有HTTP查询中返回错误的结果
- `-q`, `--quiet` : 抑制status输出
- `-A AUTH`, `--auth=AUTH_URL` : 获取auth token
- `-V AUTH_VERSION`, `--auth-version=AUTH_VERSION` : 指定认证系统的版本, 默认1.0
- `-U USER`, `--user=USER` : 为了获取token的用户名
- `-K KEY`, `--key=KEY` : 为了获取token的密钥(和 -U 组合使用)
- `-R RETRIES`, `--retries=RETRIES` : 连接失败时重试的次数
- `--os-username=<auth-username>` : OpenStack username. defaults to `env[OS_USERNAME]`
- `--os-password=<auth-password>` : OpenStack password. defaults to `env[OS_PASSWORD]`
- `--os-tenant-id=<auth-tenant-id>` : OpenStack TenantID. `env[OS_TENANT_ID]`
- `--os-tenant-name=<auth-tenant-name>` : OpenStack TenantName. `env[OS_TENANT_NAME]`
- `--os-auth-url=<auth-url>` : OpenStack auth URL. `env[OS_AUTH_URL]`
- `--os-auth-token=<auth-token>` : OpenStack token. `env[OS_AUTH_TOKEN]`
- `--os-storage-url=<storage-url>` : `env[OS_STORAGE_URL]`, 与"auth-token"配合使用可绕过"user/pass"认证
- `--os-region-name=<region-name>` : `env[OS_REGION_NAME]`
- `--os-service-type=<service-type>` : `env[OS_SERVICE_TYPE]`
- `--os-endpoint-type=<endpoint-type>` : `env[OS_ENDPOINT_TYPE]`
- `--os-cacert=<ca-certficate>` : `env[OS_CACERT]`, 用来核实TLS(https)服务器证书
- `--insecure` : `env[SWIFTCLIENT_INSECURE]`, 启动则允许客户端访问服务不需要经过SSL验证

##swift delete command

####Usage

`$ swift delete`

####Positional arguments

- __container__
- __[object]__

####Optional arguments

- `--all` : 删除所有容器和对象
- `--leave-segments` : 不删除manifest中列出的文件
- `--object-threads <threads>` : 删除对象操作的线程数(default=10)
- `--container-threads <threads>`: 删除容器操作的线程数(default=10)

##swift download command

####Usage

`$ swift download`

####Positional arguments

- __container__

> download a whole account, omit this and specify `--all`

- __[object]__

> omit this to download all objects from the container

####Optional arguments

- `--all` : download everything in the account
- `--marker` : marker to use when starting a container or account download
- `--prefix <prefix>` : 只下载以指定前缀开头的文件
- `--output <out_file>` : 进行单个文件下载时, 将输出重定向到指定文件, 指定`-`重定向至标准输出
- `--object-threads <threads>` : 下载对象操作的线程数(default=10)
- `--container-threads <threads>` : 下载容器操作的线程数(default=10)
- `--no-download` : 执行下载操作但是不写入磁盘
- `--header <name:value>` : 为查询添加自定义的"request header". 比如"Range"或"If-Match".
- `--skip-identical` : 跳过下载本地已存在的文件

##swift list command

####Usage

`$ swift list`

####Positional arguments

- __[container]__

> name of container to list object in

####Optional arguments

- `--long` : "Long listing format", 类似于`ls -l`命令
- `-lh` : "human readalbe format", 类似于`ls -lh`命令
- `--totals` : 与`-l`或`--lh`组合使用, 只显示汇总结果
- `--prefix <prefix>` : 只显示以指定前缀开头的文件
- `--delimiter` : roll up items with the given delimiter, for containers only.

##swift post command

####Usage

`$ swift post`

> updates meta information for the account, container, or object.
if the container is not found, it will be created automatically.

####Positional arguments

- __[container]__
- __[object]__

####Optional arguments

- `--read-acl <acl>` : READ ACL for containers. syntax: `.r:*`, `.r:-.example.com`, `account1, account2:user2`
- `--write-acl <acl>` : WRITE ACL for containers. syntax: `account1 account2:user2`
- `sync-to <sycn-to>` : Sync To for containers, for multi-cluster replication
- `sync-key <sync-key>` : Sync Key for containers, for multi-cluster replication
- `--meta <name:value>` : sets a meta data item, example: --meta Color:Blue --meta Size:Large
- `--header <header>` : set request headers. example: --header "Content-Type:text/plain"

##swift stat command

####Usage

`$ swift stat`

> displays information for the account, container, or object

####Positional arguments

- __[container]__
- __[object]__

####Optional arguments

- `--lh` : "human readable format", similar to `ls -lh`

##swift upload command

####Usage

`$ swift upload`

####Positional arguments

- __container__
- __file or directory__

####Optional arguments

- `--changed` : only upload files that have changed since the last upload
- `--skip-identical` : 跳过上传已存在文件
- `--segment-size <size>` : 指定文件分片最大尺寸(bytes)
- `--segment-container <container>` : 上传segments到指定的container
- `--leave-segments` : 这里应该是指是否覆盖旧版本的segments
- `--object-threads <threads>` : 上传完整对象的线程数(default=10)
- `--segment-threads <threads>` : 上传对象片段的线程数(default=10)
- `--header <name:value>` : set request headers
- `--use-slo` : 当与`--segment-size`组合使用, 将创建Static Large Object替代默认的DLO
- `--object-name <name>` : 对于单个文件作为文件名, 对于上传一个目录时则作为对象前缀
