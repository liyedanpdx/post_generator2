# Docker 部署指南

本文档提供了如何使用 Docker 部署 LinkedIn Post Auto Editor 应用的说明。

## 前提条件

- 安装 [Docker](https://www.docker.com/get-started)
- 安装 [Docker Compose](https://docs.docker.com/compose/install/) (可选，但推荐)

## 目录结构准备

确保你的 `post_generator` 目录中有以下文件和目录：

```
post_generator/
├── app.py                  # Flask应用主文件
├── requirements.txt        # Python依赖
├── Dockerfile              # Docker构建文件
├── docker-compose.yml      # Docker Compose配置文件
├── assets/                 # 静态资源
│   ├── images/             # 图片资源
│   │   └── offer_banner.png # 海报背景图片
│   └── fonds/              # 字体文件
│       └── impact.ttf      # 字体文件
├── services/               # 服务模块
├── templates/              # HTML模板
└── utils/                  # 工具函数
```

## 使用 Docker Compose 部署（推荐）

1. 打开命令行，进入 `post_generator` 目录：

   ```bash
   cd path/to/post_generator
   ```

2. 构建并启动容器：

   ```bash
   docker-compose up -d
   ```

   这将在后台启动应用。

3. 查看日志：

   ```bash
   docker-compose logs -f
   ```

4. 停止应用：

   ```bash
   docker-compose down
   ```

## 使用 Docker 命令部署

如果你不想使用 Docker Compose，也可以直接使用 Docker 命令：

1. 构建镜像：

   ```bash
   docker build -t linkedin-post-editor .
   ```

2. 运行容器：

   ```bash
   docker run -d -p 5001:5000 \
     -v $(pwd)/assets:/app/assets \
     -v $(pwd)/generated_images:/app/generated_images \
     --name linkedin-post-editor \
     linkedin-post-editor
   ```

   在 Windows 命令行中，使用：

   ```bash
   docker run -d -p 5001:5000 -v %cd%/assets:/app/assets -v %cd%/generated_images:/app/generated_images --name linkedin-post-editor linkedin-post-editor
   ```

   在 PowerShell 中，使用：

   ```powershell
   docker run -d -p 5001:5000 -v ${PWD}/assets:/app/assets -v ${PWD}/generated_images:/app/generated_images --name linkedin-post-editor linkedin-post-editor
   ```

3. 查看日志：

   ```bash
   docker logs -f linkedin-post-editor
   ```

4. 停止并删除容器：

   ```bash
   docker stop linkedin-post-editor
   docker rm linkedin-post-editor
   ```

## 访问应用

应用启动后，可以通过以下URL访问：

- API文档：http://localhost:5001
- 海报生成表单：http://localhost:5001/form

## 使用 API

### 生成海报

```bash
curl -X POST http://localhost:5001/api/generate-poster \
  -H "Content-Type: application/json" \
  -d '{"recipient_name": "张三", "offer_amount": "12,500", "team_name": "工程部"}' \
  --output poster.png
```

在 Windows 命令行中：

```bash
curl -X POST http://localhost:5001/api/generate-poster -H "Content-Type: application/json" -d "{\"recipient_name\": \"张三\", \"offer_amount\": \"12,500\", \"team_name\": \"工程部\"}" --output poster.png
```

### 获取汇率

```bash
curl http://localhost:5001/api/exchange-rates
```

## 注意事项

1. **文件自动删除**：生成的图片文件会在下载后60秒自动删除，以节省空间。

2. **持久化存储**：如果你需要长期保存生成的图片，可以修改 `app.py` 中的 `schedule_file_deletion` 函数调用，增加延迟时间或完全移除该调用。

3. **资源文件**：确保 `assets` 目录中有必要的图片和字体文件。如果没有，应用会尝试查找替代文件，但可能会影响生成的海报质量。 