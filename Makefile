init:
	python -m venv myenv
	powershell -ExecutionPolicy Bypass
	myenv\Scripts\activate
	pip install -r requirements.txt
run:
	python server.py
