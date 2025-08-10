# Bangalore Home Price Prediction Web App

link ---> https://home-predictin-system-bangalore.onrender.com

A Django web application that serves a trained machine learning model to predict Bangalore house prices based on location, square footage, number of bedrooms (BHK), and bathrooms.

## 🌟 Features
- **Interactive Web Interface**: Bootstrap-powered form for easy input
- **Machine Learning Backend**: Pre-trained Linear Regression model with 225 features
- **Location Intelligence**: 222 Bangalore locations with one-hot encoding
- **Dual API Support**: JSON endpoint and HTML form submission
- **Production Ready**: Configured for Heroku deployment

## 🚀 Live Demo
- **Web Interface**: User-friendly form with location dropdown
- **API Endpoint**: `POST /predict/` with JSON payload
- **Model Info**: LinearRegression with ~225 coefficients trained on Bangalore housing data

## 🏗️ Project Structure
```
manage.py                # Django management commands
bangalore_home_price/    # Django project settings
predictor/              # Main application
  ├── views.py          # ML model integration & API endpoints
  ├── urls.py           # URL routing
  └── templates/        # Bootstrap HTML templates
artifacts/              # Model artifacts
  ├── bangalore_home_prices_model.pkl  # Trained scikit-learn model
  └── columns.json      # Feature names & location encoding
static/                 # CSS, JS, images
requirements.txt        # Python dependencies
Procfile               # Heroku deployment config
runtime.txt            # Python version specification
```

## 🛠️ Installation & Local Development

### Prerequisites
- Python 3.12+
- pip

### Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd bangalore-home-price-prediction

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to access the application.

## 📡 API Usage

### Predict House Price
```bash
curl -X POST http://127.0.0.1:8000/predict/ \
  -H "Content-Type: application/json" \
  -d '{
    "location": "whitefield",
    "sqft": 1200,
    "bath": 2,
    "bhk": 2
  }'
```

**Response:**
```json
{
  "estimated_price": 75.5
}
```

## 🚀 Deployment

### Heroku Deployment
1. **Create Heroku App**:
   ```bash
   heroku create your-app-name
   ```

2. **Set Environment Variables**:
   ```bash
   heroku config:set DEBUG=False
   heroku config:set SECRET_KEY=your-secret-key
   ```

3. **Deploy**:
   ```bash
   git push heroku main
   ```

4. **Run Migrations**:
   ```bash
   heroku run python manage.py migrate
   ```

### Other Platforms
- **Railway**: Connect GitHub repo, set environment variables
- **PythonAnywhere**: Upload files, configure WSGI
- **DigitalOcean App Platform**: Connect GitHub, configure build settings

## 🔧 Environment Variables
```bash
DEBUG=False                    # Set to False in production
SECRET_KEY=your-secret-key    # Generate a secure secret key
```

## 🧠 Model Details
- **Algorithm**: Linear Regression (scikit-learn)
- **Features**: 225 total (3 numeric + 222 location dummy variables)
- **Training Data**: Bangalore housing dataset
- **Input Features**:
  - `location`: Area name (categorical)
  - `total_sqft`: Square footage (numeric)
  - `bath`: Number of bathrooms (numeric)
  - `bhk`: Number of bedrooms (numeric)

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments
- Bangalore housing dataset
- Django & scikit-learn communities
- Bootstrap for UI components

## Expected Artifacts
- `artifacts/columns.json` should contain: `{ "data_columns": ["total_sqft", "bath", "bhk", "location1", "location2", ...] }`
- `artifacts/bangalore_home_prices_model.pkl` a pickle of the trained model that accepts the feature vector.

## Setup
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Visit: http://127.0.0.1:8000/

## API Usage
POST `/predict/` with JSON:
```json
{
  "location": "1st Phase JP Nagar",
  "sqft": 1000,
  "bhk": 2,
  "bath": 2
}
```
Response:
```json
{ "estimated_price_lakh": 75.42 }
```

## Notes
- Ensure the locations in the JSON match (case-insensitive) entries in `data_columns` after the first three base columns.
- For production, set `DEBUG=False` and configure `ALLOWED_HOSTS`.
