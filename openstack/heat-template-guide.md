#Heat Orchestration Template(HOT) Guide

HOT用来代替Amazon的CFN, 基于YAML.
描述资源(server, floating ip, volume, etc.)之间的关系.

##Template Structure

```yaml
heat_template_version: 2014-07-21

description: Simple template to deploy a single compute instance

resources:
	my_instance:
		type: OS::Nova::Server
		properties:
			key_name: {your key-value pair}
			image: boot2docker
			flavor: m1.small
```

每个HOT模板都必须包含`heat_template_version`字段来声明当前版本,
`resources`字段来描述实例资源.
`description`是可选的, 多行的描述使用以下格式:

```yaml
	description: >
		This is how you can provide a longer description
		of your template that goes over several lines.
```

####Template input parameters

"input parameters"定义在`parameters`字段下, 允许用户在部署过程中自定义一些选项.
这样做可以使模板更易于重用.

```yaml
parameters:
	key_name:
		type: string
		label: Key Name
		description: Name of key-pair to be used for compute instance
	image_id:
		type: string
		label: Image ID
		description: Image to be used for compute instance
	instance_type:
		type: string
		label: Instance Type
		description: Type of instance (flavor) to be used.
```

在这个例子中, `key_name`, `image_id`和`instance_type`会代替`resources`中定义的`properties`.
由`get_param`函数实现.

在`parameters`中也可以通过`default`定义缺省值用来在用户未定义这些参数的时候使用.
比如下边这个例子, 定义默认的`instance_type`为"m1.small":

```yaml
parameters:
	instance_type:
		type: string
		label: Instance Type
		description: Type of instance (flavor) to be used.
		default: m1.small
```

还有一些其它有用的参数, 比如`hidden`可以隐藏一些选项的值. 通常用作用户的密码信息等.

```yaml
parameters:
	database_password:
		type: string
		label: Database Password
		description: Password to be used for database
		hidden: true
```

####Restricting user input

通过添加`constraints`字段, 定义一个限制列表, 限制用户的输入必须满足约束条件.
可以用来限制用户使用的资源数量.

```yaml
parameters:
	instance_type:
		type: string
		label: Instance Type
		description: Type of instance (flavor) to be used
		constraints:
			- allow_values: [m1.medium, m1.large, m1.xlarge]
			  description: value must be one of m1.medium, m1.large, m1.xlarge.
	database_password:
		type: string
		label: Database Password
		description: Password to be used for database
		hidden: true
		constraints:
			- length: { min: 6, max: 8 }
			  description: Password length must be between 6 and 8 characters.
			- allowed_pattern: "[a-zA-z0-9]+"
			  description: Password must consist of characters and numbers only.
			- allowed_pattern: "[A-Z]+[a-zA-Z0-9]*"
			  description: Password must start with an uppercase character.
```

在这个例子中, 我们对数据库密码的组成形式做了两次定义, 这样做不但可以使得正则表达式更简洁.
而且因为描述不同, 可以返回更精确的错误信息给用户.
在这个例子中密码是否包含非法字符和密码是否以大写字母开头是分开反馈的.


####Providing template outputs

```yaml
outputs:
	instance_ip:
		description: The IP address of the deployed instance
		value: { get_attr: [my_instance, first_address] }
```

####Structure

```yaml
heat_template_version: #datetime

description:
	# a description of the template

parameter_groups:
	# a declaration of input parameter groups and order

parameters:
	# declaration of input parameters

resources:
	# declaration of template resources

outputs:
	# declaration of output parameters
```

####Parameter Groups Section

`parameter_groups`用来关联多个参数到一个组, 注意每个参数应该只关联一次.

```yaml
parameter_groups:
	- label: <human-readable label of parameter group>
	  description: <description of the parameter group>
	  # 这里声明的参数在parameters section下定义值.
	  parameters:
		- <parameter name>
		- <parameter name>
		- ...
```

####Parameters Section

```yaml
parameters:
	parameter's name:
		type: <string | number | json | comma_delimited_list | boolean>
		label: <human-readable name of the parameter>
		default: <true | false>
		hidden: <true | false>
		constraints:
			- <parameter constraints>
```

####Parameters Constraints

```yaml
constraints:
	- <constraint type>: <constraint definition>
	  description: <constraint description>
	- ...
```

