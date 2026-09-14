#!/usr/bin/env bash
echo "Setting up CourierAI Environment..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "Environment ready! Run 'streamlit run Front-End/main.py' to launch UI."
