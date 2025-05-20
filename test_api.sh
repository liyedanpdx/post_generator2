#!/bin/bash

# 测试API
echo "测试LinkedIn Post Auto Editor API"

# 设置API URL（默认为本地）
API_URL=${1:-"http://localhost:5001"}

# 测试API信息
echo -e "\n\033[1;34m测试 API 信息...\033[0m"
curl -s ${API_URL}/ | python -m json.tool

# 测试生成海报
echo -e "\n\033[1;34m测试生成海报并上传...\033[0m"
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "Recruiter": "Test User",
    "Number": "12,500",
    "Team": "Engineering",
    "RecordID": "OcrAroeKgeQEm5cEqmLlTfUOgGc"
  }' \
  ${API_URL}/api/generate-poster | python -m json.tool

echo -e "\n\033[1;32m测试完成!\033[0m" 