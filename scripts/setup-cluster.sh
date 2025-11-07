#!/bin/sh

kind create cluster --config ./k8s/kind-config.yaml

kind load docker-image smllr:dev --name smllr

kubectl apply -f ./k8s/namespace.yaml
kubectl apply -f ./k8s
kubectl apply -f ./k8s/traefik/namespace.yaml

helm repo add traefik https://traefik.github.io/charts
helm repo update

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ./k8s/traefik/certs/tls.key -out ./k8s/traefik/certs/tls.crt \
  -subj "/CN=*.docker.localhost"

kubectl create secret tls local-selfsigned-tls \
  --cert=./k8s/traefik/certs/tls.crt --key=./k8s/traefik/certs/tls.key \
  --namespace traefik

helm install traefik traefik/traefik --namespace traefik --values ./k8s/traefik/values.yaml

kubectl apply -f ./k8s/ingress-route.yaml
