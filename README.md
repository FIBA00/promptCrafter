# PromptCrafter

<p align="center">
  <img width="200" height="200" src="https://via.placeholder.com/200x200?text=PromptCrafter" alt="PromptCrafter Logo">
</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org/)
[![Flask: 2.3.3](https://img.shields.io/badge/Flask-2.3.3-red.svg)](https://flask.palletsprojects.com/)

PromptCrafter is a web application that helps users create effective AI prompts with structured templates. It's designed for developers, content creators, and AI enthusiasts who want to get better results from their AI interactions.

## 🎯 Features

- **Structured Prompt Generation**: Create well-organized prompts following best practices
- **Personalized Templates**: Generate prompts with role, task, constraints, output style, and personality
- **Advanced Templates**: Pre-filled specialized templates for common technical scenarios
- **User Accounts**: Save, organize, edit, and share your favorite prompts
- **Public Prompt Library**: Explore prompts shared by the community with search, filtering and pagination
- **Tagging System**: Organize and discover prompts with a flexible tagging system
- **Profile Management**: Update user profile and customize account settings
- **Rate Limiting**: API rate limiting to prevent abuse
- **Responsive Design**: Modern UI that works well on all devices

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- pip (Python package installer)
- Git
- Redis (optional, for caching and rate limiting)
- PostgreSQL (recommended for production) or SQLite

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/FIBA00/promptCrafter.git
   cd promptCrafter
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (copy from example):
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Initialize the database:
   ```bash
   flask db upgrade
   ```

6. Run the development server:
   ```bash
   flask run
   ```

7. Open your browser and go to http://localhost:5000

### Docker Deployment

1. Make sure Docker and Docker Compose are installed
2. Run:
   ```bash
   docker-compose up -d
   ```
3. Visit http://localhost to see the application

## 🏗️ Project Structure

```
promptCrafter/
├── app.py                 # Application factory
├── config.py              # Configuration settings
├── models.py              # Database models
├── utils.py               # Utility functions
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose services
├── gunicorn_config.py     # Gunicorn server configuration
├── routes/                # Route blueprints
│   ├── __init__.py
│   ├── auth.py            # Authentication routes
│   ├── main.py            # Main routes
│   ├── prompts.py         # Prompt management routes
│   └── api.py             # API endpoints
├── migrations/            # Database migrations
├── tests/                 # Unit tests
├── nginx/                 # Nginx configuration
│   └── nginx.conf
├── static/                # Static assets
│   ├── css/
│   └── js/
└── templates/             # HTML templates
    ├── index.html
    ├── result.html
    ├── login.html
    ├── register.html
    ├── profile.html
    ├── edit_prompt.html
    ├── advanced_templates.html
    └── ...
```

## 🔌 API Documentation

PromptCrafter provides a RESTful API that allows you to generate prompts programmatically.

### Generate Prompt

**Endpoint**: `/api/generate`

**Method**: POST

**Request Body**:
```json
{
  "role": "AI architect",
  "task": "design a prediction engine",
  "constraints": "Must support multithreading",
  "output": "step-by-step",
  "personality": "nerdy but strategic"
}
```

**Response**:
```json
{
  "structured_prompt": "...",
  "natural_prompt": "..."
}
```

### Get Public Prompts

**Endpoint**: `/api/prompts`

**Method**: GET

**Query Parameters**:
- `search` (optional): Search string
- `tag` (optional): Filter by tag
- `sort` (optional): "newest" or "oldest"
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Results per page (default: 10, max: 50)

**Response**:
```json
{
  "prompts": [...],
  "page": 1,
  "per_page": 10,
  "total": 42,
  "pages": 5
}
```

## 🧪 Testing

Run the test suite with:

```bash
python -m unittest discover -s tests
```

## 🛠️ Tech Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login, Flask-WTF
- **Database**: SQLite (development), PostgreSQL (production)
- **Security**: CSRF protection, rate limiting, secure cookies
- **Caching**: Redis with Flask-Caching
- **Email**: Flask-Mail for notifications
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Deployment**: Docker, Gunicorn, Nginx

## 📊 Roadmap

- [ ] AI-assisted prompt improvement suggestions
- [ ] Export prompts to various formats (PDF, Markdown)
- [ ] Prompt collections/folders
- [ ] OAuth login options (GitHub, Google)
- [ ] Mobile app

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📬 Contact

Fraol D. - [@FIBA00](https://github.com/FIBA00)

Project Link: [https://github.com/FIBA00/promptCrafter](https://github.com/FIBA00/promptCrafter)
