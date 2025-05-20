# Curl 命令示例

以下是一些使用 curl 命令测试 API 的示例。

## Windows 命令行

### 1. 获取所有汇率信息

```
curl http://localhost:5000/api/exchange-rates
```

### 2. 获取特定货币的汇率（例如人民币CNY）

```
curl http://localhost:5000/api/exchange-rate/CNY
```

### 3. 生成海报并保存为poster.png

```
curl -X POST http://localhost:5000/api/generate-poster ^
  -H "Content-Type: application/json" ^
  -d "{\"recipient_name\": \"张三\", \"offer_amount\": \"12,500\", \"team_name\": \"工程部\"}" ^
  --output poster.png
```

### 4. 清理旧文件（超过48小时的文件）

```
curl -X POST http://localhost:5000/api/cleanup ^
  -H "Content-Type: application/json" ^
  -d "{\"max_age_hours\": 48}"
```

## PowerShell

### 1. 获取所有汇率信息

```powershell
Invoke-WebRequest -Method GET -Uri "http://localhost:5000/api/exchange-rates" | Select-Object -ExpandProperty Content
```

### 2. 获取特定货币的汇率（例如人民币CNY）

```powershell
Invoke-WebRequest -Method GET -Uri "http://localhost:5000/api/exchange-rate/CNY" | Select-Object -ExpandProperty Content
```

### 3. 生成海报并保存为poster.png

```powershell
Invoke-WebRequest -Method POST -Uri "http://localhost:5000/api/generate-poster" -Headers @{"Content-Type"="application/json"} -Body '{"recipient_name": "张三", "offer_amount": "12,500", "team_name": "工程部"}' -OutFile poster.png
```

### 4. 清理旧文件（超过48小时的文件）

```powershell
Invoke-WebRequest -Method POST -Uri "http://localhost:5000/api/cleanup" -Headers @{"Content-Type"="application/json"} -Body '{"max_age_hours": 48}'
```

## Linux/Mac 终端

### 1. 获取所有汇率信息

```bash
curl http://localhost:5000/api/exchange-rates
```

### 2. 获取特定货币的汇率（例如人民币CNY）

```bash
curl http://localhost:5000/api/exchange-rate/CNY
```

### 3. 生成海报并保存为poster.png

```bash
curl -X POST http://localhost:5000/api/generate-poster \
  -H "Content-Type: application/json" \
  -d '{"recipient_name": "张三", "offer_amount": "12,500", "team_name": "工程部"}' \
  --output poster.png
```

### 4. 清理旧文件（超过48小时的文件）

```bash
curl -X POST http://localhost:5000/api/cleanup \
  -H "Content-Type: application/json" \
  -d '{"max_age_hours": 48}'
```

## 注意事项

1. 确保 API 服务器已经启动并在 http://localhost:5000 上运行
2. 如果服务器运行在其他地址或端口，请相应地修改 URL
3. 在 Windows 命令行中，使用 `^` 作为续行符，并使用 `\"` 转义 JSON 中的双引号
4. 在 PowerShell 和 Linux/Mac 终端中，可以使用单引号包围 JSON 数据，避免转义问题 