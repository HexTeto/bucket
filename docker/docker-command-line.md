+ docker -h, --help: 用例帮助

+ docker: 命令列表
  + attach: attach用来对运行中的容器进行操作
  + build: 从Dockerfile和context构建新镜像
    + -t, --tag="": 添加Repository的name和可选的tag
    + -q, --quiet=false: 是否显示容器生成的详细信息，默认false
    + --no-cache: 不使用缓存
    + --rm=true: 在构建成功够删除中间容器
  + commit: 根据一个容器创建一个新镜像
    + -m, --message="": 附加一些说明信息
    + -a, --author="": 标注镜像作者
  + cp: 从容器的文件系统中拷贝文件
  + diff: 列出容器文件系统发生的变化，有A(add), D(delete), C(change)三种事件
  + events: 用来监听服务器上的实时事件，时间戳的格式可以类似这样"2014-03-06 15:49:29"
    + --since="": 定义开始记录事件的时间戳
    + --until="": 定义停止记录事件的时间戳
  + export: 导出容器到stdout，可以重定向为一个tar arhcive，比如export x > y.tar
  + history: 显示镜像的历史
    + --no-trunc=false: 不缩短输出信息
    + -q, --quiet=false: 只显示数字ID
  + images: 显示镜像
    + -a, --all=false: 显示所有的镜像包括中间层
    + --no-trunc=false: 不缩短输出信息
    + -t, --tree=false: 以树结构来输出镜像信息
    + -v, --viz=flase: 把镜像的依赖关系绘制成图并通过管道符号保存到图片文件, 例如`docker images -viz | dot -T png -o docker.png`
  + import: 创建一个空的镜像并导入指定的tarball，使用参数`-`可以从stdin读
  + info: 查看Docker相关系统信息
  + inspect: 默认情况下以JSON数组的形式返回镜像或容器的底层信息
    + -f, --format="": 可以格式化输出
  + kill: 终止一个正在运行的容器
    + -s, --signal="KILL": 发送指定的信号给容器
  + load: 通过stdin从tar归档文件读取镜像，比如`docker load < ubuntu.tar`
    + -i, --input="": 直接从".tar"读取镜像，`docker load -i ubuntu.tar`
  + login: 注册或登录指定的registry服务器，比如`docker login localhost:8888`
    + -e, --email="": Email
    + -p, --password="": Password
    + -u, --username="": Username
  + logs: 获取容器的日志
    + -f, --follow=false: 结合"attach"的方法，输出当前日志后会继续输出新的stdout和stderr
  + port: 查找指定容器中公开的端口
  + ps: 查看容器
    + -a, --all=false: 显示所有的容器包括处于停止状态下的
    + --before="": 只显示指定"ID"或"Name"之前创建的容器
    + l, --latest=false: 只显示最新创建的容器
    + n=-1: 显示最后n个创建的容器
    + --no-trunc=false: 不缩短输出信息
    + -q, --quiet=false: 只显示数字ID
    + -s, --size=flase: 显示容器尺寸，不能与`-q`同时使用
    + --since="": 只显示指定"ID"或"Name"之后创建的容器
  + pull: 从registry服务器上下载仓库或镜像
  + push: 上传镜像或者仓库到指定的registry服务器
  + restart: 重启正在运行的容器
    + -t, --time=10: 设定重启延迟秒数
  + rm: 删除容器
    + -l, --link="": 删除链接而不删除真正的容器
    + -f, --force=false: 强制删除正在运行的容器
    + -v, --volumes=false: 删除容器的同时删除与它关联的卷
  + rmi: 删除镜像
    + -f, --force=false: 强制删除镜像
    + --no-prune=false: 不删除未标记的parents
  + run: 在一个新容器中执行run指定的命令[详细参考](http://docs.docker.io/reference/run/)
    + -a, --attach=map[]: 附加到stdin, stdout or stderr
    + -c, --cpu-shares=0: CPU共享百分比
    + --cidfile="": 将容器的ID写入指定文件
    + -d, --detach=false: 独立模式，容器会在后台运行
    + -e, --env=[]: 设置环境变量
    + --env-file="": 配置环境变量文件
    + -h, --hostname="": 容器的hostname
    + -i, --interactive=false: 交互模式
    + --privileged=false: 给予该容器扩展权限
    + -m, --memory="": 内存限制(format: number + unit)
    + -n, --networking=true: 启用网络功能
    + -p, --publish=[]: 为容器映射一个网络端口
    + --rm=false: 在退出的时候自动删除容器，与"-d"冲突
    + -t, --tty=false: 分配伪终端
    + -u, --user="": Username or UID
    + --dns=[]: 为容器指定自定义的DNS-server
    + --dns-search=[]: 为容器指定自定义的DNS-search-domains
    + -v, --volume=[]: 使用`host-path:container-path:rw|ro`绑定挂载一个目录或文件
    + --volumes-from="": 从指定容器挂载所有卷
    + --entrypoint="": 覆盖镜像中默认的ENTRYPOINT
    + -w, --workdir="": 指定在容器中的工作目录
    + --lxc-conf=[]: 添加自定义的lxc选项
    + --sig-proxy=true: 接收到的所有信号proxify给进程，即使在非tty模式
    + --expose=[]: 在容器中暴露一个端口，但不直接开放给宿主机访问
    + --link="": 添加一个链接到另外的容器里
    + --name="": 为容器指定一个名字
  + save: 保存镜像到stdout, 可以重定向到一个tar archive
    + -o, --output="": 写进指定文件代替stdout
  + search: 在仓库中搜索镜像
    + --no-trunc=false: 不缩短输出
    + -s, --stars=0: 只显示大于指定stars数量的镜像
    + -t, --trusted=false: 只显示受信任的镜像
  + start: 启动一个stopped状态的容器
    + -a, --attach=false: attach容器的stdout/stderr并转发信号给进程
    + -i, --interactice=false: attach容器的stdin
  + stop: 停止一个running状态的容器(发送SIGTERM然后在等待时间过后发送SIGKILL)
    + -t, --time=10: 指定发送SIGKILL之前等待的秒数
  + tag: 给镜像添加tag
    + -f, --force=false: 强制
  + top: 查找容器中正在运行的进程
  + version: 显示版本信息
  + wait: Block until a container stops, then print its exit code




[完整参考文档](http://docs.docker.io/reference/commandline/cli/)
