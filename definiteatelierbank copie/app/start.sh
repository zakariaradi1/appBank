#!/bin/bash
gunicorn -w 4 -b 0.0.0.0:$PORT -m "definiteatelierbank_copie.app:app"

