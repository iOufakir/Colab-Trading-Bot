from flask import Flask, render_template_string
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter
import requests
import os
import logging
import schedule
import time

app = Flask(__name__)

@app.route("/")
def home():
    print('Hello world', flush=True);
    return "Home Page Route"


def schedule_ai_bot():
    schedule.every(1).minutes.do(home)
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route("/api/run-colab")
def run_colab():
    colabUrl = "https://drive.google.com/uc?id=1wUm_EV7nivXq7JbN7RUeG2E6w9ismXxN"
    outputFile = "./data/smartBot.ipynb"

    download_file(colabUrl, outputFile)

    # Execute the downloaded notebook
    result = execute_notebook(outputFile)

    return render_template_string(result)


def download_file(url, output):
    try:
        os.makedirs(
            os.path.dirname(output), exist_ok=True
        )  # Create folder if it doesn't exist
        response = requests.get(url, allow_redirects=True)
        with open(output, "wb") as f:
            f.write(response.content)
    except Exception as e:
        app.logger.error("Error downloading file", exc_info=True)


def execute_notebook(notebook_path):
    # Load the notebook
    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    # Get the kernel name from notebook metadata
    kernel_name = nb.metadata.kernelspec.name
    app.logger.info(kernel_name)
    # Create an ExecutePreprocessor
    ep = ExecutePreprocessor(timeout=None, kernel_name=kernel_name, allow_errors=True)

    executed_nb = ""
    try:
        app.logger.info("Executing notebook...")
        executed_nb, _ = ep.preprocess(nb, {"metadata": {"path": "./data"}})
        app.logger.info("Notebook executed successfully")
    except Exception as e:
        execution_result = f"Error executing notebook: {str(e)}"
        app.logger.info(execution_result)
        return execution_result

    # Convert executed notebook to HTML for display
    html_exporter = HTMLExporter()
    html_body, _ = html_exporter.from_notebook_node(executed_nb)
    return html_body


# app.logger conf
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)
    
if __name__ == "__main__":
    schedule_ai_bot()
    app.run()

