# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
    # define name
    config.vm.define "master" do |master|
    end

    # box from
    config.vm.box = "ubuntu/trusty64"
    # using a specific ip address
    config.vm.network "private_network", ip: "10.10.10.10"
    # public port
    config.vm.network "forwarded_port", guest: 80, host: 8080
    config.vm.network "forwarded_port", guest: 5000, host: 8888
  # config.vm.synced_folder "../share_data", "/vagrant_data"
    # customize vm
    config.vm.provider "virtualbox" do |vb|
        vb.name = "master"
        vb.cpus = 2
        vb.memory = 2048
    end
end
