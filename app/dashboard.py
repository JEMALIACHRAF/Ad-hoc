from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import requests
import io
import base64

# Initialize Dash App
app = Dash(__name__)

# Backend Base URL
BASE_URL = "http://127.0.0.1:8000/api"

# Layout of the Dashboard
app.layout = html.Div(
    [
        html.H1(
            "Telco Customer Churn Dashboard",
            style={
                "text-align": "center",
                "background-color": "#007BFF",
                "color": "white",
                "padding": "10px",
            },
        ),
        # KPI Section
        html.Div(
            [
                html.Div(
                    [
                        html.H3("Total Customers", style={"text-align": "center"}),
                        html.Div(
                            id="total-customers",
                            style={
                                "text-align": "center",
                                "font-size": "30px",
                                "font-weight": "bold",
                                "color": "#007BFF",
                            },
                        ),
                    ],
                    style={
                        "width": "30%",
                        "display": "inline-block",
                        "padding": "20px",
                        "border": "2px solid #007BFF",
                        "border-radius": "10px",
                        "margin": "10px",
                        "background-color": "#E8F4FF",
                    },
                ),
                html.Div(
                    [
                        html.H3("Average Monthly Charges", style={"text-align": "center"}),
                        html.Div(
                            id="average-monthly-charges",
                            style={
                                "text-align": "center",
                                "font-size": "30px",
                                "font-weight": "bold",
                                "color": "#28A745",
                            },
                        ),
                    ],
                    style={
                        "width": "30%",
                        "display": "inline-block",
                        "padding": "20px",
                        "border": "2px solid #28A745",
                        "border-radius": "10px",
                        "margin": "10px",
                        "background-color": "#E8F5E9",
                    },
                ),
                html.Div(
                    [
                        html.H3("Churn Rate", style={"text-align": "center"}),
                        html.Div(
                            id="churn-rate",
                            style={
                                "text-align": "center",
                                "font-size": "30px",
                                "font-weight": "bold",
                                "color": "#DC3545",
                            },
                        ),
                    ],
                    style={
                        "width": "30%",
                        "display": "inline-block",
                        "padding": "20px",
                        "border": "2px solid #DC3545",
                        "border-radius": "10px",
                        "margin": "10px",
                        "background-color": "#FDECEA",
                    },
                ),
            ],
            style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
        ),
        # Charts Section
        html.Div(
            [
                html.Div([dcc.Graph(id="customer-segments-visualization")], style={"width": "48%", "display": "inline-block", "padding": "10px"}),
                html.Div([dcc.Graph(id="contract-visualization")], style={"width": "48%", "display": "inline-block", "padding": "10px"}),
                html.Div([dcc.Graph(id="tenure-visualization")], style={"width": "48%", "display": "inline-block", "padding": "10px"}),
                html.Div([dcc.Graph(id="payment-method-visualization")], style={"width": "48%", "display": "inline-block", "padding": "10px"}),
                html.Div([dcc.Graph(id="prediction-visualization")], style={"width": "48%", "display": "inline-block", "padding": "10px"}),
                html.Div([dcc.Graph(id="revenue-leakage-visualization")], style={"width": "48%", "display": "inline-block", "padding": "10px"}),
                html.Div([dcc.Graph(id="churn-heatmap-visualization")], style={"width": "48%", "display": "inline-block", "padding": "10px"}),
                html.Div([dcc.Graph(id="stacked-bar-visualization")], style={"width": "48%", "display": "inline-block", "padding": "10px"}),
                html.Div([dcc.Graph(id="cohort-analysis-visualization")], style={"width": "48%", "display": "inline-block", "padding": "10px"}),
            ],
            style={"margin-top": "20px"},
        ),
        # File Upload for Prediction
        html.Div(
            [
                html.H2("Upload Customer Data for Prediction", style={"text-align": "center"}),
                dcc.Upload(
                    id="upload-prediction-file",
                    children=html.Div(
                        ["Drag and Drop or ", html.A("Select File")],
                        style={
                            "text-align": "center",
                            "border": "2px dashed #007BFF",
                            "padding": "20px",
                            "cursor": "pointer",
                        },
                    ),
                    multiple=False,
                ),
            ],
            style={"margin-top": "20px"},
        ),
    ]
)

