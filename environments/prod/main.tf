module "vpc_network" {
  # The source is the local directory path
  source = "../../vpc-module" 
  
  # Pass variables defined in the root config
  cidr_block           = "192.168.0.0/20"
  public_subnet_count  = 2
  private_subnet_count = 2
  aws_region           = "eu-central-1"
  vpc_name             = "my-vpc-prod"
  #environment          = var.environment
}


output public_subnet_cidr_blocks {  
  value       = module.vpc_network.public_subnet_cidr_blocks
  description = "List of public subnet CIDR blocks"
}

output private_subnet_cidr_blocks {  
  value       = module.vpc_network.private_subnet_cidr_blocks
  description = "List of private subnet CIDR blocks"
}

output vpc_id {
  value       = module.vpc_network.vpc_id
  description = "VPC ID"
  
}

output public_subnet_ids {  
  value       = module.vpc_network.public_subnet_ids
  description = "List of public subnet IDs"
}

output private_subnet_ids {  
  value       = module.vpc_network.private_subnet_ids
  description = "List of private subnet IDs"
}

output nat_eip_public_ips {  
  value       = module.vpc_network.nat_eip_public_ips
  description = "List of NAT EIP public IPs"
}