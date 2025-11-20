variable "aws_region" {
  description = "The AWS region to deploy resources into."
  type        = string
  default     = ""
}

variable "environment" {
  description = "The deployment environment (e.g., dev, staging, prod)."
  type        = string
  default     = ""
}