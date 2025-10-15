# Kubernetes manifests

* Apply a specific manifest with the command `oc apply -f manifest_name.yaml`
* Apply all the manifests with the command `oc apply -f .`
* To synchronize existing manifests on the cluster use the command `oc apply -k .`
* Set image stream triggers with `oc set triggers deploy/frontend --from-image=dtwin-frontend:staging -c frontend` (for frontend for example).