# Resume AI Backend

A Django-based backend for Resume AI application that provides authentication, resume analysis, and AI-powered suggestions.

## Features

- JWT Authentication
- Resume Analysis with AI Integration
- Resume Suggestions
- API Documentation with Swagger/ReDoc
- CORS Support
- File Upload Support

## Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following variables:
```
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

- Authentication:
  - POST `/api/auth/token/` - Get JWT token
  - POST `/api/auth/token/refresh/` - Refresh JWT token

- Resume Analysis:
  - POST `/api/resume/analyze/` - Analyze resume
  - GET `/api/resume/suggestions/` - Get resume suggestions
  - GET `/api/resume/history/` - Get resume analysis history

## API Documentation

- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`

## Development

The project uses:
- Django REST Framework for API development
- JWT for authentication
- drf-yasg for API documentation
- django-cors-headers for CORS support

## License

This project is licensed under the MIT License. 