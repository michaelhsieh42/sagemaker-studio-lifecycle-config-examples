#!/bin/bash

set -eux

# Replace this with the URL of your git repository
export REPOSITORY_URL=https://github.com/michaelhsieh42/sagemaker-studio-lifecycle-config-examples.git

mkdir -p .cost-dashboard/

for i in app.py gui.py requirements.txt;do
    curl https://raw.githubusercontent.com/michaelhsieh42/sagemaker-studio-lifecycle-config-examples/main/scripts/cost-dashboard/streamlit-app/${i} > .cost-dashboard/${i}
done

pip install -r requirements.txt
streamlit run .cost-dashboard/app.py --server.port 80 &
