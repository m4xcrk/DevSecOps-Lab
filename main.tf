terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "2.25.0"
    }
  }
}

provider "docker" {
  host = "tcp://10.69.98.12:2375"
}

# --- 1. Operations Hub (on VM-002) ---

resource "docker_container" "prometheus" {
  name  = "prometheus"
  image = "prom/prometheus:latest"
  ports {
    internal = 9090
    external = 9090
  }
  restart = "always"
}

resource "docker_container" "grafana" {
  name  = "grafana"
  image = "grafana/grafana:latest"
  ports {
    internal = 3000
    external = 3000
  }
  restart = "always"
}

# --- 2. Worker Nodes (Apache Servers on VM-002) ---

resource "docker_container" "apache_servers" {
  count = 2
  name  = "apache-server-${count.index}"
  image = "httpd:latest"
  ports {
    internal = 80
    external = "808${count.index + 6}" # Maps to 8086, 8087
  }
}

# --- 3. Inventory Generation ---

resource "local_file" "ansible_inventory" {
  content  = <<EOT
[lb]
vm01 ansible_host=10.69.98.11

[docker_host]
vm02 ansible_host=10.69.98.12

[attack]
vm03 ansible_host=10.69.98.13

[soc]
vm04 ansible_host=10.69.98.14

[all:vars]
ansible_user=root
ansible_ssh_private_key_file=~/.ssh/id_ed25519
EOT
  filename = "${path.module}/inventory.ini"
}
