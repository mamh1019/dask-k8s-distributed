provider "aws" {
  region = local.region
}

locals {
  cluster_name      = "workload-cluster"
  region            = "ap-northeast-1"
  tags = {
    createdBy        = "dask-k8s-demo"
    createdByProject = "example-cluster"
  }
  vpc_id = "vpc-04279b0c0608c77xx"
  public_subnets = ["subnet-034b52a8ee18a59xx", "subnet-011130e9f49e942xx"]
}

module "eks_al2023" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = "${local.cluster_name}"
  cluster_version = "1.32"
  cluster_endpoint_public_access = true
  cluster_endpoint_private_access = true
  enable_irsa = true
  create_cloudwatch_log_group = false

  # EKS Addons
  cluster_addons = {
    coredns                = {}
    eks-pod-identity-agent = {}
    kube-proxy             = {}
    vpc-cni                = {}
    aws-ebs-csi-driver     = {
      well_known_policies = {
        ebs_csi_controller = true
      }
    }
  }

  vpc_id     = local.vpc_id
  subnet_ids = local.public_subnets

  eks_managed_node_groups = {
    dask-node = {
      # Starting on 1.30, AL2023 is the default AMI type for EKS managed node groups
      instance_types = ["t3.xlarge"]
      capacity_type = "SPOT"
      disk_size = 30

      min_size = 1
      max_size = 20
      desired_size = 2

      labels = {
        "role" = "dask-node"
      }
    }

    app-node  = {
      instance_types = ["t3.xlarge"]
      capacity_type = "SPOT"
      disk_size = 30

      min_size = 1
      max_size = 3
      desired_size = 1

      labels = {
        "role" = "app-node"
      }
    }
  }

  tags = local.tags
}