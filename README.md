# Python Beginner Project

## Overview
This is a simple Python project designed for beginners to learn the basics of Python programming, including functions, web routing, and marketplace API integration.

## Project Structure
```
python-beginner-project
├── src
│   ├── main.py
│   ├── market_api.py
│   └── templates
│       ├── index.html
│       └── results.html
├── tests
│   ├── test_main.py
│   └── test_market_api.py
├── requirements.txt
├── README.md
└── .env.example
```

## Setup Instructions
1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Copy `.env.example` to `.env` and add your API credentials.
4. Install dependencies:
   ```
pip install -r requirements.txt
```

## Usage
1. Run the website:
   ```
python src/main.py
```
2. Open `http://127.0.0.1:5000` in your browser.

### Fortnite progress dashboard
1. Copy `.env.example` to `.env` and add your credentials.
2. Run the Fortnite dashboard:
   ```
python src/fortnite_app.py
```
3. Open `http://127.0.0.1:5000/fortnite` in your browser.

If you do not have a Fortnite API key, the app still shows sample progress so the dashboard works while you configure a provider.
 
### GitHub Pages (static preview)

This repository includes a static preview of the Fortnite frontend in the `docs/` folder. The static preview runs entirely on GitHub Pages and shows sample progress data.

To publish the static preview on GitHub Pages:

1. In GitHub, open your repository's **Settings > Pages**.
2. Under "Source", choose the `master` branch and the `/docs` folder, then save.
3. The site will be available at `https://<your-github-username>.github.io/<repo-name>/` (or at your custom domain if configured).

To use a custom domain with GitHub Pages:

1. Replace the `docs/CNAME` file contents with your domain (for example `example.com`).
2. In your DNS provider, create a CNAME record for `www` pointing to `<your-github-username>.github.io`, and optionally create A records for the apex domain as described in GitHub Pages docs.

Note: The static preview does not include the Flask backend. For live Fortnite progress you must deploy the Flask app to a server (Render, Railway, Fly, etc.) and point the frontend to that API.
## API configuration
This app needs credentials for eBay and TCGplayer:
- `EBAY_CLIENT_ID`
- `EBAY_CLIENT_SECRET`
- `TCGPLAYER_CLIENT_ID`
- `TCGPLAYER_CLIENT_SECRET`
- `FORTNITE_API_KEY` (optional for live Fortnite progress)
- `FLASK_SECRET_KEY` (recommended for session security)

You can optionally add `EBAY_OAUTH_TOKEN` for a pre-generated eBay token.

## Running Tests
To run the unit tests, use:
```
python -m unittest discover -s tests
```

## Contributing
Feel free to contribute to this project by submitting issues or pull requests.
