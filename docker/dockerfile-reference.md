Docker可以通过`docker build`命令从一个文本文件_Dockerfile_中读取命令来构建一个镜像.


###Format

Dockerfile的通常格式如下:

    #comment
    INSTRUCTION arguments

- 在Dockerfile中命令是不区分大小写的, 但是为了与参数区分方便, 约定使用大写
- 所有的Dockerfile中第一个指令必须是`FROM`, 它用来指定从哪个基础镜像来构建新镜像
- 以"#"开头的行视为注释行, 而"#"在其它地方出现会被当做普通的arguments


####FROM

    FROM image[:tag]

`FROM`指令为后续的指令指定了使用的基础镜像, 一个有效的Dockerfile中可以出现多个`FROM`指令用以创建多个镜像.
在构建过程中会在每一次新的`FROM`指令之前输出上一个镜像的ID.

如果不给`FROM`指定`tag`, 那么默认会使用"latest"标记的镜像.


####MAINTAINER

    MAINTAINER author's name

使用`MAINTAINER`指令来为生成的镜像署名作者.


####RUN

`RUN`指令有两种格式:

  - `RUN command` (命令运行在shell下, 等价于`RUN /bin/sh -c command`)
  - `RUN ["executable", "param1", "param2"]` (exec form)

`RUN`指令会在当前镜像的顶层创建一个新的层来执行命令并返回结果, 由此产生的新镜像继续作用于下一个指令.
分层执行命令并commit的这个过程可以让我们从镜像历史的任意一个节点来创建容器, 类似于版本控制.


####CMD

`CMD`有三种格式:

  - `CMD ["executable", "param1", "param2"]` (首选格式)
  - `CMD ["param1", "param2"]` (传入参数给ENTRYPOINT)
  - `CMD command param1 param2` (shell)

一个有效的Dockerfile中只能包含一个`CMD`指令, 如果存在多个那么只有最后一个生效.
`CMD`主要用来给容器指定一个默认行为, 它一般是一个可执行程序, 如果只传入参数, 则必须要指定`ENTRYPOINT`

在使用exec格式时注意需提供可执行程序的完整路径比如:

    CMD ["/usr/bin/wc", "--help"]

`CMD`可以与`ENTRYPOINT`搭配使用, 比如:

    ENTRYPOINT["/usr/bin/wc"]
    CMD["--help"]

 _用户在执行`docker run`时如果指定了行为, 那么`CMD`定义的默认行为将会被覆盖._
 
 > __Note__: don't confuse `RUN` with `CMD`. `RUN` actually runs a command and commits the result;
 > `CMD` does not execute anything at build time, but specifies the intended command for the image.

 
 ####EXPOSE
 
     EXPOSE port [port...]

`EXPOSE`指令告知Docker在运行容器时将监听指定的网络端口, 可以使用links来连接这些容器或将指定端口重定向到宿主机


####ENV

    ENV key value

`ENV`指令用来配置环境变量, 这些变量将作用于之后所有`RUN`指令和由该镜像启动的容器.
可以通过`docker inspect`来查看并通过`docker run --env key=value`来改变它们的值.


####ADD

    ADD src dest

`ADD`指令会从宿主机"src"位置复制文件到容器文件系统的"dest"位置.

> __Note__: If you build using STDIN (`docker build - < somefile`),
> there is no build context, so the Dockerfile can only contain an URL based ADD statement.

> __Note__: If your URL files are protected using authentication,
> you will need to use an `RUN wget`, `RUN curl`
> or other tool from within the container as ADD does not support authentication.

复制的文件会遵循以下一些规则:

  - 路径"src"必须是一个上下关联的路径(`ADD ../somthing`是无效的), 在构建过程中这些相关目录同样会被发送到docker daemon.
  - 如果"src"是一段URL并且"dest"路径以"/"结尾, 那么filename从这段URL中自动判定并被下载到"dest/filename"
  - 如果"src"是一个目录, 那么整个都会被复制, 包括文件系统元数据
  - 如果"src"是一个以公认的压缩格式保存的本地文件(gz, bz2...), 那么它会被解压为一个目录. 从URL获取的远程资源不会被解压.
  - 如果"src"是任何其它类型的文件, 它会连同其元数据被复制.
  - 如果"dest"路径不以"/"结尾, 它将被视为一个普通文件, 其内容被写到"dest".
  - 如果"dest"路径不存在, 其路径中所有缺失的目录将会被创建.


