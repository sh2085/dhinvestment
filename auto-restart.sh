#!/bin/bash

echo "🚀 Python 코드 변경 감지중... 변경되면 자동으로 docker-compose restart 합니다."

find . -type f -name "*.py" | entr -r docker-compose restart
