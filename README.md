# Climate Data K8s Infrastructure

Kubernetes deployment infrastructure for ARCO (Analysis-Ready, Cloud-Optimised) climate data services. Designed for deployment on ECMWF Common Cloud Infrastructure (CCI).

## Overview

This repository contains production-ready Kubernetes configurations for deploying cloud-native climate data services:

- **Helm Charts** - Complete Helm chart for ARCO service deployment
- **Docker** - Multi-stage Dockerfile for containerised API
- **CI/CD** - GitHub Actions workflow with self-hosted runner support
- **Monitoring** - Prometheus metrics and Grafana integration

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Ingress   │  │   Service   │  │     HPA     │         │
│  │  (NGINX)    │──│  (ClusterIP)│──│ (Autoscale) │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         │                │                │                 │
│         ▼                ▼                ▼                 │
│  ┌─────────────────────────────────────────────┐           │
│  │              ARCO Service Pods              │           │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐     │           │
│  │  │  Pod 1  │  │  Pod 2  │  │  Pod N  │     │           │
│  │  │ FastAPI │  │ FastAPI │  │ FastAPI │     │           │
│  │  └─────────┘  └─────────┘  └─────────┘     │           │
│  └─────────────────────────────────────────────┘           │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Prometheus  │  │   Grafana   │  │Elasticsearch│         │
│  │  (Metrics)  │  │ (Dashboards)│  │  (Logging)  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  S3 Data Lake   │
│  (Zarr Stores)  │
└─────────────────┘
```

## Quick Start

### Prerequisites

- Kubernetes cluster (1.24+)
- Helm 3.x
- kubectl configured for your cluster

### Deploy with Helm

```bash
# Add values for your environment
helm install arco-service ./helm/arco-service \
  --namespace arco \
  --create-namespace \
  --set image.repository=your-registry/arco-service \
  --set image.tag=latest \
  --set dataLake.endpoint=s3://your-arco-data-lake
```

### Environment-specific deployments

```bash
# Development
helm install arco-service ./helm/arco-service -f helm/arco-service/values-dev.yaml

# Staging
helm install arco-service ./helm/arco-service -f helm/arco-service/values-staging.yaml

# Production
helm install arco-service ./helm/arco-service -f helm/arco-service/values-prod.yaml
```

## Repository Structure

```
climate-data-k8s/
├── .github/
│   └── workflows/
│       └── ci.yaml              # GitHub Actions CI/CD pipeline
├── docker/
│   └── Dockerfile               # Multi-stage container build
├── helm/
│   └── arco-service/
│       ├── Chart.yaml           # Helm chart metadata
│       ├── values.yaml          # Default configuration
│       └── templates/
│           ├── _helpers.tpl     # Template helpers
│           ├── deployment.yaml  # K8s Deployment
│           ├── service.yaml     # K8s Service
│           ├── ingress.yaml     # Ingress routing
│           ├── hpa.yaml         # Horizontal Pod Autoscaler
│           ├── networkpolicy.yaml # Network security
│           └── servicemonitor.yaml # Prometheus integration
├── k8s/                         # Raw K8s manifests (alternative)
└── scripts/                     # Deployment utilities
```

## Helm Chart Features

### Deployment

- Rolling updates with zero downtime
- Configurable resource limits and requests
- Liveness and readiness probes
- Environment variable configuration
- Secret management for credentials

### Autoscaling

- Horizontal Pod Autoscaler (HPA)
- CPU and memory-based scaling
- Configurable min/max replicas
- Scale-down stabilisation

### Networking

- ClusterIP service with configurable ports
- Ingress with TLS termination
- Network policies for pod-to-pod security
- CORS configuration

### Monitoring

- Prometheus ServiceMonitor for metrics scraping
- `/metrics` endpoint exposure
- Custom metric annotations
- Grafana dashboard templates

## Configuration

### Key Values

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of pod replicas | `2` |
| `image.repository` | Container image repository | `arco-service` |
| `image.tag` | Container image tag | `latest` |
| `service.port` | Service port | `8000` |
| `ingress.enabled` | Enable ingress | `true` |
| `ingress.hosts[0].host` | Ingress hostname | `arco.example.com` |
| `resources.limits.cpu` | CPU limit | `1000m` |
| `resources.limits.memory` | Memory limit | `2Gi` |
| `autoscaling.enabled` | Enable HPA | `true` |
| `autoscaling.minReplicas` | Minimum replicas | `2` |
| `autoscaling.maxReplicas` | Maximum replicas | `10` |
| `dataLake.endpoint` | S3 data lake endpoint | `s3://arco-data-lake` |

### Example values-prod.yaml

```yaml
replicaCount: 3

resources:
  limits:
    cpu: 2000m
    memory: 4Gi
  requests:
    cpu: 500m
    memory: 1Gi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: arco-api.ecmwf.int
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: arco-api-tls
      hosts:
        - arco-api.ecmwf.int
```

## CI/CD Pipeline

The GitHub Actions workflow provides:

1. **Build** - Multi-stage Docker build
2. **Test** - Run pytest suite
3. **Scan** - Container security scanning
4. **Push** - Push to container registry
5. **Deploy** - Helm upgrade to cluster

### Self-hosted Runners

Supports ECMWF self-hosted runners per CJS2_231 requirements:

```yaml
runs-on: [self-hosted, linux, x64]
```

## Monitoring

### Prometheus Metrics

The service exposes metrics at `/metrics`:

- `arco_requests_total` - Total request count by endpoint
- `arco_request_latency_seconds` - Request latency histogram
- `arco_data_access_seconds` - Data lake access latency

### Grafana Dashboard

Import the included dashboard for:

- Request rate and latency
- Error rates by endpoint
- Pod resource utilisation
- Autoscaling events

## Security

### Network Policies

- Restrict ingress to ingress controller only
- Allow egress to data lake endpoints
- Deny inter-pod communication by default

### Pod Security

- Non-root container execution
- Read-only root filesystem
- Dropped capabilities
- Resource quotas enforced

## Related Repositories

| Repository | Description |
|------------|-------------|
| [climate-data-pipeline](https://github.com/vulcan2018/climate-data-pipeline) | ARCO data processing pipeline |
| [arco-demo](https://github.com/vulcan2018/arco-demo) | Live demonstration |
| [climate-viz-frontend](https://github.com/vulcan2018/climate-viz-frontend) | Visualisation frontend |

## Live Demo

- **Demo Site**: https://arco-demo.vercel.app
- **Pipeline Demo**: https://climate-data-pipeline.vercel.app
- **Viz Frontend**: https://climate-viz-frontend.vercel.app

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

**FIRA Software Ltd**
https://firasoftware.com

Developed for CJS2_220b_bis Extended ARCO tender submission.
