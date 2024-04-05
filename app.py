from flask import Flask, render_template_string
import nbformat
from nbconvert import HTMLExporter
import requests, subprocess
import os, sys, logging, schedule, time
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route("/")
def home():
    logger.info('Hello')
    return "Home Page Route"


def schedule_ai_bot():
    schedule.every(1).hours.do(run_colab)
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

    send_email(result, "Colab Result", "dev@il-yo.com", "ouf.ilyas@gmail.com")
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
        logger.error("Error downloading file", exc_info=True)

def execute_notebook(notebook_path):
    try:
        # Run the Jupyter command to execute the notebook
        subprocess.run(['jupyter', 'nbconvert', '--to', 'notebook', '--execute', notebook_path])

        # Read the executed notebook
        with open(notebook_path, "r", encoding="utf-8") as f:
            executed_nb = f.read()

        logger.info("Notebook executed successfully")

        # Convert executed notebook to HTML for display
        html_exporter = HTMLExporter()
        html_body, _ = html_exporter.from_notebook_node(executed_nb)
        return html_body
    except Exception as e:
        execution_result = f"Error executing notebook: {str(e)}"
        logger.info(execution_result)
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
    send_email("Hello", "Colab Result", "dev@il-yo.com", "contact@il-yo.com")
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port)
    schedule_ai_bot()

