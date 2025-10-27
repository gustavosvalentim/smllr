resource "digitalocean_database_cluster" "smllr_postgres" {
  name        = "smllr-postgres-cluster-${var.environment}"
  engine      = "pg"
  version     = "15"
  size        = "db-s-1vcpu-1gb"
  region      = var.region_name
  node_count  = 1
}

resource "digitalocean_database_db" "smllr_postgres" {
  cluster_id = digitalocean_database_cluster.smllr_postgres.id
  name       = "smllr"
}

resource "digitalocean_database_user" "smllr_postgres" {
  cluster_id = digitalocean_database_cluster.smllr_postgres.id
  name       = var.postgres_user
}

resource "digitalocean_database_connection_pool" "smllr_postgres" {
  cluster_id  = digitalocean_database_cluster.smllr_postgres.id
  name        = "pool-01"
  mode        = "transaction"
  size        = 20
  db_name     = digitalocean_database_db.smllr_postgres.name
  user        = digitalocean_database_user.smllr_postgres.name
}

resource "digitalocean_database_cluster" "smllr_valkey" {
  name        = "smllr-valkey-cluster-${var.environment}"
  engine      = "valkey"
  version     = "8"
  size        = "db-s-1vcpu-1gb"
  region      = var.region_name
  node_count  = 1
}

output "smllr_postgres_username" {
  value       = digitalocean_database_user.smllr_postgres.name
  description = "Postgres username"
}

output "smllr_postgres_password" {
  value       = digitalocean_database_user.smllr_postgres.password
  description = "Postgres password"
  sensitive   = true
}

output "smllr_postgres_host" {
  value       = digitalocean_database_connection_pool.smllr_postgres.host
  description = "Postgres host"
}

output "smllr_postgres_port" {
  value       = digitalocean_database_connection_pool.smllr_postgres.port
  description = "Postgres port"
}

output "smllr_valkey_username" {
  value       = digitalocean_database_cluster.smllr_valkey.user
  description = "Valkey username"
}

output "smllr_valkey_password" {
  value       = digitalocean_database_cluster.smllr_valkey.password
  description = "Valkey password"
  sensitive   = true
}

output "smllr_valkey_host" {
  value       = digitalocean_database_cluster.smllr_valkey.host
  description = "Valkey host"
}

output "smllr_valkey_port" {
  value       = digitalocean_database_cluster.smllr_valkey.port
  description = "Valkey port"
}
