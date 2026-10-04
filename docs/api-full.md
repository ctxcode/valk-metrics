
# Documentation

Namespaces: [main](#main)

---

# main

## Aliases for 'main'

```js
// The `Content-Type` of the text exposition format.
+ value CONTENT_TYPE ("text/plain; version=0.0.4; charset=utf-8")
// The bucket bounds a histogram gets when none are given, in seconds: from 5 ms to 10 s, the same as the official Prometheus clients.
+ value DEFAULT_BUCKETS (.{ 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10 )
```

### CONTENT_TYPE

The `Content-Type` of the text exposition format.

### DEFAULT_BUCKETS

The bucket bounds a histogram gets when none are given, in seconds: from 5 ms to 10 s,
the same as the official Prometheus clients.

## Functions for 'main'

```js
// Adds the GC metrics to the default registry; see `Registry.add_gc_metrics`.
+ fn add_gc_metrics() void
// Adds the process metrics to the default registry; see `Registry.add_process_metrics`.
+ fn add_process_metrics() void
// Registers a counter in the default registry; see `Registry.counter`.
+ fn counter(name: String, help: String, labels: local &[String] (Array[String]{})) shared Counter
// Registers a callback counter in the default registry; see `Registry.counter_fn`.
+ fn counter_fn(name: String, help: String, callback: shared fn()(f64)) void
// Returns `count` bucket bounds: `start`, `start * factor`, `start * factor^2`, ...
+ fn exponential_buckets(start: f64, factor: f64, count: uint) Array[f64]
// Registers a gauge in the default registry; see `Registry.gauge`.
+ fn gauge(name: String, help: String, labels: local &[String] (Array[String]{})) shared Gauge
// Registers a callback gauge in the default registry; see `Registry.gauge_fn`.
+ fn gauge_fn(name: String, help: String, callback: shared fn()(f64)) void
// Returns an HTTP handler that answers with the metrics of `registry`, the default registry when not given.
+ fn handler(registry: ?shared Registry (null)) shared fn(Request)(Response)
// Registers a histogram in the default registry; see `Registry.histogram`.
+ fn histogram(name: String, help: String, labels: local &[String] (Array[String]{}), buckets: ?Array[f64] (null)) shared Histogram
// Returns `count` bucket bounds: `start`, `start + width`, `start + 2 * width`, ...
+ fn linear_buckets(start: f64, width: f64, count: uint) Array[f64]
// Returns a middleware for `http.Server.add_middleware` that counts every request and times it, by method and status code, and answers `GET <path>` with the metrics.
+ fn middleware(registry: ?shared Registry (null), path: String ("/metrics"), buckets: ?Array[f64] (null)) shared fn(Request, shared fn(Request)(Response))(Response)
// Returns the metrics of the default registry in the text exposition format 0.0.4.
+ fn text() String
```

### add_gc_metrics

Adds the GC metrics to the default registry; see `Registry.add_gc_metrics`.

### add_process_metrics

Adds the process metrics to the default registry; see `Registry.add_process_metrics`.

### counter

Registers a counter in the default registry; see `Registry.counter`.

### counter_fn

Registers a callback counter in the default registry; see `Registry.counter_fn`.

### exponential_buckets

Returns `count` bucket bounds: `start`, `start * factor`, `start * factor^2`, ...

### gauge

Registers a gauge in the default registry; see `Registry.gauge`.

### gauge_fn

Registers a callback gauge in the default registry; see `Registry.gauge_fn`.

### handler

Returns an HTTP handler that answers with the metrics of `registry`, the default
registry when not given.

```valk
router.add("GET", "/metrics", metrics.handler())
```

### histogram

Registers a histogram in the default registry; see `Registry.histogram`.

### linear_buckets

Returns `count` bucket bounds: `start`, `start + width`, `start + 2 * width`, ...

### middleware

Returns a middleware for `http.Server.add_middleware` that counts every request and
times it, by method and status code, and answers `GET <path>` with the metrics.

It registers `http_requests_total`, a counter, and `http_request_duration_seconds`, a
histogram with `buckets` (`DEFAULT_BUCKETS` when not given), both with the labels
`method` and `status`, in `registry` (the default registry when not given). Requests
for `path` are not counted; an empty `path` serves no metrics.

```valk
server.add_middleware(metrics.middleware())
```

### text

Returns the metrics of the default registry in the text exposition format 0.0.4.

## Classes for 'main'

```js
// A value that only goes up, such as requests served or bytes sent.
+ class Counter is Collector {
    // Adds `amount`, which may not be negative.
    + fn add(amount: f64) void
    // Adds 1.
    + fn inc() void
    // Returns the current value.
    + fn value() f64
    // Returns the series for these label values, one for each label name in order, and creates it on first use.
    + fn with(values: local &[String]) shared Counter
}
```

### Counter

A value that only goes up, such as requests served or bytes sent.

Made with `metrics.counter` or `Registry.counter`. All methods are safe to call from
any thread at once. A counter with label names holds one series per combination of
label values: `with` returns it.

```valk
shared requests: shared metrics.Counter (metrics.counter("app_requests_total", "Requests handled.", .{ "method" }))

requests.with(.{ "GET" }).inc()
```

#### add

Adds `amount`, which may not be negative.

#### inc

Adds 1.

#### value

Returns the current value.

#### with

Returns the series for these label values, one for each label name in order, and
creates it on first use.

A repeated call does not allocate; keep the result to skip the lookup altogether.
Panics when the number of values does not match the label names.

```js
// A value that goes up and down, such as connections in use or items in a queue.
+ class Gauge is Collector {
    // Adds `amount`, which may be negative.
    + fn add(amount: f64) void
    // Subtracts 1.
    + fn dec() void
    // Adds 1.
    + fn inc() void
    // Sets the value.
    + fn set(value: f64) void
    // Sets the value to the current Unix time in seconds.
    + fn set_to_current_time() void
    // Subtracts `amount`.
    + fn sub(amount: f64) void
    // Returns the current value.
    + fn value() f64
    // Returns the series for these label values, one for each label name in order, and creates it on first use.
    + fn with(values: local &[String]) shared Gauge
}
```

### Gauge

A value that goes up and down, such as connections in use or items in a queue.

Made with `metrics.gauge` or `Registry.gauge`. All methods are safe to call from any
thread at once. A gauge with label names holds one series per combination of label
values: `with` returns it.

```valk
shared queued: shared metrics.Gauge (metrics.gauge("app_jobs_queued", "Jobs waiting to run."))

queued.inc()
queued.dec()
```

#### add

Adds `amount`, which may be negative.

#### dec

Subtracts 1.

#### inc

Adds 1.

#### set

Sets the value.

#### set_to_current_time

Sets the value to the current Unix time in seconds.

#### sub

Subtracts `amount`.

#### value

Returns the current value.

#### with

Returns the series for these label values, one for each label name in order, and
creates it on first use.

A repeated call does not allocate; keep the result to skip the lookup altogether.
Panics when the number of values does not match the label names.

```js
// Counts observations, such as request durations or response sizes, in buckets.
+ class Histogram is Collector {
    // Returns the number of observations.
    + fn count() u64
    // Records one observation.
    + fn observe(value: f64) void
    // Records the seconds since `start_ns`, a reading of `time.mono_ns()`.
    + fn observe_since(start_ns: uint) void
    // Returns the sum of all observations.
    + fn sum() f64
    // Returns the series for these label values, one for each label name in order, and creates it on first use.
    + fn with(values: local &[String]) shared Histogram
}
```

### Histogram

Counts observations, such as request durations or response sizes, in buckets.

Made with `metrics.histogram` or `Registry.histogram`. The output has a cumulative
`_bucket` series per upper bound plus `+Inf`, and `_sum` and `_count`. All methods are
safe to call from any thread at once. A histogram with label names holds one series
per combination of label values: `with` returns it.

```valk
shared latency: shared metrics.Histogram (metrics.histogram("app_job_seconds", "Time spent per job."))

let start = time.mono_ns()
run_job()
latency.observe_since(start)
```

#### count

Returns the number of observations.

#### observe

Records one observation.

#### observe_since

Records the seconds since `start_ns`, a reading of `time.mono_ns()`.

#### sum

Returns the sum of all observations.

#### with

Returns the series for these label values, one for each label name in order, and
creates it on first use.

A repeated call does not allocate; keep the result to skip the lookup altogether.
Panics when the number of values does not match the label names.

```js
// A set of metrics that are written out together.
+ class Registry {
    // Adds the memory of valk's garbage collector: `valk_gc_heap_bytes`, the bytes held by the heap of all threads, and `valk_gc_heap_peak_bytes`, the most it held.
    + fn add_gc_metrics() void
    // Adds the standard process metrics: `process_cpu_seconds_total`, `process_start_time_seconds`, and on Linux also `process_resident_memory_bytes`, `process_virtual_memory_bytes`, `process_open_fds` and `process_max_fds`.
    + fn add_process_metrics() void
    // Registers a counter; with `labels`, one series per combination of their values.
    + fn counter(name: String, help: String, labels: local &[String] (Array[String]{})) shared Counter
    // Registers a counter whose value `callback` returns each time the metrics are written; the value should never go down.
    + fn counter_fn(name: String, help: String, callback: shared fn()(f64)) void
    // Registers a gauge; with `labels`, one series per combination of their values.
    + fn gauge(name: String, help: String, labels: local &[String] (Array[String]{})) shared Gauge
    // Registers a gauge whose value `callback` returns each time the metrics are written.
    + fn gauge_fn(name: String, help: String, callback: shared fn()(f64)) void
    // Registers a histogram; with `labels`, one series per combination of their values.
    + fn histogram(name: String, help: String, labels: local &[String] (Array[String]{}), buckets: ?Array[f64] (null)) shared Histogram
    // Creates an empty registry.
    + static fn new() shared Registry
    // Returns every metric in the text exposition format 0.0.4, in the order they were registered.
    + fn text() String
    // Writes every metric in the text exposition format 0.0.4.
    + fn write(out: Writer) void !io:IoError
}
```

### Registry

A set of metrics that are written out together.

Most programs use the default registry through the module functions; a registry of
your own keeps a separate set, for example per test. It is safe to use from any
thread. Registering two metrics with the same name panics.

#### add_gc_metrics

Adds the memory of valk's garbage collector: `valk_gc_heap_bytes`, the bytes
held by the heap of all threads, and `valk_gc_heap_peak_bytes`, the most it held.

#### add_process_metrics

Adds the standard process metrics: `process_cpu_seconds_total`,
`process_start_time_seconds`, and on Linux also `process_resident_memory_bytes`,
`process_virtual_memory_bytes`, `process_open_fds` and `process_max_fds`.

#### counter

Registers a counter; with `labels`, one series per combination of their values.

#### counter_fn

Registers a counter whose value `callback` returns each time the metrics are
written; the value should never go down.

The callback runs like the one of `gauge_fn`.

#### gauge

Registers a gauge; with `labels`, one series per combination of their values.

#### gauge_fn

Registers a gauge whose value `callback` returns each time the metrics are written.

The callback runs on the thread that writes the metrics, while the registry is
locked: keep it short and do not register metrics in it.

#### histogram

Registers a histogram; with `labels`, one series per combination of their values.

`buckets` are the upper bounds in increasing order, without `+Inf`, which is always
added; `DEFAULT_BUCKETS` when not given. See `linear_buckets` and `exponential_buckets`.

#### new

Creates an empty registry.

#### text

Returns every metric in the text exposition format 0.0.4, in the order they were
registered.

#### write

Writes every metric in the text exposition format 0.0.4.

## Globals for 'main'

```js
// The registry that `metrics.counter`, `metrics.gauge`, `metrics.histogram` and the other module functions use.
+ shared default_registry : Registry
```

### default_registry

The registry that `metrics.counter`, `metrics.gauge`, `metrics.histogram` and the
other module functions use.