# Dashboard update callback
@app.callback(
    [
        Output("customer-segments-visualization", "figure"),
        Output("contract-visualization", "figure"),
        Output("tenure-visualization", "figure"),
        Output("payment-method-visualization", "figure"),
        Output("prediction-visualization", "figure"),  # Keep this output for prediction chart
        Output("total-customers", "children"),
        Output("average-monthly-charges", "children"),
        Output("churn-rate", "children"),
    ],
    [Input("upload-prediction-file", "contents")],
    [State("upload-prediction-file", "filename")],
)
def update_dashboard(uploaded_file_content, uploaded_file_name):
    # Initialize figures and KPI defaults
    total_customers, avg_charges, churn_rate = "N/A", "N/A", "N/A"
    segments_fig, contract_fig, tenure_fig, payment_methods_fig, prediction_fig = px.bar(), px.pie(), px.line(), px.bar(), px.pie()

    # Debugging: Check if file is uploaded
    if uploaded_file_content:
        try:
            # Decoding the uploaded file
            content_type, content_string = uploaded_file_content.split(",")
            decoded = base64.b64decode(content_string)

            # Save the uploaded file to a temporary location to pass to the backend
            file_path = "temp_file.csv"
            with open(file_path, "wb") as f:
                f.write(decoded)

            # Call the backend API for prediction
            prediction_response = requests.post(
                f"{BASE_URL}/ml/predict/file/",
                files={"file": open(file_path, "rb")},
            )

            if prediction_response.status_code == 200:
                # Successfully got the prediction response
                prediction_data = prediction_response.json()
                prediction_df = pd.DataFrame(prediction_data)

                # Create a pie chart for prediction results
                prediction_summary = prediction_df["RiskLevel"].value_counts().reset_index()
                prediction_summary.columns = ["RiskLevel", "Count"]
                prediction_fig = px.pie(
                    prediction_summary,
                    names="RiskLevel",
                    values="Count",
                    title="Churn Risk Level Distribution",
                    color="RiskLevel",
                    color_discrete_map={"High": "red", "Medium": "yellow", "Low": "green"},
                )
            else:
                # Handle error in prediction response
                prediction_fig = px.pie()
                print("Prediction failed: ", prediction_response.text)

        except Exception as e:
            print(f"Error uploading file or predicting: {e}")
            prediction_fig = px.pie()  # Empty pie chart on error

    # Fetching Customer Segment Data (Unchanged)
    try:
        segments_response = requests.get(f"{BASE_URL}/scores/aggregated/")
        if segments_response.status_code == 200:
            segments_data = segments_response.json()
            segments_df = pd.DataFrame(segments_data)
            if not segments_df.empty:
                segments_fig = px.bar(
                    segments_df,
                    x="segment",
                    y="average_monthly_charges",
                    title="Average Monthly Charges by Segment",
                    color="average_monthly_charges",
                    color_continuous_scale="Blues",
                )
                avg_charges = round(segments_df["average_monthly_charges"].mean(), 2)
                churn_rate = round(segments_df["average_churn_risk"].mean(), 2)
    except:
        pass

    # Fetching Contract Distribution Data (Unchanged)
    try:
        contracts_response = requests.get(f"{BASE_URL}/Telco/telco/summary/")
        if contracts_response.status_code == 200:
            contracts_data = contracts_response.json()
            contract_types = pd.DataFrame(contracts_data.get("contract_types", []))
            if not contract_types.empty:
                contract_fig = px.pie(
                    contract_types,
                    names="key",
                    values="doc_count",
                    title="Contract Type Distribution",
                    color_discrete_sequence=px.colors.sequential.Teal,
                )
                total_customers = contract_types["doc_count"].sum()
    except:
        pass

    # Fetching Tenure Distribution Data (Unchanged)
    try:
        tenure_response = requests.get(f"{BASE_URL}/Telco/telco/tenure-distribution/")
        if tenure_response.status_code == 200:
            tenure_data = tenure_response.json()
            tenure_df = pd.DataFrame(tenure_data)
            if not tenure_df.empty:
                tenure_fig = px.line(
                    tenure_df,
                    x="key",
                    y="doc_count",
                    title="Tenure Distribution",
                    markers=True,
                    line_shape="spline",
                    color_discrete_sequence=["#1F77B4"],
                )
    except:
        pass

    # Fetching Payment Methods Data (Unchanged)
    try:
        payment_response = requests.get(f"{BASE_URL}/Telco/telco/payment-methods/")
        if payment_response.status_code == 200:
            payment_methods_data = payment_response.json()
            payment_methods_df = pd.DataFrame(payment_methods_data)
            if not payment_methods_df.empty:
                payment_methods_fig = px.bar(
                    payment_methods_df,
                    x="key",
                    y="doc_count",
                    color="key",
                    title="Payment Methods by Count",
                    barmode="stack",
                )
    except:
        pass

    return (
        segments_fig,
        contract_fig,
        tenure_fig,
        payment_methods_fig,
        prediction_fig,  # Keep prediction visualization here
        total_customers,
        avg_charges,
        churn_rate,
    )

if __name__ == "__main__":
    app.run_server(debug=True)
