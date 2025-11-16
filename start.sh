#!/bin/bash

# Start the API server
uvicorn api:app --reload --host 0.0.0.0 --port 8000 &

# Wait for 3 seconds
sleep 3

# Start the bot
python bot.py