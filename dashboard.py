import streamlit as st
import pandas as pd
import json
import requests
import time
import altair as alt
from confluent_kafka import Consumer

# 1. Page Configuration
st.set_page_config(
    page_title="FraudGuard Live Monitor",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ Real-Time Fraud Detection System")
st.markdown("Monitoring financial transactions in **Kafka Stream**...")

# 2. Initialize Kafka Consumer
# distinct group_id ensures this consumer gets its own copy of messages
conf = {
    'bootstrap.servers': '127.0.0.1:9092',
    'group.id': 'dashboard-gui-group',
    'auto.offset.reset': 'latest'
}


@st.cache_resource
def get_consumer():
    c = Consumer(conf)
    c.subscribe(['financial_transactions'])
    return c


consumer = get_consumer()

# 3. Dashboard Layout Setup
# Top Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_total = st.empty()
with col2:
    metric_fraud = st.empty()
with col3:
    metric_legit = st.empty()
with col4:
    metric_saved = st.empty()

st.divider()

# Charts & Logs Row
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("💰 Transaction Volume (Live)")
    chart_placeholder = st.empty()

with c2:
    st.subheader("🚨 Recent Alerts")
    alert_placeholder = st.empty()

# 4. State Variables
if 'total_tx' not in st.session_state:
    st.session_state['total_tx'] = 0
if 'fraud_tx' not in st.session_state:
    st.session_state['fraud_tx'] = 0
if 'legit_tx' not in st.session_state:
    st.session_state['legit_tx'] = 0
if 'money_saved' not in st.session_state:
    st.session_state['money_saved'] = 0.0
if 'data' not in st.session_state:
    st.session_state['data'] = []

# 5. Main Real-Time Loop
try:
    # Create a container for the scrolling log
    log_container = st.container()

    while True:
        # Poll Kafka for messages (non-blocking, 0.5s wait)
        msg = consumer.poll(0.1)

        if msg is None:
            continue
        if msg.error():
            continue

        # Parse Data
        data = json.loads(msg.value().decode('utf-8'))

        # Call API for Prediction
        try:
            response = requests.post('http://localhost:8000/predict', json=data)
            if response.status_code == 200:
                pred = response.json()
                is_fraud = pred['is_fraud']
                prob = pred['fraud_probability']
            else:
                is_fraud = False
                prob = 0.0
        except:
            is_fraud = False
            prob = 0.0

        # Update Stats
        st.session_state['total_tx'] += 1
        if is_fraud:
            st.session_state['fraud_tx'] += 1
            st.session_state['money_saved'] += data['amount']

            # Add to Alert Log (Top of list)
            with alert_placeholder.container():
                st.error(f"FRAUD: {data['nameOrig']} | ${data['amount']:,.2f}")
        else:
            st.session_state['legit_tx'] += 1

        # Update Metrics
        metric_total.metric("Total Processed", st.session_state['total_tx'])
        metric_fraud.metric("Fraud Detected", st.session_state['fraud_tx'])
        metric_legit.metric("Legit Transactions", st.session_state['legit_tx'])
        metric_saved.metric("$$$ Saved", f"${st.session_state['money_saved']:,.2f}")

        # Update Chart Data
        st.session_state['data'].append({
            'id': st.session_state['total_tx'],
            'amount': data['amount'],
            'type': 'Fraud' if is_fraud else 'Legit'
        })

        # Keep chart clean (last 50 points)
        if len(st.session_state['data']) > 50:
            st.session_state['data'].pop(0)

        # Draw Chart
        df_chart = pd.DataFrame(st.session_state['data'])

        # Altair Chart for nice colors
        c = alt.Chart(df_chart).mark_circle(size=60).encode(
            x='id',
            y='amount',
            color=alt.Color('type', scale=alt.Scale(domain=['Legit', 'Fraud'], range=['green', 'red'])),
            tooltip=['amount', 'type']
        ).interactive()

        chart_placeholder.altair_chart(c, use_container_width=True)

        # Small sleep to prevent UI freezing
        time.sleep(0.05)

except KeyboardInterrupt:
    pass