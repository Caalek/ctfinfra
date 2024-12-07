CTFD_HELM_CHART_DIR=ctfd-helm-chart
CHART_VERSION="0.1"
IMAGE_REPO=
IMAGE_TAG=ctfd
KUBE_NS:="ctfd"
CHART_NAME=$(CTFD_HELM_CHART_DIR)
.PHONY: docker/build-ctfd
docker/build:
	docker build --tag $(IMAGE_REPO):$(IMAGE_TAG) ctfd-dockerfile/

.PHONY: docker/push-ctfd
docker/push:
	docker push $(IMAGE_REPO):$(IMAGE_TAG)

.PHONY: helm/build
helm/build:
	helm package $(CTFD_HELM_CHART_DIR) --version $(CHART_VERSION) --dependency-update

.PHONY: helm/deploy
helm/deploy: helm/build
	helm uninstall $(CHART_NAME) -n $(KUBE_NS) 2>/dev/null || true
	kubectl delete ev --all -n $(KUBE_NS)
	helm install $(CHART_NAME) $(CHART_NAME)				\
		--namespace $(KUBE_NS) --create-namespace		\
		-f "$(CTFD_HELM_CHART_DIR)/values.yaml"

helm/update:
	helm upgrade $(CHART_NAME) $(CHART_NAME)				\
		--namespace $(KUBE_NS) --create-namespace		\
		-f "$(CTFD_HELM_CHART_DIR)/values.yaml"