约束条件使用项目符号`- ...`分隔, 根据定义参数的`type`不同也有不同种类的限制.
```yaml
# type: string
length: { min: <lower limit>, max: <upper limit> }
# type: number
range: { min: <lower limit>, max: <upper limit> }
# 以上两种对于范围的限制都是闭区间, 最小和最大边界都被包含在内.
# 允许只定义一个边界, 但是至少要有一个边界.

# type: string | number
allowed_value: [<value0>, <value1>, <value2>, ...]
# 也支持使用YAML的列表表示法
allowed_value:
	- <value0>
	- <value1>
	- ...
# type: string
allowed_pattern: <regular expression>
```

####Pseudo Parameters

伪参数由系统为每个栈创建, 它的作用是允许引用访问栈的名称和标识符.
它们通常是`OS::stack_name`, `OS::stack_id`的形式.

####Resources Section

资源也是通过缩进的代码块来定义.

```yaml
resources:
	# 每个资源描述代码块都以resourceID开始, 这个值必须是唯一的
	<resource ID>:
		# OS::Nova::Server
		type: <resource type>
		properties:
			# 通常会定义flavor和image.
			<property name>: <property value>
		metadata:
			<resource specific metadata>
		depends_on: <resource ID or list of ID>
		update_policy: <update policy>
		deletion_policy: <deletion policy>
```

####Resource Dependencies

`depends_on`属性可以为资源定义一个或多个依赖资源, 通过resourceID来定义.

```yaml
resources:
	server1:
		type: OS::Nova::Server
		# single resource
		depends_on: server2
	server2:
		type: OS::Nova::Server
		# resources list
		depends_on: [server3, server4]
	server3:
		type: OS::Nova::Server
	server4:
		type: OS::Nova::Server
```

####Outputs Section

```yaml
outputs:
	# 输出代码块的名字必须是唯一的
	<paramerter name>:
		description: <description>
		# value通常都是通过一个内置函数来获取的. 比如{ get_attr: my_instance }
		value: <parameter value>
```

##Intrinsic Functions

####get_attr

`get_attr`函数允许引用一个资源的属性值.

```yaml
get_attr:
	- <resource ID>
	- <attribute name>
	- <key/index 1> (optional)
	- <key/index 2> (optional)
	- ...
#eg
resources:
	my_instance:
		type: OS::Nova::Server

outputs:
	instance_ip:
		description: IP address of the deployed compute instance
		value: { get_attr: [my_instance, first_address] }
	instance_private_ip:
		description: Private IP address of the deployed compute instance
		value: { get_attr: [my_instance, networks, private, 0] }
```

####get_file

`get_file`函数用于从外部文件替换字符串. 它通过REST API调用一个目录下的文件, 然后返回其实际内容.

```yaml
# content-key must be a static path or URL and not rely on intrinsic functions
get_file: <content key>

#eg
resources:
	my_instace:
		type: OS::Nova::Server
		properties:
			user_data:
				# relative path
				get_file: my_instance_user_data.sh
	my_other_instance:
		type: OS::Nova::Server
		properties:
			user_data:
				# absolute URL
				get_file: http://localhost/wordpress/my_test.sh
```

####get_param

`get_param`函数允许从其它位置引用输入参数.

```yaml
get_param:
	- <parameter name>
	- <key/index 1> (optional)
	- <key/index 2> (optional)
	- ...

#eg
parameters:
	instance_type:
		#...
	server_data:
		#...

resources:
	my_instance:
		type: OS::Nova::Server
		properties:
			flavor: { get_param: instance_type }
			metadata: { get_param: [ server_data, metadata ] }
			key_name: { get_param: [ server_data, keys, 0 ] }
```

####get_resource

`get_resource`函数允许引用模板内其它资源的定义.

```yaml
get_resource: <resource ID>
```

####list_join

`list_join`函数以指定的分隔符连接一个字符串列表.

```yaml
list_join:
	- <delimiter>
	- <list to join>
# return "one, two, and three"
list_join: [',', ['one', 'two', 'and three']]
```

####resource_facade

`resource_facade`函数允许一个"provider template"从它的父模板(或者说是供给对象)中检索数据.

```yaml
resource_facade: <data-type>
```

####str_replace

`str_replace`函数根据提供的模板字符串来构造字符串.

