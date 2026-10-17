# 🚀 Market Intelligence Pro

## AI-Powered Competitor Analysis & Market Gap Detection

An end-to-end Python web application that helps product teams evaluate competing mobile apps from Google Play Store, analyze customer feedback, and identify market gaps before product development.

## 📋 Project Overview

This tool automates competitor research by:
- Searching Google Play Store dynamically
- Scraping and analyzing customer reviews
- Performing sentiment analysis
- Generating AI-powered market gap insights
- Exporting comprehensive reports

## ✨ Features

### 1. Dynamic App Discovery
- Search by keyword in **English or Arabic**
- Automatic translation of Arabic keywords
- Returns app title, developer, rating, and icon

### 2. Multi-App Selection & Scraping
- Select 2-4 competing apps
- Scrape 200 recent reviews per app
- Safe and reliable scraping without memory issues

### 3. Data Pipeline & Storage
- Clean and normalize feedback text
- Extract timestamps and categorize sentiments (Positive/Neutral/Negative)
- Store in SQLite database (`competitor_intelligence.db`)
- Generate multi-sheet Excel report (`competitor_report.xlsx`)

### 4. AI-Powered Market Gap Analysis
- Feed 1-star and 2-star pain points to Google Gemini API
- Output executive-level summary:
  - 🔴 Top recurring bugs/complaints
  - 🟡 Missing features users want
  - 🟢 Strategic recommendations

### 5. Interactive Dashboard
- Built with Streamlit
- Plotly interactive charts
- Intuitive UI for non-technical stakeholders

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit** - Web dashboard
- **google-play-scraper** - App data scraping
- **pandas** - Data processing
- **TextBlob** - Sentiment analysis
- **SQLite3** - Database storage
- **Plotly** - Interactive visualizations
- **Google Gemini API** - AI analysis

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/nawal200/market-intelligence-tool.git
cd market-intelligence-tool

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt