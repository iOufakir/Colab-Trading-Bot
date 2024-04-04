from flask import Flask, jsonify, render_template_string
import gdown
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter

app = Flask(__name__)

@app.route('/')
def home():
    return 'Home Page Route'


@app.route("/api/run-colab")
def run_colab():
    # Download the Colab notebook
    gdown.download(
        "https://drive.google.com/uc?id=1wUm_EV7nivXq7JbN7RUeG2E6w9ismXxN",
        ".vercel/output/smartBot.ipynb",
        quiet=False,
    )

    # Execute the downloaded notebook
    result = execute_notebook(".vercel/output/smartBot.ipynb")

    return render_template_string(result)


def execute_notebook(notebook_path):
    # Load the notebook
    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    # Get the kernel name from notebook metadata
    kernel_name = nb.metadata.kernelspec.name
    # Create an ExecutePreprocessor
    ep = ExecutePreprocessor(timeout=None, kernel_name=kernel_name)
    
    executed_nb = ''
    try:
        print("Executing notebook...")
        executed_nb, _ = ep.preprocess(nb, {"metadata": {"path": "."}})
        print("Notebook executed successfully")
    except Exception as e:
        execution_result = f"Error executing notebook: {str(e)}"
        print(execution_result)
        return execution_result
    
    # Convert executed notebook to HTML for display
    html_exporter = HTMLExporter()
    html_body, _ = html_exporter.from_notebook_node(executed_nb)
    return html_body


if __name__ == "__main__":
    app.run(port=3000)
