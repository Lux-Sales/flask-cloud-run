#!/bin/bash

export FLASK_APP=app:app
flask run --port=8080 --host=0.0.0.0
