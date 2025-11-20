resource "aws_vpc" "main" {
  cidr_block           = var.cidr_block
  enable_dns_support   = true
  enable_dns_hostnames = true
  

tags = {
  Name        = var.vpc_name
 }
}


resource "aws_internet_gateway" "gw" {
 
  vpc_id = aws_vpc.main.id 

  tags = {
    Name = "my-vpc-internet-gateway"
  }
}


# Create the Public Route Table only if public subnets exist
resource "aws_route_table" "public" {
  # If var.public_subnet_count > 0, count is 1. Otherwise, count is 0.
  count  = var.public_subnet_count > 0 ? 1 : 0
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "Public Route Table"
  }
}

resource "aws_route_table_association" "public_association" {
  # This count ensures the association runs for every public subnet (0, 1, 2...)
  count = var.public_subnet_count

  # Target the ID of the public subnet at the current index of the loop
  subnet_id = aws_subnet.public_subnets[count.index].id

  # Target the single Public Route Table instance at index [0] for ALL subnets.
 
  route_table_id = aws_route_table.public[0].id
 
}


# Add the route for all Internet-bound traffic (0.0.0.0/0)
resource "aws_route" "public_internet_route" {
  count = length(aws_route_table.public) > 0 ? 1 : 0

  # Target the ID of the single Public Route Table created conditionally at index [0]
  route_table_id         = aws_route_table.public[0].id
  
  # The CIDR block that defines all external traffic
  destination_cidr_block = "0.0.0.0/0"
  
  # The next hop for the traffic is the Internet Gateway
  gateway_id             = aws_internet_gateway.gw.id
}


# Create two Elastic IPs (one for each NAT Gateway)
resource "aws_eip" "nat" {
  count = var.public_subnet_count
  domain = "vpc"
}

#  Create NAT Gateways
resource "aws_nat_gateway" "nat" {
  count         = var.public_subnet_count
  allocation_id = aws_eip.nat[count.index].id
  # Deploy the NAT Gateway into the corresponding public subnet
  subnet_id     = aws_subnet.public_subnets[count.index].id 
  
  tags = {
    Name = "NAT-GW-${count.index + 1}"
  }
}


resource "aws_route_table" "private" {
  count  = var.private_subnet_count
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "Private-RT-${count.index + 1}"
  }
}

# Add the outbound route to the corresponding NAT Gateway
resource "aws_route" "private_nat_route" {
  count                  = var.private_subnet_count
  route_table_id         = aws_route_table.private[count.index].id
  destination_cidr_block = "0.0.0.0/0"
  # Route traffic to the NAT GW in the SAME AZ index
  nat_gateway_id         = aws_nat_gateway.nat[count.index].id
}

# Associate each Private Subnet with its corresponding Route Table
resource "aws_route_table_association" "private_association" {
  count          = var.private_subnet_count
  # Associate the private subnet with the route table at the same index
  subnet_id      = aws_subnet.private_subnets[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}