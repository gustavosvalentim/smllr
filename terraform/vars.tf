variable "environment" {
  type    = string
  default = "development"
}

variable "do_token" {
  type = string
}

variable "droplet_ssh_key_id" {
  type = string
}

variable "image_name" {
  type    = string
  default = "ubuntu-24-04-x64"
}

variable "region_name" {
  type    = string
  default = "nyc1"
}

variable "postgres_user" {
  type    = string
  default = "smllr_usr"
}

variable "valkey_db_name" {
  type    = string
  default = "smllr"
}

