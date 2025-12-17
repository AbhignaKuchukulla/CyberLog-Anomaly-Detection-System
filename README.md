# CyberLog Anomaly Detection System

CyberLog Anomaly Detection System is a beginner-friendly data science project that simulates a simplified SIEM-style analytics workflow for detecting anomalous user authentication activity using unsupervised machine learning.

The project focuses on building a clean data pipeline, extracting behavioral features from security logs, and generating interpretable anomaly insights.


## Problem Statement (SIEM Context)

Security Operations Centers (SOCs) monitor authentication events such as login attempts, success and failure outcomes, IP addresses, devices, and locations to detect suspicious behavior.

Common indicators of compromise include:
- Excessive failed login attempts
- Unusual access times
- Sudden spikes in activity
- Logins from new devices or IP addresses

This project analyzes authentication logs to identify potentially anomalous behavior using statistical analysis and unsupervised machine learning techniques.  
The focus is on analytics and explainability rather than real-time alerting.


## Data Description

- Synthetic authentication log data designed to resemble real-world SIEM event logs
- Columns:
  - user_id
  - timestamp
  - event_type (login)
  - status (success or failure)
  - ip_address
  - device
  - location

Injected anomaly patterns include:
- Excessive failed login attempts
- Logins during unusual hours
- Sudden spikes in login activity
- New or rarely used IP addresses and devices

Synthetic data is used to avoid privacy and confidentiality issues.


## Approach (Data Science Pipeline)

### Data Generation
Synthetic authentication logs are generated using Python and saved as:
- data/raw_logs.csv

### Preprocessing
Logs are cleaned by parsing timestamps, handling missing values, and removing duplicates.
- Output: data/processed_logs.csv

### Feature Engineering
Numerical features derived from behavior:
- Login frequency per user
- Failed login ratio
- Hour of day
- Unique IP count per user

### Anomaly Detection
- Features are normalized
- Isolation Forest is used to generate anomaly scores and labels

### Visualization
Plots are created to compare normal and anomalous behavior and saved in the visuals directory.


## Machine Learning Model Explanation

Unsupervised learning is used because security data rarely has labeled attacks.

Isolation Forest identifies anomalies by isolating observations that differ significantly from normal behavior.

Feature scaling ensures equal contribution from all features.

---

## Project Structure

CyberLog-Anomaly-Detection-System  
├── data  
├── notebooks  
├── src  
├── visuals  
├── README.md  
└── requirements.txt  


## How to Run

Install dependencies:
pip install -r requirements.txt

Run from project root:
python src/data_generator.py  
python src/preprocessing.py  
python src/anomaly_model.py  



## Key Learnings

- Understanding SIEM-style security analytics
- Building clean preprocessing pipelines
- Applying unsupervised ML to cybersecurity data
- Interpreting anomaly scores
- Writing readable, maintainable data science code
