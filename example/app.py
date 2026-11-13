import logging
import os
import random
import signal
import sys
import time

from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

running = True


def _handle_signal(_signum: int, _frame: object) -> None:
    global running
    running = False


def init_telemetry() -> tuple[TracerProvider, MeterProvider, LoggerProvider]:
    """Initialize OTLP gRPC providers for traces, metrics, and logs."""
    resource = Resource.create(
        {
            "service.name": os.getenv("OTEL_SERVICE_NAME", "pi-otlp-example"),
            "service.version": "0.1.0",
        }
    )

    # 1. Traces
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(tracer_provider)

    # 2. Metrics
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(), export_interval_millis=5000
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    # 3. Logs (bridged from stdlib logging -> OTLP + stdout)
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter()))
    set_logger_provider(logger_provider)

    otel_handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(otel_handler)
    root_logger.addHandler(stdout_handler)

    return tracer_provider, meter_provider, logger_provider


def main() -> None:
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    tracer_provider, meter_provider, logger_provider = init_telemetry()
    tracer = trace.get_tracer(__name__)
    meter = metrics.get_meter(__name__)
    logger = logging.getLogger("pi-otlp-example")

    req_counter = meter.create_counter(
        name="demo_requests_total",
        description="Total synthetic requests processed",
    )
    latency_hist = meter.create_histogram(
        name="demo_request_duration_ms",
        unit="ms",
        description="Synthetic request duration in milliseconds",
    )

    interval = float(os.getenv("INTERVAL_SECONDS", "2.0"))
    seq = 0

    logger.info(
        "Started pi-otlp-example (OTLP endpoint=%s)",
        os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "default"),
    )

    while running:
        seq += 1
        with tracer.start_as_current_span("handle_sensor_ping") as parent_span:
            parent_span.set_attribute("ping.seq", seq)
            work_ms = random.uniform(12.0, 65.0)

            with tracer.start_as_current_span("process_payload") as child_span:
                time.sleep(work_ms / 1000.0)
                status = "error" if seq % 10 == 0 else "ok"
                child_span.set_attribute("status", status)

            req_counter.add(1, {"status": status})
            latency_hist.record(work_ms, {"status": status})

            if status == "error":
                logger.warning("Simulated warning on ping seq=%d (%.1f ms)", seq, work_ms)
            else:
                logger.info("Processed synthetic ping seq=%d (%.1f ms)", seq, work_ms)

        time.sleep(interval)

    logger.info("Shutting down telemetry providers...")
    tracer_provider.shutdown()
    meter_provider.shutdown()
    logger_provider.shutdown()


if __name__ == "__main__":
    main()
