# IPL Cricket Analytics Dashboard 🏏

## Project Overview
IPL Cricket Analytics is a data analytics and visualization project developed using Python. It analyzes Indian Premier League historical data and presents insights through an interactive Streamlit dashboard.

## Features
- Tournament overview and key statistics
- Team-wise performance analysis
- Batting statistics and top batsmen
- Bowling statistics and top bowlers
- IPL match records
- Season and team filters
- Interactive data visualizations

## Technologies Used
- Python
- Pandas
- NumPy
- Streamlit
- Plotly
- PyYAML
- PyArrow

## Project Structure
```text
IPL_Cricket_Analytics/
├── backend/
├── dataset/
│   ├── ipl/
│   └── processed/
├── frontend/
│   ├── app.py
│   └── styles.py
├── reports/
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/sahil77454/IPL_Cricket_Analytics.git
```

2. Enter the project directory:

```bash
cd IPL_Cricket_Analytics
```

3. Create a virtual environment:

```bash
python -m venv venv
```

4. Activate it on Windows:

```bash
venv\Scripts\activate
```

5. Install dependencies:

```bash
pip install -r requirements.txt
```

6. Run the dashboard:

```bash
python -m streamlit run frontend/app.py
```

## Dashboard Modules
1. Overview
2. Team Analysis
3. Batting Analysis
4. Bowling Analysis
5. Match Records

## Author
**Sahil Narkar**

GitHub: https://github.com/sahil77454

## Purpose
Developed as an educational Data Analytics and Visualization project.