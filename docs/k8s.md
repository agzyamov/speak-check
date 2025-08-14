# Local Kubernetes (k3d) Deployment

This guide runs the CEFR Speaking Exam Simulator on a local Kubernetes cluster using k3d (no Docker Desktop), Colima for Docker runtime, and kubectl.

## Prerequisites
- Colima running (Docker CLI available)
- kubectl
- k3d

## Build the image
```bash
docker build -t speak-check:latest .
```

## Create cluster and map ports
```bash
k3d cluster create speak-check \
  -p "8501:30080@loadbalancer" \
  -p "27018:30017@loadbalancer"
```

## Load image into the cluster
```bash
k3d image import speak-check:latest -c speak-check
```

## Apply manifests
```bash
kubectl apply -f k8s/namespace.yaml
kubectl -n speak-check apply -f k8s/configmap.yaml -f k8s/secret.yaml
kubectl -n speak-check apply -f k8s/mongo-statefulset.yaml -f k8s/mongo-service.yaml \
  -f k8s/app-deployment.yaml -f k8s/app-service.yaml
```

## Create secrets (do not commit keys)
```bash
kubectl -n speak-check create secret generic app-secrets \
  --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
  --from-literal=GITHUB_PERSONAL_ACCESS_TOKEN="$GITHUB_PERSONAL_ACCESS_TOKEN"
```

## Verify
```bash
kubectl -n speak-check rollout status deploy/speak-check-app
kubectl -n speak-check get pods,svc
curl -f http://localhost:8501/_stcore/health
```

## Access
- App: http://localhost:8501
- MongoDB (local tools): localhost:27018 -> cluster 27017

## Cleanup
```bash
k3d cluster delete speak-check
```
