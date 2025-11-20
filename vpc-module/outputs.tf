output "vpc_id" {
  description = "The ID of the newly created VPC."
  # Assuming the VPC resource is named "aws_vpc.main"
  value       = aws_vpc.main.id 
}

output "public_subnet_cidr_blocks" {
  description = "A list of CIDR blocks for the public subnets."
  
  # If public_subnet_count > 0, return the list of CIDR blocks.
  # Otherwise, return an empty list.
  value       = var.public_subnet_count > 0 ? aws_subnet.public_subnets[*].cidr_block : []
}

output "private_subnet_cidr_blocks" {
  description = "A list of CIDR blocks for the private subnets."
  
  # If private_subnet_count > 0, return the list of CIDR blocks.
  # Otherwise, return an empty list.
  value       = var.private_subnet_count > 0 ? aws_subnet.private_subnets[*].cidr_block : []
}


output "public_subnet_ids" {
  description = "A list of IDs for the public subnets. Only available if public_subnet_count > 0."
  
  value         = var.public_subnet_count > 0 ? aws_subnet.public_subnets[*].id : null
}

output "private_subnet_ids" {
  description = "A list of IDs for the private subnets. Only available if private_subnet_count > 0."
  value         = var.private_subnet_count > 0 ? aws_subnet.private_subnets[*].id : null
}

output "nat_eip_public_ips" {
  description = "A list of the Public IP addresses (EIPs) allocated for the NAT Gateways. Only available if public_subnet_count > 0."

  value         = var.public_subnet_count > 0 ? aws_eip.nat[*].public_ip : null
}