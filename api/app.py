from flask import Flask, render_template_string
import nbformat
from nbconvert import HTMLExporter
import requests, subprocess
from nbconvert.preprocessors import ExecutePreprocessor
import os, sys, logging
from threading import Thread
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
import datetime
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)

colabUrl = "https://drive.google.com/uc?id=1wUm_EV7nivXq7JbN7RUeG2E6w9ismXxN"
outputFile = "./data/smartBot.ipynb"

gemini_prompt = """
Context: As a financial data model, is it a good idea to buy NVDA stock based on the current date/time? Do quick market research, check Yahoo data, analytics and any provided data and give me a quick response.

Details: Reply with one word: positive, neutral or negative. (positive to buy, and negative to sell)

Prompt: Based on the current date/time '%s', should I buy a $NVDA stock right now?
"""


@app.route("/")
def home():
    return "Home Page Route"

@app.route("/api/run-gemini")
def run_gemini():
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-pro")

    response = model.generate_content(gemini_prompt)

    logger.info("Gemini response feedback: %s", response.prompt_feedback)
    send_email(response.text, "Gemini Result", "dev@il-yo.com", "dev@il-yo.com")
    return response.text


@app.route("/api/run-colab", methods=["HEAD"])
def run_colab():
    # Download file from gdrive
    download_file()

    # Background task
    background_task = Thread(target=execute_background_task)
    background_task.start()

    return "Colab notebook has been executed!", 202


def execute_background_task():
    # Execute the colab notebook
    result = execute_notebook()
    # Send email with the result
    send_email(result, "Colab Result", "dev@il-yo.com", "dev@il-yo.com")


def download_file():
    try:
        os.makedirs(
            os.path.dirname(outputFile), exist_ok=True
        )  # Create folder if it doesn't exist
        response = requests.get(colabUrl, allow_redirects=True)
        with open(outputFile, "wb") as f:
            f.write(response.content)
    except Exception as e:
        logger.error("Error downloading file", exc_info=True)


def execute_notebook():
    # Load the notebook
    with open(outputFile, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)
    # Get the kernel name from notebook metadata
    kernel_name = nb.metadata.kernelspec.name
    logger.info(f"kernel: {kernel_name}")
    # Create an ExecutePreprocessor
    ep = ExecutePreprocessor(
        timeout=None, kernel_name=kernel_name, store_widget_state=False
    )

    executed_nb = ""
    try:
        logger.info("Executing notebook...")
        executed_nb, _ = ep.preprocess(nb, {"metadata": {"path": "./data"}})
        logger.info("Notebook executed successfully")
    except Exception as e:
        execution_result = f"Error executing notebook: {str(e)}"
        logger.info(execution_result)
        return execution_result

    # Convert executed notebook to HTML for display
    html_exporter = HTMLExporter()
    html_body, _ = html_exporter.from_notebook_node(executed_nb)
    return html_body


def send_email(body, subject, sender_email, recipient_email):
    message = Mail(
        from_email=sender_email,
        to_emails=recipient_email,
        subject=subject,
        html_content=body,
    )

    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        result = sg.send(message)
        logger.info("Email sent successfully : %s", result.status_code)
    except Exception as e:
        logger.error("Error sending email:", e)


def get_current_time():
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %I:%M %p")
    return formatted_datetime


def _init_logger():
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = _init_logger()  # Initialize logger


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
