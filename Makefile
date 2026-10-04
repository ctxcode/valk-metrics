vc ?= valk

test:
	$(vc) build ./tests --test --run
lint:
	$(vc) build ./src --lint
example:
	$(vc) build ./example --run
bench:
	$(vc) build ./bench --run
# Needs python3 with prometheus_client; also runs promtool when it is installed
check-format: test
	python3 tests/check-format.py
docs:
	$(vc) doc . -o docs/api.md --markdown --no-private
	$(vc) doc . -o docs/api-full.md --markdown --no-private --full

.PHONY: test lint example bench check-format docs
