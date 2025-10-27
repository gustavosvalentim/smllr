resource "digitalocean_project" "smllr_project" {
  name        = "smllr-iac"
  description = "Project for smllr infrastructure resources"
  purpose     = "Web Application"
  environment = var.environment
  resources   = [
    digitalocean_droplet.smllr_droplet.urn,
    digitalocean_database_cluster.smllr_postgres.urn,
    digitalocean_database_cluster.smllr_valkey.urn,
  ]
}