```yaml
str_replace:
	template: <template string>
	params: <parameter mapping>

#eg
outputs:
	Login_URL:
		description: the URL to log into the deployed application
		value:
			str_replace:
				template: http://host/MyApp
				params:
					host: { get_attr: [ my_instance, first_address ] }
```

##Resource Types

####OS::Cinder::Volume

```yaml
resources:
	my_instace:
		type: OS::Cinder::Volume
		properties:
			# 指定该cinder实例创建在何处, 可选属性
			availability_zone: string
			# 指定一个卷来创建备份, 可选属性
			backup_id: string
			# 描述, 可选属性
			description: string
			# 指定用来创建卷的镜像名称或ID, 格式必须是glance.image, 可选属性
			image: string
			# 元数据字典, 可选属性
			metadate: Map
			# 卷显示的名称, 可选属性
			name: string
			# 卷的体积(GB), 目前只支持扩容. 最小不能小于1, 可选属性
			size: integer
			# 指定用来创建卷的快照的ID, 可选属性
			snapshot_id: string
			# 如果指定, 则将其作为源来使用, 可选属性
			source_volid: string
			# 如果指定则映射到指定后端类型, 可选属性
			volume_type: string
			# 和image描述相同, 不清楚区别在哪
			imageRef: string
```

####OS::Cinder::VolumeAttachment

```yaml
resources:
	my_instance:
		type: OS::Cinder::VolumeAttachment
		properties:
			# 卷附加的服务器的UUID, 必须属性
			instance_uuid: string
			# 附加卷在实例上的挂载点, 可选属性
			mountpoint: string
			# 被附加的卷的ID, 必须属性
			volume_id: string
```

####OS::Glance::Image

```yaml
resources:
	my_instance:
		type: OS::Glance::Image
		properties:
			# 镜像的容器格式: ami, ari, aki, bare, ova, ovf. 必须属性
			container_format: string
			# 镜像的磁盘格式: ami, ari, aki, vhd, vmdk, raw, qcow2, vdi, iso. 必须属性
			disk_format: string
			# 镜像ID, 可选属性, 不指定则glance会自动生成一个uuid.
			id: string
			# 决定镜像是否公开, 默认为false(即私有), 可选属性
			is_public: boolean
			# 到镜像存储位置的URL, 必须属性
			location: string
			# boot镜像的磁盘空间大小(GB), 缺省值为0(不做限制), 可选属性
			min_disk: integer
			# boot镜像的内存空间大小(GB), 缺省值为0(不做限制), 可选属性
			min_ram: integer
			# 镜像名称, 可选属性
			name: string
			# 如果该值为True, 则镜像受到保护将不可被删除, 可选属性
			protected: boolean
```

####OS::Heat::AutoScalingGroup

```yaml
resources:
	my_instance:
		type: OS::Heat::AutoScalingGroup
		properties:
			# 冷却周期(秒), 可选属性
			cooldown: integer
			# 初始的资源数量, 可选属性
			desired_capacity: integer
			# 一个扩展组中的最大资源数量, 必须属性, 最小值不得小于0
			max_size: integer
			# 一个扩展组中的最小资源数量, 必须属性, 最小值不得小于0
			min_size: integer
			# 定义组中的资源, 必须是已经在模板中声明过的资源, 必须属性
			resource: map
			# 定义该扩展组滚动更新的策略, 可选属性,
			# {"min_in_service": number, "pause_time": number, "max_batch_size": number},
			# "max_batch_size"定义一次更新重置的最大资源数量, 默认为1, 最小不能小于0, 可选属性,
			# "min_in_service"定义滚动更新过程中, 保持服务的资源的最小数量, 默认为1, 最小不能小于0, 可选属性,
			# "pause_time"定义两次更新行为之间的间隔时间(秒), 默认为0, 最小不能小于0, 可选属性.
			rolling_updates: map
```

####OS::Heat::ScalingPolicy

```yaml
resources:
	my_instance:
		type: OS::Heat::ScalingPolicy
		properties:
			# 规定以下哪种情况对容量进行调节, 必须属性.
			# change_in_capacity, exact_capacity, percent_change_in_capcity
			adjustment_type: string
			# 指定应用此策略的自动扩展组的资源ID, 必须属性.
			auto_scaling_group_id: string
			# 冷却周期(s)
			cooldown: number
			# 每次调节的大小
			scaling_adjustment: number
```

