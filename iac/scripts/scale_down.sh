#!/bin/bash
# Set AWS_PROFILE to your EKS CLI profile (e.g. export AWS_PROFILE=your-eks-profile)
AWS_PROFILE="${AWS_PROFILE:-your-eks-profile}"

eksctl scale nodegroup --cluster=example-cluster --name=dask --nodes=1 --profile "$AWS_PROFILE"
echo "Scaled down to 1 node."