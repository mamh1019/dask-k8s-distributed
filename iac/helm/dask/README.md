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
```bash
kubectl create namespace dask-cluster
kubectl apply -f storageclass.yaml
kubectl apply -f pv.yaml
kubectl apply -f pvc.yaml
kubectl get pv
```

#### Run
- Client 에서 Jupyter 실행
```bash
/srv/workload-cluster/venv/bin/python /srv/workload-cluster/venv/bin/jupyter-lab --no-browser --ip=0.0.0.0 --port=8888 &
```
- 클러스터 클라이언트 dashboard 접속을 위한 터널링
```bash
ssh -i ~/.ssh/eks-pod-ssh.pem -L 56737:localhost:56737 ec2-user@52.199.38.184
```