####OS::Heat::CWLiteAlarm

```yaml
resources:
	my_instance:
		type: OS::Heat::CWLiteAlarm
		properties:
			# 当状态转为报警(alarm)时, 要执行的操作的列表, 可选属性
			AlarmActions: list
			# 警报描述, 可选属性
			AlarmDescription: string
			# 用来指定一个统计数据与阈值进行比较,
			# 允许以下四种比较状态, 可选属性.
			# GreaterThanOrEqualToThreshold, GreaterThanThreshold,
			# LessThanThreshold, LessThanOrEqualToThreshold.
			ComparisonOperator: string
			# 与指标相关的规模列表, 可选属性
			Dimensions: list
			# 定义评估周期, 可选属性
			EvaluationPeriods: string
			# 当状态为数据缺少(insufficient-data)时执行的操作列表, 可选属性
			InsufficientDataActions: list
			# 报警系统要监视的指标名称, 可选属性
			MetricName: string
			# 指标的namespace, 可选属性
			Namespace: string
			# 当状态转换到正常(ok)时执行的操作列表, 可选属性
			OKActions: list
			# 评估周期(s)
			Period: string
			# 为评估系统提供参考值, 可选属性, 允许以下五种度量标准,
			# SampleCount, Average, Sum, Minimum, Maximum
			Statistic: string
			# 为评估系统提供阈值, 可选属性
			Threshold: string
			# 定义指标的单位, 可选属性, 允许
			# Seconds, Microseconds, Milliseconds,
			# Bytes, Kilobytes, Megabytes, Gigabytes, Terabytes,
			# Bits, Kilobits, Megabits, Gigabits, Terabits,
			# Percent, Count, Count/Second,
			# Bytes(Bits)/Second, Kilobytes(bits)/Second, Megabytes(bits)/Second,
			# Gigabytes(bits)/Second, Terabytes(bits)/Second, None
			Units: string
```

####OS::Heat::HARestarter

```yaml
resources:
	my_instance:
		type: OS::Heat::HARestarter
		properties:
			# 要重启的实例ID
			InstanceId: string
```

####OS::Heat::InstanceGroup

```yaml
resources:
	my_instance:
		type: OS::Heat::InstanceGroup
		properties:
			# 应用配置的资源名称, 必须属性
			LaunchConfigurationName: string
			# 负载均衡资源的列表, 可选属性
			LoadBalancerNames: list
			# 需要的实例数, 必须属性
			Size: integer
			# 为该组附加标签, 可选属性, [{"key": string, "value": string}]
			Tags: list(map())
```

####OS::Heat::RandomString

```yaml
resources:
	my_instance:
		type: OS::Heat::RandomString
		properties:
			# 定义组成随机字符串的元素, [{"class": string, "min": integer}]
			# 字典中"class"用来指定字符的类, 允许
			# lettersdigits, letters, lowercase, uppercase, digits,
			# hexdigits, octdigits.
			# "min"指定至少包含几个该类的字符. 默认为1, 范围是[1, 512]
			character_classes: list(map())
			# 生成字符串的长度, 默认为32, 范围[1, 512]
			length: integer
```

####OS::Heat::ResourceGroup

```yaml
resources:
	my_instance:
		type: OS::Heat::ResourceGroup
		properties:
			# 创建实例的数量, 最小为1
			count: integer
			# 定义组内的资源, 必须属性, {type: string, properties: {...}}
			resource_def: map

```

####OS::Heat::SoftwareConfig

```yaml
resources:
	my_instance:
		type: OS::Heat::SoftwareConfig
		properties:
			# 指定要应用的配置文件内容
			config: string
			# 指定一组应用配置交付给实例, 默认不分组(Heat::Ungrouped), 可选属性
			group: string
			# 软件配置需要的输入, 可选属性
			# [{"name": string, "type": string, "default": string, "description": string}]
			inputs: list(map)
			# 传递给指定配置管理工具的参数, 可选属性
			options: map
			# 指定输出内容, 可选属性
			# [{"description": string, "error_output": boolean, "name": sting, "type": string}]
			outputs: list(map())
```

####OS::Heat::SoftwareDeployment

