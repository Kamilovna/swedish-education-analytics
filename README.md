# Swedish Education Analytics
## Overview
This project analyzes application results for Swedish Higher Vocational Education (Yrkeshögskolan) programs using official data from the Swedish National Agency for Higher Vocational Education (MYH).
The project combines education data with official demographic statistics from Statistics Sweden (SCB). Municipality and county codes are used to integrate datasets, while annual population statistics provide demographic context for the analysis. A GeoJSON file (`sweden_counties.json`) is used to visualize regional statistics on interactive maps.
The processed data is stored in an AWS PostgreSQL database and can be queried through a FastAPI application.
## Data Sources
The project uses data from the following official sources:
- **Myndigheten för Yrkeshögskolan (MYH)** – application results for Higher Vocational Education programs (2020–2025).
- **Statistics Sweden (SCB)** – municipality and county codes, as well as annual population statistics.
- **GeoJSON administrative boundaries** – `sweden_counties.json` for geographic visualization.
## Technologies
- Python 3.x
- FastAPI
- PostgreSQL (AWS RDS)
- SQLAlchemy
- Pandas
- Jupyter Notebook
- Git
- GitHub
## Project Structure
```text
.
├── data/
|   ├── processed                            # Cleaned dataset
│       ├── applications.csv                 # Processed application dataset
│       ├── municipalities.csv               # Municipality reference data
│       ├── counties.csv                     # County reference data
│       ├── population_2020-2025.csv         # Combined population dataset
|   ├── raw                                  # Original datasets (MYH & SCB)
│       ├── resultat-ansokningsomgang-2020.xlsx
│       ├── resultat-ansokningsomgang-2021.xlsx
│       ├── resultat-ansokningsomgang-2022.xlsx
│       ├── resultat-ansokningsomgang-2023.xlsx
│       ├── resultat-ansokningsomgang-2024.xlsx
│       ├── resultat-ansokningsomgang-2025.xlsx
│       ├── kommunlankod-2026.xlsx           # Municipality and county codes (SCB)
│       ├── population 2020-24.xlsx
│       ├── population 2025.xlsx
└── sweden_counties.json                     # GeoJSON for map visualizations
│
├── notebooks/
│   └── data_preparation.ipynb               # Data cleaning and transformation
│
├── applications.py                         # Streamlit page for applications statistics
├── education_capacity.py                   # Streamlit page for education capacity analysis
├── frontend.py                             # Main Streamlit application
├── schemas.py                              # Pydantyc schemas used by FastAPI
├── setup.py                                # Database inicialisation
├── main.py                                 # FastAPI application
└── README.md
```
## Geographic Data
The project uses `sweden_counties.json` (GeoJSON) to display county- and municipality-level statistics on interactive maps.
The geographic boundaries are linked with official SCB municipality and county codes, enabling spatial visualization of education capacity and application data.
## Data Preparation
Data preprocessing is documented in the Jupyter notebook:
`notebooks/data_preparation.ipygit addnb`
The notebook performs the following steps:
- imports raw Excel files;
- cleans and standardizes the datasets;
- merges annual MYH application results;
- integrates municipality and county codes from SCB;
- combines annual population statistics;
- exports processed CSV files for database import.
## Installation
Clone the repository:
```bash
git clone https://github.com/yourusername/swedish-education-analytics.git
cd swedish-education-analytics
```
Create a virtual environment:
```bash
python -m venv venv
```
Activate it:
Windows
```bash
source venv/Scripts/activate
```
Linux/macOS
```bash
source venv/bin/activate
```
Install dependencies:
```bash
pip install -r requirements.txt
```
## Environment Variables
Create a .env file with your database credentials:
```env
DB_HOST=...
DB_PORT=5432
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
```
## Database
The project uses an **AWS PostgreSQL database.**
Run
```bash
python setup.py
```
to create  the required tables
## Running the project
```bash
uvicorn main:app --reload
```