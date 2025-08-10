#!/bin/bash

# Deployment script for Bangalore Home Price Prediction
echo "🚀 Deploying Bangalore Home Price Prediction..."

# Check if git remote exists
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "❌ Please add GitHub remote first:"
    echo "git remote add origin https://github.com/YOUR_USERNAME/bangalore-home-price-prediction.git"
    exit 1
fi

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push -u origin main

# Check if Heroku CLI is installed
if command -v heroku &> /dev/null; then
    echo "🎯 Heroku CLI found. Setting up Heroku deployment..."
    
    # Create Heroku app if it doesn't exist
    if ! heroku apps:info bangalore-home-price-prediction &> /dev/null; then
        echo "📱 Creating Heroku app..."
        heroku create bangalore-home-price-prediction
    fi
    
    # Set environment variables
    echo "⚙️ Setting environment variables..."
    heroku config:set DEBUG=False
    heroku config:set SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    
    # Deploy to Heroku
    echo "🚀 Deploying to Heroku..."
    git push heroku main
    
    # Run migrations
    echo "🗄️ Running migrations..."
    heroku run python manage.py migrate
    
    echo "✅ Deployment complete!"
    echo "🌐 Your app is live at: https://bangalore-home-price-prediction.herokuapp.com"
else
    echo "⚠️ Heroku CLI not found. Please install it from:"
    echo "https://devcenter.heroku.com/articles/heroku-cli"
    echo "Or use Railway/Render for deployment."
fi
