Name: Manimoy Karmakar
Roll number:AIML-A6/May-10007

Problem Statement:

Covid-19 data analyzer:Real-time analysis of vaccination rates, cases by region

Solution:
Using Pandas,Plotly,APIs I’ve planned to approach this problem.

1. Brief(Overview): 

 A real-time data analysis tool for tracking COVID-19 vaccination rates and case statistics by region, powered by Python, Pandas, Plotly, and public health APIs. 

2. Features:

01. Real-time COVID-19 case data fetched via public APIs
02. Vaccination rate tracking by country and region
03. Interactive visualizations (line charts, bar charts, choropleth maps)
04. Regional comparison dashboards
05. Daily/weekly trend analysis
06. xportable reports and chart snapshots

3.  Tech Stack:

 Tool         | Purpose                             |
|------------|--------------------------------------|
| Python 3.9+| Core language                        |
| Pandas     | Data wrangling and analysis          |
| Plotly     | Interactive charts and dashboards    |
| Requests   | API data fetching                    |
| disease.sh |Free COVID-19 REST API (no key needed)|
| NumPy      |  Numerical computations              |
|------------|--------------------------------------|



4. Project Structure:

covid19-data-analyzer/
│
├── main.py                  # Entry point
├── fetcher.py               # API data fetching logic
├── analyzer.py              # Pandas-based analysis functions
├── visualizer.py            # Plotly chart builders
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
└── output/
    └── charts/              # Saved chart HTML files

5. Installations

git clone https://github.com/yourusername/COVID-19-Data-Analyzer.git

cd COVID-19-Data-Analyzer

Dependencies:
pip install pandas plotly requests

Usage

Run the analyzer:

python covid_analyzer.py

The program will:

   01. Fetch the latest COVID-19 data.
   02. Display key statistics.
   03. Generate interactive visualizations.

6. License
    MIT License. See [LICENSE](LICENSE) for details.

7.  Future Improvements

    01.  Add a Streamlit/Dash web dashboard
    02.  Support state/province-level data
    03.  Integrate WHO and CDC datasets
    04.  Add automated daily email reports
    05.  Docker containerization


8. Acknowledgements

    01.  [disease.sh](https://disease.sh/) for the free COVID-19 API
    02.  [Plotly](https://plotly.com/python/) for visualization
    03. [Pandas](https://pandas.pydata.org/) for data analysis



















