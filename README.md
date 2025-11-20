# AWS VPC Module with Two-Stage GitHub Actions CI/CD

This repository provides a modular, reusable **Terraform module** for provisioning a standard, highly available AWS Virtual Private Cloud (VPC) with public and private subnets across multiple Availability Zones (AZs).

It includes a robust **two-stage GitHub Actions CI/CD pipeline** for validating infrastructure changes on Pull Requests and safely deploying them on merge.

---

## Project Architecture: AWS VPC

The Terraform module creates a best-practice VPC topology designed for high availability and security:

* **VPC**: The main network container, defined by `var.cidr_block`.
* **Public Subnets**: Provisioned for public-facing resources and spread across multiple AZs.
* **Private Subnets**: Provisioned for application servers, providing isolated, secure network space.
* **Internet Gateway (IGW)**: Provides internet access for the VPC.
* **NAT Gateways (NAT-GWs)**: One NAT-GW is deployed in *each* public subnet, allowing private resources to initiate outbound internet traffic.
* **Routing**: Public subnets route directly to the IGW, while each Private Subnet routes to its corresponding NAT-GW within the same AZ index.

---

## Module Usage

### 1. Requirements

* Terraform CLI (version `1.13.5` used in CI/CD)
* An AWS account with configured credentials.

### 2. Input Variables

The module is configured using the following variables, defined in `variables.tf`:

| Variable Name | Description | Type | Default Value |
| :--- | :--- | :--- | :--- |
| `vpc_name` | The name to tag the main VPC resource. | `string` | `""` |
| `cidr_block` | The CIDR block for the entire VPC. | `string` | `""` |
| `public_subnet_count` | The number of public subnets to create across AZs. | `number` | `2` |
| `private_subnet_count` | The number of private subnets to create across AZs. | `number` | `2` |
| `aws_region` | The AWS region for deployment. | `string` | `"eu-central-1"` |
| `environment` | The deployment environment (used for tagging). | `string` | `""` |

### 3. Outputs

The module exports key resource identifiers for use by other modules, as defined in `outputs.tf`:

| Output Name | Description | Condition |
| :--- | :--- | :--- |
| `vpc_id` | The ID of the newly created VPC. | Always |
| `public_subnet_ids` | A list of IDs for the public subnets. | Only if `public_subnet_count > 0` |
| `private_subnet_ids` | A list of IDs for the private subnets. | Only if `private_subnet_count > 0` |
| `nat_eip_public_ips` | A list of Public IP addresses (EIPs) allocated for the NAT Gateways. | Only if `public_subnet_count > 0` |

---

## CI/CD Pipeline: GitHub Actions

The repository utilizes two GitHub Actions workflows to enforce code quality, review, and safe deployment, leveraging **OIDC** for secure AWS authentication.

### 1. `terraform-plan.yml`: Validation Pipeline (Runs on Pull Request)

This pipeline acts as the essential quality gate before merging code.

| Feature | Description | File Source |
| :--- | :--- | :--- |
| **Trigger** | `pull_request` events targeting `dev`, `staging`, or `main`. | `terraform-plan.yml` |
| **Authentication** | Uses **OIDC** to assume an IAM role for temporary credentials. | `terraform-plan.yml` |
| **Plan Execution**| Runs `terraform init` and `terraform plan` for the target environment (`TF_ENV_FOLDER`). | `terraform-plan.yml` |
| **PR Comment** | Posts the full `terraform plan` output back to the Pull Request. | `terraform-plan.yml` |
| **Security** | Runs **Checkov** for security scanning on the Terraform code, uploading an HTML report artifact. | `terraform-plan.yml` |

### 2. `terraform-apply.yaml`: Deployment Pipeline (Runs on Push/Merge)

This pipeline is responsible for safely applying the infrastructure changes once code has been reviewed and merged.

| Feature | Description | File Source |
| :--- | :--- | :--- |
| **Trigger** | `push` events to `dev`, `staging`, or `main` branches. | `terraform-apply.yaml` |
| **Concurrency** | Uses a concurrency group based on the branch name to prevent concurrent deployments to the *same* environment. | `terraform-apply.yaml` |
| **Notifications** | Posts a commit comment to indicate the deployment has **started**. | `terraform-apply.yaml` |
| **Apply Execution**| Runs the full workflow (init, plan, and **apply**) for the target environment (`TF_ENV_FOLDER`). | `terraform-apply.yaml` |

---

## Getting Started

1.  **Configure AWS IAM**: Set up the OIDC provider in AWS and create the IAM role `arn:aws:iam::477568783935:role/GitHubActions-AWS-Admin` that trusts your GitHub repository's OIDC identity.
2.  **Set Repository Variables**: Define the `AWS_REGION` variable in your GitHub Repository Settings.
3.  **Create Environment Files**: Create your environment-specific configuration files (e.g., `environments/dev/variables.tfvars`).
4.  **Open a Pull Request**: Submit code changes and check the PR comment for the `terraform plan` output.
5.  **Merge**: Merge your PR to trigger the automated `terraform apply` deployment.
