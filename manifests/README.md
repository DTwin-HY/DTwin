# Kubernetes manifests

* Apply a specific manifest with the command `oc apply -f manifest_name.yaml`
* Apply all the manifests with the command `oc apply -f .`
* To synchronize existing manifests on the cluster use the command `oc apply -k .`
* Set image stream triggers with `oc set triggers deploy/frontend --from-image=dtwin-frontend:staging -c frontend` (for frontend for example).
* To quickly refresh the image without waiting for the next check (every 15 minutes), use the command `oc import image dtwin-frontend:staging` with the desired image.