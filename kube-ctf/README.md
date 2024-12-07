kube-ctf
========

Pre-configured kubernetes infrastructure with load balancing and some network hardening enabled. Also contains
per-team challenge assignment for web challenges. Inspired by [kCTF](https://github.com/google/kctf).

## How to Setup
1. Create the cluster
```sh
./scripts/cluster-deploy
```

2. Configure the cluster and IAM resources.
```sh
./scripts/cluster-configure
```

3. Install the cluster resources.
```sh
./scripts/cluster-install
```

4. Create config/values.yaml and populate it with values.
```yaml
#TODO: Update before deploying
challenge-manager:
  authSecret: <secret_that_you_put_in_ctfd_kubectf_plugin_config>
  registryPrefix: europe-west1-docker.pkg.dev/<project_id>/repo-name


googleProject: 
googleRegion: 
googleRepositoryName: 



domain:
  challenges: <challenge root domain> # challenges will be a subdomain of this
  management: <root domain> # This url is going to be used for contacting the challenge-manager using https://challenge-manager.<this_domain>

replicas:
  challenge-manager: 2

cert:
  email: <contact email> # required for letsencrypt
  cfDNSToken: <cloudflare dns token> # used to configure dns-01 certificate validation
```

4. Deploy the helm stack.
```sh
helm install kubectf -f config/values.yaml chart/
```

5. Upload the sample whoami challenge for testing.
```sh
kubectl apply -f templates/whoami/kube-isolated.yaml
```

## How to Deploy Isolated Challenges
See the README at [services/challenge-manager](services/challenge-manager)

## Authors
- [BlueAlder](https://github.com/BlueAlder)
- [jordanbertasso](https://github.com/jordanbertasso)
- [lecafard](https://github.com/lecafard)
