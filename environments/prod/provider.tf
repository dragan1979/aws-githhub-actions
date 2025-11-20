provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      # ------------------------------------------------
      # MANDATORY TAGS
      # ------------------------------------------------
      Environment      = var.environment
      Project          = "Tatooine-State-Backend"
      CostCenter       = "4775"
      ManagedBy        = "Terraform"
      
      # ------------------------------------------------
      # OPERATIONAL/AUDIT TAGS
      # ------------------------------------------------
      SecurityTier     = "Internal"
      AutomationSource = "GitHub-Actions"
    }
  }
}


terraform {
  required_version = ">= 1.10.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0" # Use a version appropriate for your setup
    }
  }

  # --- S3 Backend Configuration ---
  backend "s3" {
    bucket         = "terraform-tfstate-bucket-tatooine" # Your S3 Bucket Name
    key            = "prod/terraform.tfstate" # Path to the state file within the bucket
    region         = "eu-central-1" # The region where your S3 bucket resides
    
    # ----------------------------------------------------
    # S3 Native Locking Configuration (Recommended for new TF versions)
    # The default locking mechanism uses a file named .tflock in the bucket.
    # ----------------------------------------------------
    use_lockfile = true
    
    # Enable server-side encryption for the state file (Highly Recommended)
    encrypt = true 
    
    # Optional: If you use a profile instead of environment variables
    # profile = "my-terraform-user" 
  }
}