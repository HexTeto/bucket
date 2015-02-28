## Overview

__Btrfs (B-tree file system)__ 是 Oracle 开发的一个 "Copy on Write" 的文件系统,
该文件系统主要包括以下特性:
- 基于扩展的文件存储
- 文件尺寸上限为 `16EiB` (Exbibtye, `1EiB = 1024 PB = 2^60 bytes` )
- 对小文件和建立索引的目录的空间利用更高效
- 动态索引节点分配
- 可写快照和只读快照
- 子卷 (可分离内部文件系统的根)
- 支持数据和元数据的校验和
- 压缩
- 多设备支持
- 支持文件条块化 (File Striping), 文件镜像 (File Mirroring) 和二者结合的三种实现
- 高效增量备份
- 后台消除进程支持查找和修复冗余副本上的文件错误
- 支持在线文件系统碎片整理和离线文件系统检查
- 对 RAID 5 / RAID 6 更好的支持 (recommends kernel version ≥ 3.19)

<br>

## Converting to Brtfs

> __WARNING__ : 无论何时, 首先进行数据备份!


```sh
# 使用 fsck 检测分区是否存在错误
fsck.ext4 /dev/sda4
# 转换分区
btrfs-convert /dev/sda4
# 挂载分区
mount /dev/sda4 /mnt
```

当需要转换根分区时, 使用 LiveCD 进入临时系统:

```sh
fsck.ext4 /dev/sda1
btrfs-convert /dev/sda1
mount /dev/sda1 /mnt
for i in dev dev/pts proc sys; do mount --bind /$i /mnt/$i; done
chroot /mnt
blkid | grep sda1
```

编辑 `fstab` 根据 `blkid` 的输出结果修改对应的 `UUID`, 并修改文件系统类型为 `btrfs`.

最后重新安装 `grub`.

```sh
grub-install /dev/sda
update-grub
```
