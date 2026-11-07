# PiOTLP

A lightweight, containerized OpenTelemetry (OTLP) metrics and dashboarding stack designed for low-resource edge devices (like Raspberry Pi) up to dedicated servers.

Powered by **[VictoriaMetrics](https://victoriametrics.com/)** and **[Grafana](https://grafana.com/)**.

---

## Architecture & Endpoints

| Service | Port | Endpoint / Purpose |
| :--- | :--- | :--- |
| **VictoriaMetrics** | `8428` | **OTLP Ingestion**: `http://<host>:8428/opentelemetry/v1/metrics`<br>**Prometheus Query API & UI**: `http://<host>:8428` |
| **Grafana** | `3000` | **Web UI**: `http://<host>:3000`<br>Pre-provisioned with VictoriaMetrics as the default datasource. |

*Note: VictoriaMetrics single-node serves OTLP metrics directly over its HTTP server (port 8428).*

---

## Hardware Profiles

Pre-tuned environment configurations are available in [`profiles/`](profiles/):

* **`small_pi`** (`profiles/small_pi.env`): **1–2GB RAM** (Raspberry Pi 3/4/5 1–2GB, Pi Zero 2W). Caps total container limits at ~296MB; disables background alerting to save memory.
* **`big_pi`** (`profiles/big_pi.env`): **4GB+ RAM** (Raspberry Pi 5/4 4GB/8GB, mini-PCs). Enables Grafana alerting, increases cache sizes, and scales query concurrency.
* **`server`** (`profiles/server.env`): **8GB+ RAM** (Dedicated servers, high-ingestion hosts).

---

## Quick Start

### 1. Select a profile
Copy the profile suited for your hardware to `.env` (defaults to `small_pi` if omitted):

```bash
# For a 1-2GB Raspberry Pi:
cp profiles/small_pi.env .env

# For a 4GB / 8GB Raspberry Pi:
cp profiles/big_pi.env .env

# For a server:
cp profiles/server.env .env
```

### 2. Start the stack

```bash
podman compose up -d
```
*(Also compatible with `docker compose`).*

### 3. Send OTLP Metrics

Configure your application or OpenTelemetry SDK to send HTTP metrics to:

```bash
export OTEL_EXPORTER_OTLP_METRICS_ENDPOINT="http://<pi-ip>:8428/opentelemetry/v1/metrics"
export OTEL_EXPORTER_OTLP_METRICS_PROTOCOL="http/protobuf"
```

### 4. View Dashboards

Open `http://<pi-ip>:3000` in your browser (default login: `admin` / `admin`). VictoriaMetrics is already configured as the default Prometheus datasource.
