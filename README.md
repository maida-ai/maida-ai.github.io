# Maida AI Landing Page

A modern, responsive landing page for Maida AI built with Flask.

## Features

- Modern, clean design
- Responsive layout
- Smooth animations and transitions
- Mobile-friendly navigation
- Optimized performance

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the development server:
```bash
python app.py
```

2. Open your browser and navigate to `http://localhost:5000`

## Development

- `app.py` - Main Flask application
- `templates/` - HTML templates
- `static/` - Static files (CSS, JavaScript, images)
  - `css/` - Stylesheets
  - `js/` - JavaScript files
  - `images/` - Image assets

## Production Deployment

For production deployment, it's recommended to use Gunicorn:

```bash
gunicorn app:app
```

## License

Copyright © 2024 Maida AI. All rights reserved.
