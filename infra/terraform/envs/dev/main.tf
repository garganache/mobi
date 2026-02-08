data "scaleway_account_project" "current" {
  project_id = var.scw_project_id
}

# Minimal Kapsule cluster for dev
resource "scaleway_k8s_cluster" "dev" {
  name        = "mobi-dev-cluster"
  description = "Dev Kubernetes cluster for mobi"

  type = "kapsule"
  cni  = "cilium"
  tags = ["env:dev", "app:mobi"]

  version                     = "1.30.0"
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

output "project_name" {
  value = data.scaleway_account_project.current.name
}

output "k8s_cluster_id" {
  value = scaleway_k8s_cluster.dev.id
}
