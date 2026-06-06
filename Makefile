.PHONY: install uninstall install-system install-user dev test

PREFIX ?= /usr/local
INSTALL_DIR ?= $(HOME)/.local/bin

install-user:
	@echo "Installing waybar-jalaly-calendar for current user..."
	pip install --user -e .
	@echo ""
	@echo "Done! Make sure $(INSTALL_DIR) is in your PATH."
	@echo "Then add 'custom/shamsi-date' to your Waybar config (see config/)."

install-system:
	@echo "Installing waybar-jalaly-calendar system-wide..."
	sudo pip install -e .
	@echo "Done!"

install: install-user

uninstall:
	pip uninstall waybar-jalaly-calendar -y
	rm -f /tmp/waybar-jalaly-state
	@echo "Uninstalled."

dev:
	pip install -e .
	@echo "Development install complete."

test:
	pip install -e ".[test]"
	python -m pytest tests/ -v
