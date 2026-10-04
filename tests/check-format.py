#!/usr/bin/env python3
# Checks the text that `make test` writes to tests/tmp/sample.prom with
# prometheus_client's parser and, when installed, `promtool check metrics`.
import math, subprocess, shutil, sys

path = sys.argv[1] if len(sys.argv) > 1 else "tests/tmp/sample.prom"
text = open(path, encoding="utf-8").read()

from prometheus_client.parser import text_string_to_metric_families

families = {f.name: f for f in text_string_to_metric_families(text)}

def sample(name, **labels):
    for f in families.values():
        for s in f.samples:
            if s.name == name and s.labels == labels:
                return s.value
    raise SystemExit(f"missing sample {name} {labels}")

assert families["plain"].type == "counter"
assert sample("plain_total") == 3.25
assert families["labeled"].documentation == "Help with \\ and\nnewline."
assert sample("labeled_total", path='/a "quoted"', code="200") == 1
assert sample("labeled_total", path="back\\slash\nnewline", code="500") == 2
assert sample("labeled_total", path="", code="日本") == 1
assert math.isnan(sample("special_values", v="nan"))
assert sample("special_values", v="inf") == math.inf
assert sample("special_values", v="ninf") == -math.inf
assert sample("special_values", v="tiny") == -1.5e-300
assert sample("special_values", v="huge") == 1.7e308
assert families["latency_seconds"].type == "histogram"
assert sample("latency_seconds_bucket", op="read", le="0.005") == 1
assert sample("latency_seconds_bucket", op="read", le="+Inf") == 2
assert sample("latency_seconds_count", op="read") == 2
assert sample("latency_seconds_sum", op="write") == 12
assert sample("sizes_bucket", le="100") == 1
assert sample("callback_value") == 2
assert sample("valk_gc_heap_bytes") > 0
print(f"prometheus_client: {len(families)} families parsed")

promtool = shutil.which("promtool")
if promtool:
    # Lint rules about names and units are advice; only parse errors fail
    out = subprocess.run([promtool, "check", "metrics"], input=text.encode(), capture_output=True)
    print("promtool:", (out.stdout + out.stderr).decode().strip() or "no problems")
    if b"error while linting" in (out.stdout + out.stderr).lower():
        sys.exit(1)
