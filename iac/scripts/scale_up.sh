#!/bin/bash
# Set AWS_PROFILE to your EKS CLI profile (e.g. export AWS_PROFILE=your-eks-profile)
AWS_PROFILE="${AWS_PROFILE:-your-eks-profile}"

eksctl scale nodegroup --cluster=example-cluster --name=dask --nodes=16 --profile "$AWS_PROFILE"

echo "Waiting for all nodes to be ready..."
while [[ $(kubectl get nodes --no-headers | grep -c " Ready") -lt 16 ]]; do
  echo "Waiting..."
  sleep 10
done

echo "All nodes are ready!"
