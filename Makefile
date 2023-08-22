# Makefile for Python project using pip

# Set up virtual environment
venv:
	python -m venv venv
	powershell -ExecutionPolicy Bypass
	@echo "Virtual environment created. Activate it using 'source venv/bin/activate'."

activate:
	@echo "Virtual environment created. Activate it using 'venv/bin/activate'."

install:
	pip install -r requirements.txt

# Update project dependencies
update:
	pip freeze > requirements.txt

# Run your project
run:
	python server.py

# Clean up generated files
clean:
	rm -rf venv
	find . -name "__pycache__" -exec rm -r {} +
	rm -rf *.egg-info
	rm -rf dist build

# Help command to display available tasks
help:
	@echo "Available tasks:"
	@echo "  - make venv       : Create a virtual environment"
	@echo "  - make install    : Install project dependencies from requirements.txt"
	@echo "  - make update     : Update requirements.txt with currently installed packages"
	@echo "  - make run        : Run your project"
	@echo "  - make clean      : Clean up generated files"
	@echo "  - make help       : Show this help message"

