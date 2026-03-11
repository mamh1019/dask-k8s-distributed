## Installs

### Infra Setup
#### EKS Cluster
- 클러스터 및 관리형 노드 그룹 생성
- NAT를 사용하면 비용이 나오기에 Public Subnet 으로 노드를 배치함
```bash
$ cd k8s
$ eksctl create cluster --config-file=cloudformation.yaml
```
or
```
$ cd terraform
$ terraform apply
```

#### aws-ebs-csi-driver
- 각 Pod 에 연결 할 EFS의 드라이버 설치
- [aws-ebs-csi-driver 공식 문서](https://docs.aws.amazon.com/ko_kr/eks/latest/userguide/ebs-csi.html)
```bash
helm upgrade --install aws-efs-csi-driver --namespace kube-system aws-efs-csi-driver/aws-efs-csi-driver
```