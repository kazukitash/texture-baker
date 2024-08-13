#!/bin/bash

cd $(dirname $0)
rm texture-baker.zip
zip -r texture-baker.zip . -x "*.venv*" -x "*.git*" -x "*.vscode*" -x "*.gitignore*" -x "*poetry.lock*" -x "*pyproject.toml*" -x "*README.md*" -x "*setup.sh*" -x "*.DS_Store*"