```yaml
resources:
	my_instance:
		type: OS::Heat::SoftwareDeployment
		properties:
			# 指定哪些操作会触发这个部署, 可选属性, 允许的行为有
			# CREATE, UPDATE, DELETE, SUSPEND, RESUME. 默认是["CREATE", "UPDATE"]
			actions: list
			# 指定OS::Heat::SoftwareConfig资源的ID以应用配置, 可选属性
			config: string
			# 指定一些配置参数, 可选属性
			input_values: map
			name: string
			# OS::Nova::Server的ID, 可选属性
			server: string
			# 指定服务器如何传递信号, 可选属性
			# 允许 "CFN_SIGNAL", "HEAT_SIGNAL", "NO_SIGNAL"
			# 默认是使用"CFN_SIGNAL"(使用HTTP POST方法传递一个以CFN键值对签名的URL)
			signal_transport: string
```

####OS::Neutron::ExtraRoute

```yaml
resources:
	my_instance:
		type: OS::Neutron::ExtraRoute
		properties:
			# 网络中的CIDR(无类别域间路由)表示, 必须属性
			destination: string
			# 下一跳的IP地址, 必须属性
			nexthop: string
			# 路由器ID, 必须属性
			router_id: string
```

####OS::Neutron::Firewall

```yaml
resources:
	my_instance:
		type: OS::Neutron::Firewall
		properties:
			# 开关防火墙, 设为false则防火墙会默认丢掉所有的包, 可选属性
			admin_stat_up: boolean
			description: string
			#OS::Neutron::FirewallPolicy的ID, 必须属性
			firewall_policy_id: string
			name: string
```

####OS::Neutron::FirewallPolicy

```yaml
resources:
	my_instance:
		type: OS::Neutron::FirewallPolicy
		properties:
			# 是否开启审计器, 默认为"false", 每次相关的防火墙策略或规则发生改变后恢复默认值, 可选属性.
			audited: boolean
			description: string
			# 一个有序列表用于防火墙规则, 必须属性
			firewall_rules: list
			name: string
			# 是否在所有的租户间共享这条防火墙策略, 默认为"default"
			shared: boolean
```

####OS::Neutron::FirewallRule

```yaml
resources:
	my_instance:
		type: OS::Neutron::FirewallRule
		properties:
			# 定义对数据包执行的操作, 可选属性, 默认为"deny", 允许值有"allow", "deny".
			action: string
			description: string
			# 目的地IP地址或者CIDR地址, 可选属性
			destination_ip_address: string
			# 目标端口, 允许设定一个端口范围, 可选属性
			destination_port: string
			# 同destination.
			source_ip_address: string
			source_port: string
			# 是否应用该规则, 默认为"true", 可选属性
			enabled: boolean
			# 允许的IP协议版本, 默认为"4", 可选属性
			ip_version: string
			name: string
			# 防火墙规则应用的协议, "tcp", "udp", "icmp", "none", 可选属性
			protocol: string
			# 是否共享给其它租户, 默认为"false"
			shared: boolean
```

####OS::Neutron::FloatingIP

```yaml
resources:
	my_instance:
		type: OS::Neutron::FloatingIP
		properties:
			# 当端口存在多个IP地址时, 指定使用哪个地址, 可选属性
			fixed_ip_address: string
			# 指定IP属于哪个网络, 可选属性
			floating_network: string
			# 关联已有端口的地址与floatingIP, 可选属性
			port_id: string
			# 在creation request中指定一些额外参数, 默认为空, 可选属性
			value_specs: map
```

####OS::Neutron::HealthMonitor

```yaml
resources:
	my_instance:
		type: OS::Neutron::HealthMonitor
		properties:
			# 健康度监视是否开启, 默认为"true", 可选属性
			admin_state_up: boolean
			# 负载均衡集群成员之间常规链接的最小时间(s), 必须属性
			delay: integer
			# 在响应中使用HTTP状态码来表示健康状况, 可选属性
			expected_codes: string
			# 当type为"HTTP"时, 在这里定义允许的HTTP方法, 可选属性
			http_method: string
			# 允许尝试的链接次数, 超过这个值后成员状态显示为"INACTIVE", 必须属性
			max_retries: integer
			# 建立链接的超时时间(s), 必须属性
			timeout: integer
			# 健康度监控的预设类型, 必须属性, 允许PING, TCP, HTTP, HTTPS
			type: string
			# 指定用于检测成员健康度的HTTP请求的HTTP路径
			url_path: string
```
