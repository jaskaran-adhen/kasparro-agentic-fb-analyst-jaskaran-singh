# kasparro-agentic-fb-analyst-jaskaran-singh

Kasparro Agentic Facebook Ads Analyst

A multi-agent AI system that autonomously diagnoses Facebook Ads
performance, identifies ROAS fluctuations, and generates data-driven
creative recommendations.

🚀 Quick Start

1. Install Dependencies

    pip install -r requirements.txt

2. Add Your Dataset

Place your Facebook Ads CSV file in the project directory.

File Name: synthetic_fb_ads_undergarments.csv

Required Columns: - campaign_name - date - spend - roas - ctr -
purchases - revenue - creative_message

3. Run Analysis

    python run.py "Analyze ROAS drop and suggest improvements"

📊 Sample Output

Console Output:

    🚀 Facebook Ads Analysis Starting...
    📋 Planner: Breaking down your query...
    📊 Data: Loading your dataset...
    📈 Data: Finding ROAS trends...
    💡 Insight: Generating hypotheses...
    🔬 Evaluator: Validating theories...
    🎨 Creative: Creating new ad ideas...
    ✅ ANALYSIS COMPLETED!

Generated Files: - insights.json — Analysis results with confidence
scores - creatives.json — Creative recommendations for campaigns -
report.md — Complete summary report

🛠️ System Architecture

The system uses 5 specialized AI agents: 1. Planner Agent – Breaks down
analysis tasks 2. Data Agent – Loads and validates dataset 3. Insight
Agent – Generates performance hypotheses 4. Evaluator Agent – Validates
insights with confidence scoring 5. Creative Agent – Creates data-driven
ad ideas

📁 Project Structure

    ├── run.py
    ├── requirements.txt
    ├── config/
    │   └── config.yaml
    ├── data/
    ├── reports/
    └── logs/

🎯 Features

-   ROAS Trend Analysis
-   Hypothesis Testing with confidence scores
-   Creative Optimization
-   Structured Outputs (JSON + Markdown)
-   Fully Autonomous multi-agent workflow

❓ Troubleshooting

File Not Found? - Ensure synthetic_fb_ads_undergarments.csv exists and
contains required columns

Module Errors? - Run pip install -r requirements.txt - Use Python 3.8+

📋 Requirements

-   Python 3.8+
-   pandas
-   PyYAML

▶️ Start analyzing Facebook ads

    python run.py "Analyze ROAS drop"
