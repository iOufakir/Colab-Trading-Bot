# Trading Bot

## Description

This trading bot project executes a Colab notebook daily at 12pm UTC, fetching data, executing trades, and providing a summary of the trading activity. The bot uses Flask to create a web interface for triggering the trading process.

Notebook used behind the scenes:
`https://drive.google.com/uc?id=1wUm_EV7nivXq7JbN7RUeG2E6w9ismXxN`

## Installation

To run the trading bot locally, follow these steps:

`pip install -r requirements.txt`

## Usage

- Running the app locally using docker:
`docker build -t smartbot:latest .`
`docker run --name smartbot -p 5000:5000 smartbot SENDGRID_API_KEY=KEY`

Access the api at `http://localhost:5000/api/run-colab` to trigger the trading process.
