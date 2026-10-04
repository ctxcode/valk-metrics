# valk-metrics

Prometheus metrics for [Valk](https://valk-lang.dev) services: counters, gauges and histograms
with labels, updated from any thread with atomics, written in the text exposition format 0.0.4.
Includes an HTTP middleware that counts and times requests, and process and GC metrics.

Requires Valk 0.7.8 or newer.

## Install

```
vman install github.com/ctxcode/valk-metrics
```

## Example

```rust
use metrics
use valk.http
use valk.time

shared jobs: shared metrics.Counter (metrics.counter("app_jobs_total", "Jobs handled, by queue.", .{ "queue" }))
shared queued: shared metrics.Gauge (metrics.gauge("app_jobs_queued", "Jobs waiting to run."))
shared job_seconds: shared metrics.Histogram (metrics.histogram("app_job_seconds", "Time spent per job."))

fn handler(req: http.Request) http.Response {
    let start = time.mono_ns()
    queued.inc()
    jobs.with(.{ "mail" }).inc()
    queued.dec()
    job_seconds.observe_since(start)
    return http.Response.text("done")
}

fn main() {
    metrics.add_process_metrics()
    metrics.add_gc_metrics()

    let server = http.Server.new("0.0.0.0", 8080, handler)
    // Counts and times every request, and answers GET /metrics
    server.add_middleware(metrics.middleware())
    server.start() !!
}
```

`curl localhost:8080/metrics`:

```
# HELP app_jobs_total Jobs handled, by queue.
# TYPE app_jobs_total counter
app_jobs_total{queue="mail"} 1
...
# HELP http_requests_total HTTP requests answered, by method and status code.
# TYPE http_requests_total counter
http_requests_total{method="GET",status="200"} 1
# HELP http_request_duration_seconds Time spent answering HTTP requests, by method and status code.
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="GET",status="200",le="0.005"} 1
...
```

## Metrics

`metrics.counter`, `metrics.gauge` and `metrics.histogram` register a metric in the default
registry and return it as `shared`, so every thread can use it; keep it in a `shared` global as
above, or pass it to the code that needs it. A name can be registered once.

| | |
|---|---|
| `Counter` | `inc()`, `add(amount)`, `value()` |
| `Gauge` | `set(v)`, `inc()`, `dec()`, `add(v)`, `sub(v)`, `set_to_current_time()`, `value()` |
| `Histogram` | `observe(v)`, `observe_since(start_ns)`, `count()`, `sum()` |

Histograms take their upper bounds with `buckets:`; the default is `metrics.DEFAULT_BUCKETS`
(5 ms to 10 s), and `metrics.linear_buckets(start, width, count)` and
`metrics.exponential_buckets(start, factor, count)` make others. `+Inf` is always added.

```rust
let sizes = metrics.histogram("app_upload_bytes", "Upload sizes.", buckets: metrics.exponential_buckets(1024, 4, 8))
```

`gauge_fn` and `counter_fn` take a callback that gives the value each time the metrics are
written:

```rust
metrics.gauge_fn("app_cache_entries", "Entries in the cache.", fn() f64 { return cache_size() })
```

## Labels

A metric with label names holds one series per combination of values; `with` returns it, and
creates it the first time:

```rust
let requests = metrics.counter("app_requests_total", "Requests.", .{ "method", "status" })
requests.with(.{ "GET", "200" }).inc()

// Or keep the series and skip the lookup
let ok = requests.with(.{ "GET", "200" })
ok.inc()
```

A repeated `with` does not allocate and takes no lock: each thread remembers the series it
used. Calling `inc()` on a metric that has labels, or `with` with the wrong number of values,
panics. Every combination stays in memory and in the output, so keep values to a small set:
not user ids or raw paths.

## Serving

- `server.add_middleware(metrics.middleware())` counts requests in `http_requests_total` and
  times them in `http_request_duration_seconds`, by `method` and `status`, and answers
  `GET /metrics`. Options: `registry`, `path` (`""` serves nothing) and `buckets`. Methods
  outside the standard ones are counted as `other`. Static files and `fast` handlers do not
  pass through middleware.
- `metrics.handler()` is a handler that answers with the metrics, for a router or a server of
  its own: `router.add("GET", "/metrics", metrics.handler())`.
- `metrics.text()` and `registry.text()` return the text; `registry.write(out)` writes it to any
  `io.Writer`.

`metrics.add_process_metrics()` adds `process_cpu_seconds_total`, `process_start_time_seconds`,
`process_resident_memory_bytes`, `process_virtual_memory_bytes`, `process_open_fds` and
`process_max_fds`. `metrics.add_gc_metrics()` adds `valk_gc_heap_bytes` and
`valk_gc_heap_peak_bytes`.

## Registries

`metrics.Registry.new()` makes a separate set with the same methods as the module functions
(`counter`, `gauge`, `histogram`, `gauge_fn`, `counter_fn`, `add_process_metrics`,
`add_gc_metrics`, `text`, `write`). The middleware and handler take one as their first
argument.

## Benchmarks

Nanoseconds per call on each thread, with all threads updating the same metric, and calls
per second of all threads together. Ryzen 5 7600X, `make bench`; the Prometheus Go client
(client_golang 1.24.1, Go 1.27.1) for reference.

| | valk-metrics 1 thread | 4 threads | 8 threads | Go client 1 thread | 4 threads | 8 threads |
|---|---|---|---|---|---|---|
| `counter.inc()` | 1.3 ns | 17.8 ns (225M/s) | 47.8 ns (167M/s) | 1.5 ns | 21.0 ns (190M/s) | 49.2 ns (162M/s) |
| `counter.add(0.5)` | 3.0 ns | 42.3 ns (94M/s) | 133 ns (60M/s) | 3.3 ns | 76.4 ns (52M/s) | 192 ns (41M/s) |
| `gauge.add(1)` | 3.0 ns | 46.4 ns (86M/s) | 184 ns (44M/s) | 3.2 ns | 68.9 ns (57M/s) | 189 ns (42M/s) |
| `histogram.observe()` | 6.9 ns | 73.9 ns (54M/s) | 185 ns (43M/s) | 6.7 ns | 249 ns (16M/s) | 552 ns (14M/s) |
| `with("GET", "200").inc()` | 27.1 ns | 64.0 ns (63M/s) | 113 ns (71M/s) | 28.5 ns | 232 ns (17M/s) | 409 ns (19M/s) |
| `with("GET", "200").observe()` | 31.4 ns | 145 ns (28M/s) | 321 ns (25M/s) | 36.7 ns | 270 ns (14M/s) | 478 ns (16M/s) |

## Not supported

Summaries (quantiles), exemplars, native histograms, the OpenMetrics and protobuf formats,
removing a labeled series, and pushing to a Pushgateway. Process metrics other than the start
time are only read on Linux.

## Development

`make test` runs the suite, `make example` runs the example, `make bench` the benchmarks,
`make lint` checks the sources and `make docs` regenerates the API documentation.
`make check-format` checks the output with Python's `prometheus_client` parser, and with
`promtool check metrics` when it is installed.