####ENTRYPOINT

`ENTRYPOINT`指令有两种格式:

  - `ENTRYPOINT ["executable", "param1", "param2"]` (首选格式)
  - `ENTRYPOINT command param1 param2` (shell)

一个有效的Dockerfile只能包含一个`ENTRYPOINT`, 如果存在多个时, 只有最后一个生效.

"Entry-Point"本身就有切入点的意思, `ENTRYPOINT`指令会为容器添加一个入口, 和`CMD`不同, 它不会被`docker run`指定的命令覆盖.
设置了切入点后, 比如`docker run ubuntu -h`这个命令, `-h`会作为参数传入给`ENTRYPOINT`指定的程序.

参数可以依照首选格式和可执行程序一同定义在一个JSON数组中或者定义在`CMD`中. 前者定义的参数不会被`docker run`传入的参数覆盖.
后者则会在`docker run`传入参数时被覆盖.


####VOLUME

    VOLUME ["/data"]

`VOLUME`指令会创建一个指定名称的挂载点来挂载宿主机或者其它容器上的目录


####USER

    USER daemon

`USER`指令用来设置运行镜像时的username或UID


####WORKDIR

    WORKDIR /path/to/workdir

`WORKDIR`指令给其后的`RUN`, `CMD`和`ENTRYPOINT`设置工作目录.
在Dockerfile中它可以出现多次, 如果定义了一段相对路径, 那么它是相对于上一个`WORKDIR`的.


####ONBUILD

    ONBUILD [INSTRUCTION]

`ONBUILD`指令为镜像添加一个触发器, 当这个镜像作为另一个镜像的基础镜像时被执行. 它用来构建一个镜像作为其它镜像的基础镜像使用.
例如, 构建一个应用开发环境镜像, 然后在其之上构建应用镜像.

它的工作原理如下:

  1. 当遇到一个`ONBUILD`指令则添加一个触发器到镜像构建的元数据, 这个指令并不影响当前的构建.
  2. 构建结束后, 所有的触发器列表被存储到镜像并可以通过`docker inspect`来查看.
  3. 该镜像可能通过`FROM`指令被用作基础镜像来构建新的镜像, 下游构建器查找`ONBUILD`触发器并执行它们.
  如果触发器执行失败则`FROM`指令中断并导致构建失败, 只有所有触发器执行成功, 则构建过程会继续进行.
  4. 触发器执行后会在最终得到的镜像中被清除, 也就是说不会继续被基于结果镜像而构建的镜像继承.

一个触发器可以被写成这样:

    [...]
    ONBUILD ADD . /app/src
    ONBUILD RUN /usr/local/bin/python-build --dir /app/src
    [...]

> __Warning__: 链式的`ONBUILD ONBUILD ...`这样的命令格式是不被允许的.

> __Warning__: `ONBUILD`不能触发`FROM`或`MAINTAINER`指令.


####Example:

    FROM    ubuntu
    MAINTAINER test <test@docker.io>
    
    # make sure the package repository is up to date
    RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
    
    # Install vnc, xvfb in order to create a 'fake' display and firefox
    RUN apt-get update
    RUN apt-get install -y x11vnc xvfb firefox
    RUN mkdir /.vnc
    
    # Setup a password
    RUN x11vnc -storepasswd 123456 ~/.vnc/passwd
    
    # Autostart firefox (might not be the best way, but it does the trick)
    RUN bash -c 'echo "firefox" >> /.bashrc'
    
    EXPOSE 5900
    ENTRYPOINT ["x11vnc"]
    CMD ["-forever", "-usepw", "-create"]
    
    #Multiple images
    #FROM    ubuntu
    #[...]