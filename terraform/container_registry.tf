resource "digitalocean_container_registry" "smllr_container_registry" {
  name                      = "smllr-registry"
  subscription_tier_slug    = "starter"
}

resource "digitalocean_container_registry_docker_credentials" "smllr_docker_credentials" {
  registry_name = digitalocean_container_registry.smllr_container_registry.name
}

output "container_registry_url" {
  value         = digitalocean_container_registry.smllr_container_registry.server_url
  description   = "Container registry URL"
}

output "container_registry_credentials" {
  value         = digitalocean_container_registry_docker_credentials.smllr_docker_credentials.docker_credentials
  description   = "Credentials to sign in with docker"
  sensitive     = true
}
