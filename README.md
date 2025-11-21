# 🛡️ Real-Time Fraud Detection System

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Kafka](https://img.shields.io/badge/Apache_Kafka-Streaming-black)
![FastAPI](https://img.shields.io/badge/FastAPI-Serving-green)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![Docker](https://img.shields.io/badge/Docker-Containerization-blue)

A full-stack, real-time machine learning pipeline that detects fraudulent financial transactions in milliseconds. This project ingests a high-throughput stream of transactions, processes them via **Apache Kafka**, scores them using a **LightGBM** model deployed with **FastAPI**, and visualizes the results on a live **Streamlit** dashboard.

![Dashboard Screenshot]<img width="1512" height="982" alt="Screenshot 2025-11-20 at 10 43 17 PM" src="https://github.com/user-attachments/assets/2f768b4e-aa2c-44b9-862e-c2c3f3a1d2fc" />


---

## 🚀 Key Features

- **Real-Time Streaming:** Simulates 20M+ transaction volume using a custom Producer and Apache Kafka.  
- **Low-Latency Inference:** Deployed LightGBM model via FastAPI (REST) with sub-50ms response times.  
- **Imbalanced Data Handling:** Trained on the PaySim dataset (0.2% fraud rate) using dynamic class weighting to achieve **99% Recall**.  
- **Live Dashboard:** Interactive Streamlit interface to monitor transaction traffic, flagged fraud, and estimated saved revenue.  
- **Containerized Infrastructure:** Uses Docker Compose to orchestrate Kafka services without manual setup.  

---

## 🏗️ Architecture

The system follows a decoupled microservices architecture:

1. **Producer:** Generates synthetic financial transactions and pushes them to the `financial_transactions` Kafka topic.  
2. **Kafka Broker:** Central messaging backbone for real-time streaming.  
3. **Inference Service (FastAPI):** Serves a trained LightGBM model for ultra-fast predictions.  
4. **Detector / Consumer:** Listens to Kafka, sends data to the API, logs alerts.  
5. **Dashboard:** Monitors stream activity and fraud alerts in real time.  


![Architecture](https://github.com/user-attachments/assets/648a9446-102a-4700-9401-274d1b02d911)


---

## 🛠️ Tech Stack

- **Language:** Python 3.12  
- **ML Model:** LightGBM (Gradient Boosting)  
- **Streaming:** Apache Kafka (KRaft mode)  
- **API Framework:** FastAPI + Uvicorn  
- **Visualization:** Streamlit + Altair  
- **Containerization:** Docker & Docker Compose  

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- Docker Desktop installed and running.  
- Python 3.9+  

### 2. Clone the Repo
```bash
git clone https://github.com/MananxRobin/fraud-detection-system.git
cd fraud-detection-system
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
> Use `confluent-kafka` instead of `kafka-python` for Python 3.12.

### 4. Start Infrastructure (Kafka)
```bash
docker-compose up -d
```

*Wait ~30 seconds for Kafka to initialize.*

---

## 🏃‍♂️ How to Run (The “Control Room”)

Open **4 terminals**:

### **Terminal 1 — Start FastAPI (Inference Service)**
```bash
python app.py
```

### **Terminal 2 — Start Streamlit Dashboard**
```bash
streamlit run dashboard.py
```

### **Terminal 3 — Start Fraud Detector**
```bash
python detector.py
```

### **Terminal 4 — Start Producer**
```bash
python producer.py
```

Then open **http://localhost:8501** to view your live dashboard.

---

## 📊 Model Performance

| Metric | Score | Notes |
|-------|-------|-------|
| **Accuracy** | 99.8% | High due to class imbalance |
| **Recall (Fraud)** | **99%** | Most important metric |
| **Precision** | ~11% | Acceptable false positives for safety |

---

## 📂 Project Structure

```
├── docker-compose.yml                            # Kafka infrastructure
├── requirements.txt                              # Python dependencies
├── README.md                                     # Documentation
├── app.py                                        # FastAPI inference service
├── dashboard.py                                  # Streamlit dashboard
├── detector.py                                   # Kafka consumer logic
├── producer.py                                   # Data stream simulator
├── train_model.py                                # Training & feature engineering
└── fraud_model.pkl                               # Saved LightGBM model

```

---

## 🔮 Future Improvements

- **Database Integration (PostgreSQL)** for audit trails  
- **Feature Store (Redis)** for velocity-based real-time features  
- **Cloud Deployment** using AWS ECS or Kubernetes  

---

**Author:** Manan Ambaliya
**License:** MIT
