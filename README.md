### [optional] for local cluster

> 3 nodes, 4GB RAM, 4 vCPU, 30GB storage

#### Cluster init
1. **Disable swap!**

2. Create cluster
```bash
kubeadm init --pod-network-cidr=10.240.0.0/16
```

3. Join with other nodes
```bash
kubeadm join <control-plane-ip>:6443 --token <token> --discovery-token-ca-cert-hash sha256:<hash>
```

4. Configure kubectl
```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

#### Cluster configuration
For persistent volumes:
```bash
kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/master/deploy/local-path-storage.yaml
kubectl patch storageclass local-path -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```

For cluster networking:
> Flannel
> ```bash
> kubectl create ns kube-flannel
> kubectl label --overwrite ns kube-flannel pod-security.kubernetes.io/enforce=privileged
> helm repo add flannel https://flannel-io.github.io/flannel/
> helm install flannel --set podCidr="10.240.0.0/16" --namespace kube-flannel flannel/flannel
> ```
> ***OR***
>
> Calico (preferred)
>
> **Make sure that cidr value from *custom-resources.yaml* matches the subnet used in `kubeadm init` command**
> ```bash
> kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.29.1/manifests/tigera-operator.yaml
> curl https://raw.githubusercontent.com/projectcalico/calico/v3.29.1/manifests/custom-resources.yaml -O
> kubectl create -f custom-resources.yaml
> ```

```
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.7/config/manifests/metallb-native.yaml
kubectl apply -f ipaddresspool.yaml
kubectl apply -f l2advertisment.yaml
```

#### Tools

```bash
apt install docker-ce docker-ce-cli docker-buildx-plugin make
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | tee /usr/share/keyrings/helm.gpg > /dev/null
apt-get install apt-transport-https --yes
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | tee /etc/apt/sources.list.d/helm-stable-debian.list
apt-get update
apt-get install helm
```

## KubeCTF deploy

#### [optional] for GCP
```bash
cd kube-ctf
# cluster creation
./scripts/cluster-deploy
# GCP svc account config
./scripts/cluster-configure
# kube-ctf services build
./scripts/services-build
```

#### Configure
Edit `kube-ctf/chart/values.yaml`.
> Optionally edit `kube-ctf/services/landing/public/{index,404}.html` to change CTF name.

```bash
cd kube-ctf/services
docker build -t repo:landing landing
docker push repo:landing
docker build -t repo:challenge-manager challenge-manager
docker push repo:challenge-manager
```

#### Deploy

```bash
cd kube-ctf
cp chart/values.yaml.template chart/values.yaml
```

Edit `chart/values.yaml` to match your configuration.
```
./scripts/cluster-install
helm install kubectf chart/
```

## CTFd deploy

```bash
cd website
docker build -t <repo>:ctfd ctfd-dockerfile
docker push <repo>:ctfd
kubectl create namespace ctfd
```
Edit `Makefile` to match your configuration.
```
make docker/build
make docker/push
make helm/deploy
```

Edit `website/ingressRoute-traefik.yaml` to match your domain: ``match: Host(`example.com`)``
```bash
kubectl apply -f ingressRoute-traefik.yaml
```

---
---
## [optional] Kubernetes dashboard
Add helm repo:
`helm repo add kubernetes-dashboard https://kubernetes.github.io/dashboard/`

Install dasboard:
`helm upgrade --install kubernetes-dashboard kubernetes-dashboard/kubernetes-dashboard --create-namespace --namespace kubernetes-dashboard`

Create a file with user config:
```bash
apiVersion: v1
kind: ServiceAccount
metadata:
  name: USERNAME
  namespace: kubernetes-dashboard
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: USERNAME
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: USERNAME
  namespace: kubernetes-dashboard
```

Apply the configuration:
`kubectl apply -f filename.yaml`

Generate a token for the user:
`kubectl -n kubernetes-dashboard create token USERNAME [--duration 43200s]` (43200s = 30dni)

Forward port to access dashboard:
`kubectl -n kubernetes-dashboard port-forward svc/kubernetes-dashboard-kong-proxy 8443:443`

Dashboard is available at [https://localhost:8443](https://localhost:8443)

### Metrics server

Install metric server:
`kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml`

> If there are no metrics on dashboard edit metrics-server deployment:
> `kubectl edit deployment -n kube-system metrics-server`
> Add `--kubelet-insecure-tls` to `args`.

---
---
## Debugging
Getting elements:
`kubectl get {pod,service,...} NAME [-n namespace]`

Showing configuration:
`kubectl describe {pod,service,...} [-n namespace]`

Checking logs:
`kubectl logs {pod,service} [-n namespace] [-f]`

Port forwarding:
`kubectl port-forward service/NAME 8888:8000 [-n ns]`

Container shell access:
`kubectl exec -it pod/NAME [-n namespace] -- bash`

Pods and nodes they're deployed on:
`kubectl get pod -o=custom-columns=NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName --all-namespaces`
