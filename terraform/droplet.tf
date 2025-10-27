resource "digitalocean_droplet" "smllr_droplet" {
  image             = var.image_name
  name              = "smllr-${var.environment}-001"
  region            = var.region_name
  size              = "s-1vcpu-1gb"
  ssh_keys          = [var.droplet_ssh_key_id]
  graceful_shutdown = true
  user_data         = file("droplet-init")

  tags = ["environment:${var.environment}", "project:smllr"]
}
