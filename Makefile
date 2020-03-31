PROJECT=spinnaker-marketplace
IMAGE=gcr.io/${PROJECT}/spinbot

BRANCH := $(shell git rev-parse --abbrev-ref HEAD)

init:
	python3 -m pip install -r requirements.txt

docker:
	gcloud builds submit . \
      --config cloudbuild.yaml \
      --project ${PROJECT} \
      --substitutions=TAG_NAME=${BRANCH}-latest,_PROJECT=${PROJECT}

.PHONY: init docker
