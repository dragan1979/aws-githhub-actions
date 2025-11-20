variable "vpc_name" {
  type = string
  default = ""
}   

variable "cidr_block" {
  type = string
  default = ""
}

#variable "availability_zones" {
#  description = "A list of Availability Zones to use."
#  type        = list(string)
#  default     = ["eu-central-1a", "eu-central-1b"]
#}

variable "public_subnet_count" {
  description = "The number of public subnets to create in each AZ."
  type        = number
  default     = 2
}

variable "private_subnet_count" {
  description = "The number of private subnets to create in each AZ."
  type        = number
  default     = 2
}



variable "aws_region" {
  description = "The AWS region where resources will be deployed."
  type        = string
  default     = "eu-central-1"
}


data "aws_availability_zones" "available" {
  state = "available"
}

variable "environment" {
  description = "The deployment environment (e.g., dev, staging, prod)."
  type        = string
  default     = ""
}