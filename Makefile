TOOLKIT = toolkit

# --- Support (eseguire prima dei dataset principali) ---

SUPPORT = \
	support/opencivitas-fsc-enti-rso \
	support/opencivitas-glossario

.PHONY: support
support:
	@for d in $(SUPPORT); do \
		echo "=== $$d ==="; \
		$(TOOLKIT) run --config $$d/dataset.yml || exit 1; \
	done

# --- Dataset principali ---

.PHONY: run-determinanti run-fsc-rso run-indicatori run-all
run-determinanti:
	$(TOOLKIT) run --config datasets/opencivitas-determinanti/dataset.yml

run-fsc-rso:
	$(TOOLKIT) run --config datasets/opencivitas-fsc-rso/dataset.yml

run-indicatori:
	$(TOOLKIT) run --config datasets/opencivitas-indicatori/dataset.yml

run-all: support run-determinanti run-fsc-rso run-indicatori

# --- Validazione config ---

.PHONY: check
check:
	@for f in $$(find support -name dataset.yml | sort); do \
		echo "→ $$f"; \
		$(TOOLKIT) run preflight --config "$$f" --years 2025 > /dev/null 2>&1 || exit 1; \
	done
	@for f in $$(find datasets -name dataset.yml | sort); do \
		echo "→ $$f"; \
		$(TOOLKIT) run preflight --config "$$f" --years 2022 > /dev/null 2>&1 || exit 1; \
	done
	@echo "All configs valid"

# --- Dashboard ---

.PHONY: dashboard
dashboard:
	cd dashboard && streamlit run app.py

# --- Pulizia ---

.PHONY: clean
clean:
	rm -rf out/

# --- Registry ---

.PHONY: registry registry-write
registry:
	$(TOOLKIT) registry build --prefix opencivitas

registry-write:
	$(TOOLKIT) registry build --prefix opencivitas --write

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:' Makefile | sort
