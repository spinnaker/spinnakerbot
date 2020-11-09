PROJECT=spinnaker-community
DOCKER_REGISTRY=us-docker.pkg.dev/spinnaker-community/spinbot

BRANCH := $(shell git rev-parse --abbrev-ref HEAD)

init:
	python3 -m pip install -r requirements.txt

docker:
	gcloud builds submit . \
      --config cloudbuild.yaml \
      --project ${PROJECT} \
      --substitutions=TAG_NAME=${BRANCH}-latest,_DOCKER_REGISTRY=${DOCKER_REGISTRY}

.PHONY: init docker
