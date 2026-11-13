# PiOTLP End-to-End Python Example

A minimal containerized Python app managed with [`uv`](https://docs.astral.sh/uv/) that emits **metrics**, **logs**, and **traces** over OTLP gRPC to `pi-otlp`.

## Run Locally

1. **Start `pi-otlp` with the `full` profile** (from the repository root):
   ```bash
   podman compose --env-file profiles/big_pi.env up -d
   ```

2. **Start this example app** (from `example/`):
   ```bash
   cd example
   podman compose up --build
   ```
   *(Works identically with `docker compose` if you use Docker).*

3. **Verify all three signals:**
   - **Grafana:** Open `http://localhost:3000` (`admin` / `admin`) $\to$ **Explore**:
     - **VictoriaMetrics:** Query `demo_requests_total` or `demo_request_duration_ms_bucket`
     - **VictoriaLogs:** Query `pi-otlp-example` (includes correlated `trace_id` / `span_id`)
     - **VictoriaTraces:** Search for service `pi-otlp-example` to inspect `handle_sensor_ping` $\to$ `process_payload` spans
   - **Direct UIs:**
     - VictoriaMetrics: `http://localhost:8428/vmui`
     - VictoriaLogs: `http://localhost:9428/select/vmui/`
     - VictoriaTraces: `http://localhost:10428/select/vmui/`
