resource "aws_subnet" "public_subnets" {
 count      = var.public_subnet_count
 vpc_id     = aws_vpc.main.id
 # Allocation starts at index 1: (0+1=1), (1+1=2), etc.
 cidr_block = cidrsubnet(var.cidr_block, 4, count.index + 1)
 #availability_zone = element(var.availability_zones, count.index)
 availability_zone = data.aws_availability_zones.available.names[count.index]
 tags = {
   Name = "Public Subnet-${count.index + 1}"
 }
}


resource "aws_subnet" "private_subnets" {
 count      = var.private_subnet_count
 vpc_id     = aws_vpc.main.id
 cidr_block = cidrsubnet(var.cidr_block, 4, count.index + var.public_subnet_count + 1)
 #availability_zone = element(var.availability_zones, count.index)
 availability_zone = data.aws_availability_zones.available.names[count.index]
 tags = {
   Name = "Private Subnet-${count.index + 1}"
 }
}








