from flask import Flask, render_template_string
import nbformat
from nbconvert import HTMLExporter
import requests, subprocess
import os, sys, logging, schedule, time
from threading import Thread
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

colabUrl = "https://drive.google.com/uc?id=1wUm_EV7nivXq7JbN7RUeG2E6w9ismXxN"
outputFile = "./data/smartBot.ipynb"
    
@app.route("/")
def home():
    return "Home Page Route"


@app.route("/api/run-colab", methods=['HEAD'])
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
    send_email(result, "Colab Result", "dev@il-yo.com", "contact@il-yo.com")

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
    try:
        # Run the Jupyter command to execute the notebook
        subprocess.run(['jupyter', 'nbconvert', '--to', 'notebook', '--execute', outputFile])

        # Read the executed notebook
        with open(outputFile, "r", encoding="utf-8") as f:
            executed_nb = nbformat.read(f, as_version=4)

        logger.info("Notebook executed successfully")

        # Convert executed notebook to HTML for display
        html_exporter = HTMLExporter()
        html_body, _ = html_exporter.from_notebook_node(executed_nb)
        return html_body
    except Exception as e:
        execution_result = f"Error executing notebook: {e}"
        logger.error(execution_result)
        return execution_result


def send_email(body, subject, sender_email, recipient_email):
    message = Mail(
        from_email=sender_email,
        to_emails=recipient_email,
        subject=subject,
        html_content=body)

    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        result = sg.send(message)
        logger.info("Email sent successfully : %s", result.status_code)
    except Exception as e:
        logger.error("Error sending email:", e)


def _init_logger():
    logger = logging.getLogger('app')
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = _init_logger()  # Initialize logger


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

