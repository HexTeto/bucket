实验环境

```yaml
master:
    addr: '172.16.1.10'
    user: 'vagrant'
    pass: 'mysecret'
servant:
    addr: '172.16.1.11'
    user: 'vagrant'
    pass: 'mysecret'
```

## Ansible 配置

编辑文件 `/etc/ansible/hosts` 修改主机与组配置:

```py
[master]
172.16.1.10

[servant]
172.16.1.11    ansible_ssh_private_key_file = '/srv/ssh_keys/auth.key'
172.16.1.12    ansible_ssh_private_key_file = '/srv/ssh_keys/auth.key'

[webserver]
www[01:03].mycloud.org

[webserver:port]
http_port = 8080
ssh_user = 'vagrant'
ssh_port = 2143

```

组变量与主机变量也可以分别保存在单独的文件中, 比如 `/etc/ansible/group_vars/servant`.
组变量和主机变量文件既可以保存在 `playbook` 目录中, 也可以保存在 `inventory` 目录中,
如果同时存在, `inventory` 优先级高于 `playbook`.

通过 `ansible <host> -m ping` 命令测试主机连通性.
默认情况下该命令使用 `root` 用户,
如果本地主机与远程主机之间未配置 SSH 信任证书报错则需要 `-k` 选项并提供对应的 SSH 密码.
如果要使用特定用户访问, 比如 `vagrant`, 则指定 `-u vagrant -sudo` 选项.


#### 配置 SSH 密钥对

为了避免每次都要输入密码, 可以使用 `ssh-keygen` 和 `ssh-copy-id` 实现快速证书生成和公钥下发.

```bash
# on master host generate a key pair
ssh-keygen -t rsa

# /usr/bin/ssh-copy-id [-i [identity_file]] [user@]machine
ssh-copy-id -i $HOME/.ssh/id_rsa.pub vagrant@172.16.1.11
ssh-copy-id -i $HOME/.ssh/id_rsa.pub vagrant@172.16.1.12
ssh-copy-id -i $HOME/.ssh/id_rsa.pub vagrant@172.16.1.13
```

下发的公钥在目标主机上保存为 `$HOME/.ssh/authorized_keys`


#### 匹配目标

命令格式为: `ansible <pattern> -m <module> -a <arguments>`

匹配目标 `<pattern>` 遵照以下规则:
- 匹配目标为组名, 主机名或 IP 地址, 之间用 `:` 分隔.
- 支持通配符以及正则表达式匹配
- 支持逻辑操作符: 与 `&`, 非 `!`
- 支持变量匹配 `{{var_name}}`

Ansible 提供了大量模块, 详细参考[文档](http://docs.ansible.com/modules.html).
配置部分用来进行连通性测试的 `ansible <host> -m ping` 命令就是加载了 `ping` 模块.
也可以使用 `-M` 以指定模块路径的形式加载模块.

<br>
<br>

## Playbook

和其它同类软件类似, playbook 语法同样基于 [YAML](http://en.wikipedia.org/wiki/YAML).
在 YAML 中几个简单的要点:
- 空格没有数量限制 (不要使用制表符), 同级元素左对齐即可.
- 内容避免掺杂锚点 `&` 和引用 `*` 以防混淆.
- 字符串不需要在引号之内, 需要强制内容为某种数据类型时可以使用引号或严格类型标签 `!!`
- 除了 block format, 也可以支持 JSON 语法的 inline format

```yml

# filename: nginx.yml

--- # block format
hosts: webservers
    vars:
        worker_processes: 1
        num_cpus: 1
        max_open_file: 16384
        root: !!str /srv/we     # 类型标签声明为字符串类型
        remote_user: "vagrant"  # 引号声明为字符串类型
    tasks:
      - name: installation
        apt: pkg=nginx, state=latest
      - name: configuration
        template: src=/home/ansibleLab/nginx.conf dest=/etc/nginx/nginx.conf
        notify: restart service
      - name: verify
        service: name=nginx state=started
    handlers:
      - name: restart service   # handlers 通过 name 标签来触发
        service: name=nginx state=restarted
```

定义好的 playbook 使用 `ansible-playbook <playbook_file.yml> [arguments]` 执行.

常用参数有:
- `-u REMOTE_USER`: 指定执行远程主机用来执行的用户
- `--syntax-check`: 检查语法错误
- `--list-hosts playbooks`: 显示匹配到的主机列表
- `-T TIMEOUT`: 定义 playbook 执行的超时时间
- `--step`: 以单任务分布运行
- `-help`: 获取更多帮助信息


#### Roles and Include Statements

Ansible 支持从外部引用配置方便将业务流程抽象后复用.

```yml

# conf.d/proc.yml

- name: placeholder foo
  command: /bin/foo
- name: placeholder bar
  command: /bin/bar

# task.yml

tasks:
    - include: conf.d/proc.yml
    - include: conf.d/user.yml user=vagrant   # 也可以传递参数到引用, 称为 "parameterized include"

--- # inline format
tasks:
    - {include: conf.d/proc.yml}
    - {include: conf.d/user.yml, user: vagrant, ssh_keys: ['keys/one.txt', 'keys/two.txt']}
```
