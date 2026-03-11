```bash
eksctl create iamserviceaccount \
  --name efs-csi-controller-sa \
  --namespace kube-system \
  --cluster workload-cluster \
  --role-name AmazonEKS_EFS_CSI_DriverRole \
  --attach-policy-arn arn:aws:iam::aws:policy/service-role/AmazonEFSCSIDriverPolicy \
  --approve


kubectl create serviceaccount efs-csi-controller-sa -n kube-system
eksctl create iamserviceaccount \
  --name efs-csi-controller-sa \
  --namespace kube-system \
  --cluster workload-cluster \
  --attach-role-arn arn:aws:iam::YOUR_AWS_ACCOUNT_ID:role/AmazonEKS_EFS_CSI_DriverRole \
  --approve

helm install aws-efs-csi-driver aws-efs-csi-driver/aws-efs-csi-driver \
  --namespace kube-system \
  --set controller.serviceAccount.create=false \
  --set controller.serviceAccount.name=efs-csi-controller-sa
```

```bash
helm upgrade --install prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace "prometheus" \
  -f "values.yaml"
```