.PHONY: clone debug-config doctor venv

clone:
	@bash scripts/clone-repo.sh

doctor: 
	@bash scripts/doctor.sh

venv:
	@echo "Run: source scripts/venv.sh"

debug-config:
	@python vscode/debug_launch.py