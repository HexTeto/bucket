_重复的会被`[default]`中设置覆盖的没有记录, 省略了一些可以依靠字面意思理解以及不重要的设置_

__参考自[configuration reference](http://docs.openstack.org/icehouse/config-reference/content/object-expirer-configuration.html)__


###Object server configuration

__object-server.conf__

```
[DEFAULT]
bind_ip = 0.0.0.0                                                               # 服务器绑定的ip地址
bind_port = 6000                                                                # 服务器绑定的端口
bind_timeout = 30                                                               # 尝试绑定操作的超时限制(秒)
backlog = 4096                                                                  # 可以挂起的TCP连接的最大数目
user = swift                                                                    # 运行服务的用户
swift_dir = /etc/swift                                                          # Swift的配置目录
devices = /srv/node                                                             # 磁盘挂载位置的父目录
mount_check = true                                                              # 用来防止意外导致的写入root device
disable_fallocate = false                                                       # 如果底层系统不支持预分配空间的话禁用
expiring_objects_container_divisor = 86400                                      # ???
expiring_objects_account_name = expiring_objects                                # ???
workers = auto                                                                  # 更多的workers可以减小一个耗时请求对其它请求带来的负面影响
max_clients = 1024                                                              # 一个worker可以处理的最大客户端数量
log_name = swift                                                                # 记录日志时使用的标签
log_facility = LOG_LOCAL0                                                       # 日志记录工具
log_level = INFO                                                                # 日志记录等级
log_address = /dev/log                                                          # 日志文件位置
log_custom_handlers =                                                           # 自定义日志处理程序, 多个程序以","分隔
log_udp_host =                                                                  # 不设置的情况下, syslog的UDB接收器被禁用
log_udp_port = 514                                                              # 在设置了host时才生效
log_statsd_host = localhost                                                     # StatsD功能
log_statsd_port = 8125
log_statsd_default_sample_rate = 1.0                                            # 定义一个概率, 为给定事件或定时测量发送一个样品
log_statsd_sample_rate_factor = 1.0                                             # 不建议设置小于1.0的值, 如果日志记录频率太高可以调整上一项
log_statsd_metric_prefix =                                                      # 这个值会附加到每个指标中被发送
eventlet_debug = false                                                          # 开关eventlet的调试模式
fallocate_reserve = 0                                                           # ???
conn_timeout = 0.5                                                              # 外部服务的连接超时时间
node_timeout = 3                                                                # 外部服务的请求超时时间
client_timeout = 60                                                             # 客户端读一个chunk的超时时间
network_chunk_size = 65536                                                      # 限制在网络上一个chunk的大小
disk_chunk_size = 65536                                                         # 限制硬盘上一个chunk的大小


[app:object-server]
use = egg:swift#object                                                          # 设置paste.deploy的Entry point
max_upload_time = 86400                                                         # 上传一个对象允许的最大时间
slow = 0                                                                        # 如果设置>0, 那么将为PUT和DELETE请求设置一个最小完成时间(秒)
keep_cache_size = 5424880                                                       # 使用缓存的最大对象限制
keep_cache_private = False                                                      # 是否允许私有对象使用核心缓存
mb_per_sync = 512                                                               # 对于PUT请求, 每n MB同步文件
allowed_headers =                                                               # 设置对象的元数据中包含的headers
auto_create_account_prefix = .                                                  # 自动创建accounts时添加指定前缀
threads_per_disk = 0                                                            # 用于执行磁盘I/O的每块磁盘线程池大小
                                                                                # 0表示不使用线程池, 过高的值会导致读写延迟, 建议每块磁盘4线程
replication_server = false                                                      # 定义告诉服务器如何处理复制动词请求, True(1)为接受复制, False为拒绝. 不定义全接受
replication_concurrency = 4                                                     # 限制并发处理多少个传入的replication请求, 设置为0则不限制.
replication_one_per_device = True                                               # 限制每个device每次只传入一个replication请求, 设置为False则允许设备并发处理多个请求
replication_lock_timeout = 15                                                   # 设置等待一个已有的replication device lock的超时时间(秒)
replication_failure_ratio = 1.0                                                 # 如果replication子请求失败的比例超过了设定值则全部的replication将被终止
replication_failure_threshold = 100                                             # 在replication_failure_ratio被检测之前允许replication子请求的失败次数


[pipeline:main]
pipeline = healthcheck recon object-server                                      # ???


[object-replicator]
vm_test_mode = no                                                               # 表示当前使用的是虚拟机环境
daemonize = on                                                                  # 是否以守护进程模式运行replication
concurrency = 1                                                                 # number of replication workers to spawn
stats_interval = 300                                                            # 记录replication统计数据的间隔(秒)
sync_method = rsync                                                             # 同步方法
rsync_timeout = 900                                                             # 同步文件的最大持续时间
rsync_bwlimit = 0                                                               # ???
rsync_io_timeout = 30                                                           # 传递给rsync的一个I/O操作的最大持续时间(秒)
http_timeout = 60                                                               # HTTP请求的最大持续时间
lockup_timeout = 1800                                                           # 时间内没有任何复制的话尝试杀死所有workers
reclaim_age = 604800                                                            # 一个对象经过多少秒之后可以被回收
ring_check_interval = 15                                                        # 检查环的频率(秒)
recon_cache_path = /var/cache/swift                                             # 目录中统计存储了几个项目将被存储
rsync_error_log_line_length = 0                                                 # rsync的错误日志输出限制
handoff_first = False                                                           # 绝大多数情况下这项应设为False
handoff_delete = auto                                                           # 默认情况下handoff partitions会在成功复制到约定的节点后被删除, 保持默认即可


[object-updater]
interval = 300                                                                  # minimum time for a pass to take
slowdown = 0.01                                                                 # time in seconds to wait between objects


[object-auditor]
files_per_second = 20                                                           # 每秒审核的最大文件个数. 应根据系统规格进行调整, 设为0则不进行限制
bytes_per_second = 10000000                                                     # 每秒审核的最大字节数. 设为0不进行限制, 设为1则不支持并发, 同一时间只处理1个请求.
log_time = 3600                                                                 # 日志记录频率
zero_byte_files_per_second = 50                                                 # 每秒审核的最大0字节文件个数
object_size_stats =                                                             # ???


[filter:healthcheck]
use = egg:swift#healthcheck                                                     # 设置paste.deploy的ENTRY point


[filter:recon]
use = egg:swift#recon                                                           # 设置paste.deploy的ENTRY point
recon_lock_path = /var/lock                                                     # ???
```

###Object expirer configuration

__object-expirer.conf__

```
[app:proxy-server]
use = egg:swift#proxy


[filter:cache]
use = egg:swift#memcache


[fileter:catch_errors]
use = egg:swfit#catch_errors


[object-expirer]
expiring_objects_account_name = expiring_objects
report_interval = 300
processes = 0
process = 0


[pipeline:main]
pipeline = catch_errors cache proxy-server
```

###Container server configuration

__container-server.conf__

```
[DEFAULT]
bind_ip = 0.0.0.0
bind_port = 6001
bind_timeout = 30
allowed_sync_hosts = 127.0.0.1
db_preallocation = off                                                          # 开关存储空间预分配功能
eventlet_debug = False
fallocate_reserve = 0


[app:container-server]
use = egg:swift#container
allow_versions = False                                                          # 开关对象版本控制功能


[pipeline:main]
pipeline = healthcheck recon container-server


[container-replicator]
per_diff = 1000                                                                 # 限制items数量来获得每个差异?
max_diffs = 100                                                                 # 设置replicator同步数据库花费的时间上限
run_pause = 30                                                                  # 等待replication之间传输的时间(秒)


[container-updater]
account_suppression_time = 60                                                   # Seconds to suppress updating an account that has generated an error


[container-auditor]
containers_per_second = 200                                                     # 每秒审核的最大容器数量


[container-sync]
sync_proxy = http://10.1.1.1:8888,http://10.1.1.2:8888                          # 如果使用http代理则设置代理服务器地址. 默认没有代理服务器
container_time = 60                                                             # 限制同步每个容器花费的最大时间


[filter:healthcheck]
use = egg:swift#healthcheck
disable_path =


[filter:recon]
use = egg:swift#recon
```

###Account server configuration

__account-server.conf__

```
[DEFAULT]
bind_ip = 0.0.0.0
bind_port = 6002
bind_timeout = 30
mount_check = True
disable_fallocate = False
fallocate_reserve = 0


[account-server]
use = egg:swift#account
replication_server = False


[pipeline:main]
pipeline = healthcheck recon account-server


[account-replicator]
error_suppression_interval = 60                                                 # 错误恢复时限(秒)
error_suppression_limit = 10                                                    # 错误计数限制


[account-auditor]
accounts_per_second = 200                                                       # 每秒审核accounts的最大个数, 设为0则不做限制


[account-reaper]
delay_reaping = 0                                                               # 通常reaper会立即删除已经被删除的accounts的信息, 设定该值可以延迟这个操作(秒)
reap_warn_after = 2592000                                                       # reaper执行前发出警告的时间(秒)?


[filter:healthcheck]
use = egg:swift#healthcheck


[filter:recon]
use = egg:swift#recon
```

###Proxy server configuration

__proxy-server.conf__

```
[DEFAULT]
bind_ip = 0.0.0.0
bind_port = 80
expose_info = True                                                              # 是否允许通过HTTP方法 GET /info 获取配置信息
admin_key = SECRET_ADMIN_KEY                                                    # 默认为空, 大多数情况下可以设置成 egg:swift#proxy
disallowed_sections = container_quotas, tempurl                                 
cert_file = /etc/swift/proxy.crt                                                # 启动SSL相关, 只应在测试时设置它
key_file = /etc/swift/proxy.key                                                 # 启动SSL相关, 只应在测试时设置它


[app: proxy-server]
use = egg:swift#proxy
recheck_account_existence = 60                                                  # cache timeout in seconds to send memcached for account existence
recheck_container_existence = 60                                                # cache timeout in seconds to send memcached for container existence
object_chunk_size = 8192
client_chunk_size = 8192
node_timeout = 10
recoverable_node_timeout = node_timeout                                         # ???
post_quorum_timeout = 0.5
allow_account_management = False                                                # 设置为"True"则任何授权用户都可以创建或删除account, "False"则所有人都不可以
object_post_as_copy = True                                                      # 设为"True"打开fast post功能, 只有元数据创建新的存储, 原始数据保持, 这会影响sync
account_autocreate = False                                                      # 设为"True"当不存在于swift中的account获得授权则自动创建其存储目录
max_containers_per_account = 0                                                  # 限制每个account可包含的最大containers数量, 默认为0不做限制
max_containers_whitelist =                                                      # 可以超过上一项限制的白名单列表
deny_host_headers =                                                             # 设置在这里的hosts headers列表将被拒绝
put_queue_depth = 10                                                            # PUT队列的深度, 过高的值会造成写延迟
sorting_method = affinity                                                       # Storage nodes可以通过三种方式选择: shuffle(随机), affinity(亲和力), timing(延迟)
                                                                                # 无论采用何种方式, 还是会随机选择equally-sorting nodes以均衡负载
timing_expiry = 300                                                             # 当sorting_method = timing时生效, 设置延迟阀值
max_large_object_get_time = 86400                                               # 为了获取大对象允许的最大连接时间限制(秒)
request_node_count = 2 * replicas                                               # 设置一个normal request联系的Storage nodes数量
read_affinity = r1z1=100, r1z2=200, r2z1=300, r2z2=400                          # r<n>z<m> = region n, zone m. 这里的值设置更低的数字将拥有更高的优先级
write_affinity = r1                                                             # 意义同上, 写亲和力在处理PUT请求时会优先写到设置的region和zone中, 然后才是其它节点
write_affinity_node_count = 2 * replicas                                        # 设置优先处理请求的local nodes(write_affinity中设置的regions和zones)的个数
swift_owner_headers = x-container-read, x-container-write,                      # 这些值在swift_owners中被用于auth system.
x-container-sync-key, x-container-sync-to, x-account-meta-temp-url-key,
x-account-meta-temp-url-key-2, x-account-access-control


[pipeline:main]
pipeline = catch_errors gatekeeper healthcheck proxy-logging cache              # pipeline用来给各种中间件创建入口
container_sync bulk tempurl slo dlo ratelimit container-quotas                  # 这里为了使用Keystone作为认证系统, 需要将"tempauth"改为"authtoken keystoneauth"
account-quotas proxy-logging proxy-server authtoken keystoneauth                # pipeline变量的值有一定的顺序要求, 会在后文中提到


[filter:account-quotas]
use = egg:swift#account_quotas


[filter:authtoken]                                                              # 这里配置keystone作为认证系统需要首先配置并启动keystoneauth middleware
auth_host = $KEYSTONE_HOST                                                      # 并确定在"[pipeline:main]"中设置了"authtoken keystoneauth"
auth_port = 35357
auth_protocol = http
auth_uri = http://$KEYSTONE_HOST:5000/
admin_tenant_name = service
admin_user = swift
admin_password = $SWIFT_PASS
delay_auth_decision = 1
cache = swift.cache
include_service_catalog = False


[filter:keystoneauth]
use = egg:swift#keystoneauth
operator_roles = admin, swiftoperator                                           # 指定哪些用户可以拥有管理tenant, 创建container以及为其它用户设定ACL的权限
reseller_admin_role = ResellerAdmin                                             # 指定哪些用户可以拥有创建和删除accounts的权限


[filter:cache]
use = egg:swift#memcache
memcache_servers = $MEMCACHE_HOST_0:11211, $MEMCACHE_HOST_1:11211, ...          # memcacheed servers的IP:Port
memcache_serialization_support = 2                                              # 设置memcache的序列化和反序列化方法, 默认2只使用JSON进行序列化操作
memcache_max_connections = 2                                                    # memcache服务器上每个worker的最大连接数


[filter:catch_errors]
use = egg:swift#catch_errors


[filter:dlo]                                                                    # Dynamic Large Object(DLO) support
use = egg:swift#dlo
rate_limit_after_segment = 10                                                   # 下载一个被分割的大对象时, 从第几个segment之后开启速率限制
rate_limit_segments_per_sec = 1                                                 # 限制每秒提供几个segments, 设为0则不做限制
max_get_time = 86400                                                            # 对于GET请求的时间限制


[filter:gatekeeper]
use = egg:swift#gatekeeper


[filter:healtchcheck]
use = egg:swift#healthcheck


[filter:list-endpoints]
use = egg:swift#list_endpoints
list_endpoints_path = /endpoints/


[filter:proxy-logging]
use = egg:swift#proxy_logging
access_log_udp_host = $CONTROLLER_HOST                                          # 这里如何设置日志选项, 将会覆盖[DEFAULT]中的设置(在默认章节没有access_前缀)
access_log_udp_port = 514                                                       # access_udp_host的设置会优先于access_log_address
log_statsd_valid_http_methods =
GET, HEAD, POST, PUT, DELETE, COPY, OPTIONS                                     # 允许哪些方法被StatsD记录, 不在此列出的方法会标记为"BAD_METHOD"
```

###Proxy server memcache configuration

__memcache.conf__

```
[memcache]                                                                      # memcache可以被设置在单独的配置文件里
memcache_servers =                                                              # 也可以配置在proxy-server.conf的[filter:cache]部分
memcache_serialization_support =                                                # 如果不配置memcache则使用其自身配置文件的设置
memcache_max_connections =
```

###Rsyncd configuration

__rsyncd.conf__

```
[account]
max connections = 2
path = /srv/node
read only = False
lock file = /var/lock/account.lock


[container]
max connections = 4
path = /srv/node
read only = False
lock file = /var/lock/container.lock


[object]
max connections = 8
path = /srv/node
read only = False
lock file = /var/lock/object.lock
```

###Configure Object Storage features

####Object Storage zones

数据分布: Regions > Zones > Servers > Drives.
如果部署了多个Regions, Swift会通过Regions来存储对象, 其副本尽可能分布在Region内的不同Zones里; 当只剩1个可用Zone时, 数据会分布于不同的Servers;
以此类推最终数据分布在不同的Drives上.

Regions根据设备间的延迟或其它网络原因, 将设备进行广域地分隔.
Zones则是一个人为设定的任意区域, 管理员通过划分zones来保障隔离级别. 它可能是一间机房, 也可能是一个机柜上的一组服务器.
Servers则通常定义为一个固定的IP/Port.
Drives就是Server上根据mount point来区别的存储卷.

在一个产品级的部署中, 应保证数据副本分布在不同的Zones中, 并且每个Zone都有各自独立的电源等设施以提供一个主机级别的冗余. 这样能够使单个服务器进行停机维护时扔保证数据的可用性.

####Temporary URL

允许创建一个临时地址用来指向下载某个对象. 即分享链接功能.

__要启用该功能需要在`proxy-server.conf`中`[pipeline:main]`下的`pipeline`变量添加`tempurl`入口, 其它的中间件启用方式同理.__
__`tempurl`需要定义在`dlo`, `slo`和`auth filter(s)`之前.__
_我们使用Keystone所以这里的`auth filter(s)`指的是`authtoken`和`keystoneauth`, 下文同样_
_所有的`[filter:xxx]`代码块都可以添加在`proxy-server.conf`中_

配置选项如下:

```
[filter:tempurl]
use = egg:swift#tempurl
methods = GET HEAD PUT                                                          # 允许Temporary URLs执行哪些HTTP方法
incoming_remove_headers = x-timestamp                                           # 传入请求中需要删除的headers
incoming_allow_headers =                                                        # incoming_remove_headers中的例外
outgoing_remove_headers = x-object-meta-*                                       # 传出的响应中需要删除的headers, 支持通配符"*"来进行匹配
outgoing_allow_headers = x-object-meta-public-*                                 # 作为outgoing_remove_headers中的例外被允许的项
```

####Domain Remap

域名重映射中间件可以转换container和account的域名部分到路径参数使Proxy可以解析.
配置选项如下:

```
[filter:domain_remap]
use = egg:swift#domain_remap
storage_domain = example.com
path_root = v1
reseller_prefixes = AUTH
```

####CNAME lookup

CNAME查找中间件通过查找CNAMErecord来识别主机头中包含的未知域名, 组件依赖`python-dnspython`.
配置选项如下:

```
[filter:cname_lookup]
use = egg:swift#cname_lookup
storage_domain = example.com
lookup_depth = 1                                                                # CNAMES是可递归的, 所以要指定搜索深度
```

####Name Check filter

名称检查器会拒绝任何包含非法字符和不合格长度的路径.

_需要在`pipeline`中被定义在`proxy-server`之前_

配置选项如下:

```
[filter:name_check]
use = egg:swift#name_check
forbidden_chars = `?^%<>                                                        # 这里定义的字符将不允许用作Name
maximum_length = 255                                                            # Name的最大长度
forbidden_regexp = /\./|/\.\./|/\.$|/\.\.$                                      # 禁止的正则表达式语法
```

####Constraints

用来更改Swift的内部限制, 会更新`swift.conf`中`[swift-constraints]`的值.
__修改这些参数要小心, 它们会直接影响整个集群的性能.__

配置选项如下:

```
max_file_size = 5368709122                                                      # 设定允许单个对象的最大体积(bytes), 该参数也作用在一个大对象的若干个segments上.
max_meta_name_length = 128                                                      # 在utf-8编码下, 元数据报头的名称部分的最大长度(bytes)
max_meta_value_length = 256                                                     # 在utf-8编码下, 元数据值的最大长度
max_meta_count = 90                                                             # 单个account, container, 或object可存储的元数据的键的最大个数
max_meta_overall_size = 4096                                                    # 在utf-8编码下, 元数据(keys + values)的最大体积(bytes)
max_header_size = 8192                                                          # 在utf-8编码下, 每个报头的最大体积(bytes)
max_object_name_length = 1024                                                   # 在utf-8编码下, 对象名称的最大长度(bytes)
container_listing_limit = 10000                                                 # container listing request返回的最大数量
account_listing_limit = 10000                                                   # account listing request返回的最大数量
max_account_name_length = 256                                                   # 在utf-8编码下, 账户名称的最大长度(bytes)
max_container_name_length = 256                                                 # 在utf-8编码下, 容器名称的最大长度(bytes)
```

####Cluster Health

`swift-dispersion-report`工具用来衡量整体集群的健康状况. 它的原理是检查容器和对象是否被储存在了适当的位置, 比如如果1个对象有3个副本, 如果其中只有2个存储在了不同的故障域内, 则该对象的健康程度就是66.66%. 单个对象的健康程度, 尤其是对于一些比较旧的对象来说, 通常能够反映它所处的整个partition的健康状况.

进行健康检查需要为其创建一个新的account, 然后使用`swift-dispersion-populate`工具创建随机的对象和容器直到它们分布到不同的partitions上.
最后使用`swift-dispersion-report`工具检查这些随机容器和对象的健康状况.

这些工具需要直接访问整个集群和ring文件. 将它们安装在proxy node上即可. 它们使用共同的配置文件`/etc/swift/dispersion.conf`. 配置选项如下:

```
[dispersion]
auth_url = http://localhost:8080/auth/v1.0
auth_user = test:tester
auth_key = testing
auth_url = http://localhost:5000/v2.0/
auth_user = tenant:user
auth_key = password
auth_version = 2.0
auth_type = publicURL                                                           # publicURL/internalURL 使用哪个endpoint进行验证
keystone_api_insecure = no
swift_dir = /etc/swift
dispersion_coverage = 1.0                                                       # 样品占总空间的百分比
retries = 5                                                                     # 重复次数
concurrency = 25                                                                # workers数量
container_populate = yes                                                        # 是否使用容器来测试
object_populate = yes                                                           # 是否使用对象来测试
object_report = yes
dump_json = no                                                                  # 是否以json数组输出检查报告
```

####Static Large Object(SLO) support

支持用户同时上传多个对象, 然后这些对象可以被当作一个对象被下载. SLO区别于DLO, 它不依赖于最终一致的容器列表. 取而代之是使用用户自定义的对象分段清单(a user-defined manifest of the object segments)来完成.

其配置选项如下:

```
use = egg:swift#slo
max_manifest_segments = 1000
max_manifest_size = 2097152
min_segment_size = 1048576
rate_limit_after_segment = 10                                                   # 和DLO中相同选项同理
rate_limit_segments_per_sec = 0
max_get_time = 86400
```

####Container Quotas

容器配额中间件可以实现为容器添加简单的配额以限制对象的PUT操作.
通过给容器添加元数据值来设置配额:

  - X-Container-Meta_Quota-Bytes:   限制容器的最大体积(bytes)
  - X-Container-Meta-Quota-Count:   限制容器的最大对象数量

_需要在`pipeline`中被定义在`auth filter(s)`之后_

```
[filter:container-quotas]
use = egg:swift#container_quotas
```

与此类似的还有Account Quotas中间件

```
[filter:account-quotas]
use = egg:swift#account_quotas
```

####Bulk Delete

批量删除中间件可以允许在一次请求中批量删除account中的多个文件. DELETE请求的主体是一个按行分隔的列表, 每行一个要删除的文件. 文件必须以URL的格式列出.
当发送一个DELETE请求, 如果成功删除(或文件不存在)则返回HTTPOk, 如果有文件删除失败, 则返回HTTPBadGateway.

_需要在`pipeline`中被定义在`ratelimit`和`auth filter(s)`之前_

配置选项如下:

```
[filter:bulk]
use = egg:swift#bulk
max_containers_per_extraction = 10000
max_failed_extractions = 1000
max_deletes_per_request = 10000
max_failed_deletes = 1000
yield_frequency = 10
delete_container_retry_count = 0
```
