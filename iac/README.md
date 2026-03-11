# workload-cluster
k8s Distributed Data Processor for Data Team

## 개요
이 클러스터는 **[Dask Gateway](https://gateway.dask.org/)**를 사용하여 대규모 데이터 처리를 위한 동적이고 확장 가능한 분산 처리를 하기 위해 사용 됨
    
## VPC 구성
- **Public 및 Private 서브넷**  
  - Public 서브넷: 로드 밸런서 및 외부 인터넷과 연결되는 리소스에 사용
  - Private 서브넷: 워커 노드와 내부 워크로드에 사용

- **NAT Gateway 미사용**  
  - 비용 절감을 위해 NAT Gateway를 사용하지 않음
  - 외부 인터넷 필요 시 생성

## Installs

### Infra Setup
#### EKS Cluster
- 클러스터 및 관리형 노드 그룹 생성
- NAT를 사용하면 런닝 비용이 나오기에 Public Subnet 으로 노드를 배치함. 하루 1시간 정도만 대용량 계산을 위한 스케일 업을 하기 때문
```bash
$ eksctl create cluster --config-file=./cluster-iac/k8s/cloudformation.yaml
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

### Pod Setup
#### requirements
- python==3.10.12
- requirements.txt 에 있는 모든 패키지 설치
- Client 및 모든 Worker 의 python 버전은 동일해야 함 

#### Dask Kubernetes 클러스터 설정
- dask-operator 설치
- https://kubernetes.dask.org/en/latest/installing.html
```bash
helm install --repo https://helm.dask.org --create-namespace -n dask-operator --generate-name dask-kubernetes-operator
```

#### EFS Setup
- claim.yaml 에서 사용할 클러스터 명을 지정한 후 연동
- 각 파일 내 efs-id 변경
```bash
kubectl apply -f efs/pv.yaml
kubectl apply -f efs/claim.yaml
kubectl apply -f efs/storageclass.yaml
kubectl get pv -w
```