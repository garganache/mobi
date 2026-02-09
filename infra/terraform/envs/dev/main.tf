data "scaleway_account_project" "current" {
  project_id = var.scw_project_id
}

# Dev private network managed by Terraform
resource "scaleway_vpc_private_network" "dev" {
  name = "mobi-dev-private-network"
  tags = ["env:dev", "app:mobi"]
}

# Minimal Kapsule cluster for dev
resource "scaleway_k8s_cluster" "dev" {
  name        = "mobi-dev-cluster"
  description = "Dev Kubernetes cluster for mobi"

  type = "kapsule"
  cni  = "cilium"
  tags = ["env:dev", "app:mobi"]

  # Explicit Kapsule version (from Scaleway UI)
  version            = "1.35.0"
  private_network_id = scaleway_vpc_private_network.dev.id

  delete_additional_resources = true
}

resource "scaleway_k8s_pool" "dev_default" {
  cluster_id = scaleway_k8s_cluster.dev.id
  name       = "dev-pool"

  node_type = "DEV1-M"
  size      = 1

  autoscaling = false

  tags = ["env:dev", "app:mobi"]
}

# Managed Postgres for dev (Scaleway RDB)
resource "scaleway_rdb_instance" "dev" {
  name          = "mobi-dev-db"
  engine        = "PostgreSQL-16"
  node_type     = "DB-DEV-S"
  is_ha_cluster = false
  region        = var.scw_region

  tags = ["env:dev", "app:mobi"]
}

resource "scaleway_rdb_database" "mobi" {
  instance_id = scaleway_rdb_instance.dev.id
  name        = "mobi"
}

resource "scaleway_rdb_user" "mobi" {
  instance_id = scaleway_rdb_instance.dev.id
  name        = "mobi"
  password    = var.mobi_db_password
  is_admin    = false
}

output "project_name" {
  value = data.scaleway_account_project.current.name
}

output "k8s_cluster_id" {
  value = scaleway_k8s_cluster.dev.id
}

output "db_connection_url" {
  value       = "postgresql+psycopg://${scaleway_rdb_user.mobi.name}:${var.mobi_db_password}@${scaleway_rdb_instance.dev.endpoint_ip}:${scaleway_rdb_instance.dev.endpoint_port}/${scaleway_rdb_database.mobi.name}"
  sensitive   = true
  description = "SQLAlchemy-compatible connection URL for the mobi dev DB"
}
