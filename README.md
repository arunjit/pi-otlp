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

### 1. Start the stack

You can pass a profile directly using `--env-file`:

```bash
# Run with the small_pi profile (1-2GB RAM):
podman compose --env-file profiles/small_pi.env up -d

# Or run with the big_pi profile (4GB+ RAM):
podman compose --env-file profiles/big_pi.env up -d

# Or run with the server profile:
podman compose --env-file profiles/server.env up -d
```

Alternatively, copy your preferred profile to `.env` once:

```bash
cp profiles/small_pi.env .env
podman compose up -d
```
*(If neither `.env` nor `--env-file` is specified, the compose file automatically falls back to `small_pi` defaults).*

### 2. Send OTLP Metrics

Configure your application or OpenTelemetry SDK to send HTTP metrics to:

```bash
export OTEL_EXPORTER_OTLP_METRICS_ENDPOINT="http://<pi-ip>:8428/opentelemetry/v1/metrics"
export OTEL_EXPORTER_OTLP_METRICS_PROTOCOL="http/protobuf"
```

### 3. View Dashboards

Open `http://<pi-ip>:3000` in your browser (default login: `admin` / `admin`). VictoriaMetrics is already configured as the default Prometheus datasource.

---

## Raspberry Pi Prerequisite (Memory Limits)

Raspberry Pi OS disables kernel memory cgroups by default. If you see:
```text
crun: opening file `memory.max` for writing: No such file or directory
```
Enable memory cgroups in your boot config:

1. Edit `/boot/firmware/cmdline.txt` (or `/boot/cmdline.txt` on older OS releases):
   ```bash
   sudo nano /boot/firmware/cmdline.txt
   ```
2. Append to the end of the **single line** (do not add a new line):
   ```text
   cgroup_enable=memory cgroup_memory=1
   ```
3. Reboot:
   ```bash
   sudo reboot
   ```
