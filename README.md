# LinkedIn Post Auto Editor

A powerful API service that generates customized LinkedIn offer announcement posters, with options to upload to AWS S3 and integrate with Lark (Feishu) tables.

## 🌟 Features

- Generate professional offer announcement posters with customizable fields
- Direct image generation in multiple formats (binary, base64)
- AWS S3 integration for image storage
- Lark (Feishu) table integration for automated updates
- Docker support for easy deployment
- RESTful API with comprehensive documentation

## 📋 API Endpoints

### Root Endpoint
- `GET /`: Returns API information and available endpoints

### Poster Generation
- `POST /api/generate-poster`: Generate poster, upload to S3, and optionally update Lark table
- `POST /api/generate-poster-direct`: Generate poster and return Base64 image data
- `POST /api/generate-poster-binary`: Generate poster and return binary image stream

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- AWS account (for S3 storage)
- Lark (Feishu) account (for table integration)
- Docker (optional, for containerized deployment)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/post_generator.git
   cd post_generator
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

5. Edit the `.env` file with your credentials:
   ```
   # AWS S3 configuration
   AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_ID
   AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY
   S3_BUCKET=your_bucket_name

   # Lark (Feishu) API configuration
   LARK_APP_ID=your_lark_app_id
   LARK_APP_SECRET=your_lark_app_secret

   # Lark (Feishu) table configuration
   LARK_APP_TOKEN=your_lark_app_token
   LARK_TABLE_ID=your_lark_table_id
   LARK_FIELD_NAME=Post_Url

   # MongoDB configuration
   MONGODB_URI=mongodb+srv://username:password@your-cluster.mongodb.net/?retryWrites=true&w=majority
   MONGODB_DB=your_db_name
   MONGODB_COLLECTION=your_collection_name

   # Application configuration
   DEBUG=True
   PORT=5001

   # Security configuration
   SECRET_KEY=your-secret-key-here
   ```

## 🏃‍♂️ Running the Application

### Run Locally

```bash
python app_lark.py
```

The API will be available at http://localhost:5001

### Docker Deployment

For Docker deployment, please refer to [DOCKER_GUIDE.md](DOCKER_GUIDE.md).

## 📝 API Usage Examples

### Generate Poster and Upload to S3

```bash
curl -X POST http://localhost:5001/api/generate-poster \
  -H "Content-Type: application/json" \
  -d '{
    "Recruiter": "John Smith",
    "Number": "12,500",
    "Team": "Engineering",
    "RecordID": "rec7s8gha1",
    "lark_update": true
  }'
```

Response:
```json
{
  "success": true,
  "poster_url": "https://yourpbucket.s3.amazonaws.com/output_John_Smith_12500_Engineering.png",
  "message": "Poster has been generated, uploaded, and Lark table has been updated",
  "lark_update": true
}
```

### Generate Poster with Multiple Teams

```bash
curl -X POST http://localhost:5001/api/generate-poster \
  -H "Content-Type: application/json" \
  -d '{
    "Recruiter": "Jane Doe",
    "Number": "15,000",
    "Team": "Engineering; Product Development"
  }'
```

### Get Direct Base64 Image

```bash
curl -X POST http://localhost:5001/api/generate-poster-direct \
  -H "Content-Type: application/json" \
  -d '{
    "Recruiter": "Alice Johnson",
    "Number": "20,000",
    "Team": "Data Science"
  }'
```

### Get Binary Image Stream

```bash
curl -X POST http://localhost:5001/api/generate-poster-binary \
  -H "Content-Type: application/json" \
  -d '{
    "Recruiter": "Bob Williams",
    "Number": "18,750",
    "Team": "DevOps"
  }' \
  --output offer_poster.png
```

## 📁 Project Structure

```
post_generator/
├── app_lark.py              # Main Flask application
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
├── assets/                  # Static assets
│   ├── images/              # Image assets
│   │   └── offer_banner.png # Poster background image
│   └── fonds/               # Font files
│       └── impact.ttf       # Font file
├── services/                # Service modules
│   └── image_generator.py   # Image generation service
├── utils/                   # Utility functions
│   ├── lark_function.py     # Lark API integration
│   ├── s3upload.py          # AWS S3 upload utilities
│   └── format_utils.py      # Formatting utilities
└── generated_images/        # Directory for generated images
```

## 🔐 Security Considerations

- Never commit sensitive information like API keys to version control
- Use environment variables for all sensitive configuration
- Rotate credentials regularly
- Consider implementing rate limiting for API endpoints

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request