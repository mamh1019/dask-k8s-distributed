# Dask-k8s 분산 처리 (EFS 기반)

Kubernetes 환경에서 **AWS EFS**를 워커 공유 스토리지로 사용하는 Dask 분산 처리 데모.  
여러 Pod가 EFS 볼륨을 공유해 대용량 데이터를 읽고 쓰며 병렬 처리를 수행한다.

## 핵심 구성

| 구성요소 | 설명 |
|---------|------|
| **AWS EFS** | 워커 Pod 간 공유 스토리지 (EFS CSI Driver + StorageClass) |
| `KubeCluster.from_name()` | 기존 DaskCluster CRD 리소스 참조 |
| `Client(cluster)` | 분산 작업 실행을 위한 클라이언트 |
| `cluster.scale(n)` | 워커 Pod 수 동적 조정 |
| `dask.delayed(fn)(...)` | 태스크 지연 생성 (lazy) |
| `dask.compute(*lazy_results)` | 태스크 제출 및 결과 수집 |

## 직렬화 제약

Dask는 태스크를 워커 Pod로 전달할 때 직렬화(serialize)한다.  
DB 커넥션, 파일 핸들 등 직렬화 불가 객체는 워커 함수 인자로 전달할 수 없다.  
공유 데이터는 pickle 가능한 형태로 전달하거나, 워커 내부에서 직접 로드한다.

## 실행

```bash
# DaskCluster 리소스가 dask-cluster 네임스페이스에 존재해야 함
python main.py

# 옵션: --tasks 200 --batch-size 20 --categories 10
python main.py --tasks 200 --batch-size 20
```

## Infrastructure (iac)

CloudFormation, eksctl, Helm으로 AWS 인프라를 구성한다.  
Dask 워커는 EFS PVC를 마운트하여 공유 디스크(`/var/analysis`)를 사용한다.

### 1. VPC (CloudFormation)

`iac/cloudformation/vpc/config.yaml`로 VPC 및 서브넷 생성.

- **Public Subnet**: 로드 밸런서, 외부 연결 리소스
- **Private Subnet**: 워커 노드, 내부 워크로드
- NAT Gateway 미사용 (비용 절감)

```bash
aws cloudformation create-stack \
  --stack-name <stack-name> \
  --template-body file://iac/cloudformation/vpc/config.yaml
```

### 2. EKS Cluster

VPC 생성 후 eksctl로 EKS 클러스터 생성.

```bash
eksctl create cluster --config-file=iac/cluster-iac/k8s/cloudformation.yaml
```

### 3. 디렉터리 구조

```
iac/
├── cloudformation/vpc/   # VPC, Subnet 템플릿
├── cluster-iac/k8s/     # eksctl 설정 (cloudformation.yaml, node-groups, dask-nodes)
├── helm/                 # Dask, Prometheus + EFS StorageClass/ServiceAccount
└── scripts/              # scale_up/down 스크립트
```

### 4. 배포 전 교체할 값

- **`iac/helm/prometheus/efs-account/trust-policy.json`**: `YOUR_AWS_ACCOUNT_ID`, `YOUR_EKS_OIDC_PROVIDER_ID`를 실제 AWS 계정 ID와 EKS OIDC Provider ID로 교체.
- **`iac/helm/prometheus/storageclass.yaml`**: `fs-YOUR_EFS_FILESYSTEM_ID`를 실제 EFS 파일시스템 ID로 교체.
- **`iac/scripts/scale_up.sh`, `scale_down.sh`**: `AWS_PROFILE` 환경 변수를 설정하거나, 스크립트 내 `your-eks-profile` 기본값을 사용할 EKS CLI 프로필명으로 수정.
