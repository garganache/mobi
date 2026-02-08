data "scaleway_account_project" "current" {
  project_id = var.scw_project_id
}

output "project_name" {
  value = data.scaleway_account_project.current.name
}
