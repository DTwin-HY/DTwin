# Software architecture

## Deployment diagram

![deployment diagram](./assets/deployment-diagram.png)

This project is designed to be deployed to OpenShift OKD distribution of Kubernetes. The manifests for the deployments, services, image streams, and routes are included in the [manifests](../manifests/) folder. The pods use image streams and triggers to update themselves when the target image is updated.

### OpenShift Route
The OpenShift Route node is a route in OpenShift OKD, that exposes the Nginx Frontend Pod's service to external traffic.

### Nginx Frontend Pod
The Nginx Frontend Pod functions as a reverse proxy and a static file server for the Vite + React frontend of the project. 

### Flask Backend Pod
The Flask Backend Pod contains all the backend logic of the project, implemented as a WSGI server using Gunicorn and Flask.

### PostgreSQL Pod
The PostgreSQL Pod is implemented with OKD's (or CSC's Rahti's) default PostgreSQL template with persistent storage.