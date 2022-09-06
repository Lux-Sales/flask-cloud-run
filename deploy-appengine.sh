#!/bin/bash

gcloud app deploy alunos/app.yaml --quiet \
&& gcloud app deploy materias/app.yaml --quiet \
&& gcloud app deploy default/app.yaml --quiet \
&& gcloud app deploy dispatch.yaml --quiet
