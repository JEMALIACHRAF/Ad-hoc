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
        # Ad-hoc Analysis
        html.Div(
            [
                html.H2("Ad-hoc Analysis", style={"text-align": "center"}),
                dcc.Dropdown(
                    id="adhoc-analysis-type",
                    options=[
                        {"label": "Revenue Leakage", "value": "revenue_leakage"},
                        {"label": "Cohort Analysis", "value": "cohort_analysis"},
                        {"label": "Stacked Bar Chart", "value": "stacked_bar"},
                    ],
                    placeholder="Select Analysis Type",
                ),
                dcc.Textarea(
                    id="adhoc-parameters",
                    placeholder='Additional Parameters (JSON): e.g., {"segment": "SeniorCitizen"}',
                    style={"width": "100%", "height": "100px"},
                ),
                html.Button("Run Analysis", id="run-adhoc-analysis", style={"margin-top": "10px"}),
                dcc.Graph(id="adhoc-analysis-visualization"),
            ],
            style={"margin-top": "20px", "padding": "10px", "border": "1px solid #CCC", "border-radius": "10px"},
        ),
        dcc.Interval(id="interval-component", interval=60000, n_intervals=0),
    ]
)

@app.callback(
    [
        Output("customer-segments-visualization", "figure"),
        Output("contract-visualization", "figure"),
        Output("tenure-visualization", "figure"),
        Output("payment-method-visualization", "figure"),
        Output("prediction-visualization", "figure"),
        Output("revenue-leakage-visualization", "figure"),
        Output("churn-heatmap-visualization", "figure"),
        Output("stacked-bar-visualization", "figure"),
        Output("cohort-analysis-visualization", "figure"),
        Output("adhoc-analysis-visualization", "figure"),
        Output("total-customers", "children"),
        Output("average-monthly-charges", "children"),
        Output("churn-rate", "children"),
    ],
    [Input("upload-prediction-file", "contents"), Input("run-adhoc-analysis", "n_clicks")],
    [State("upload-prediction-file", "filename"), State("adhoc-analysis-type", "value"), State("adhoc-parameters", "value")],
)
def update_dashboard(uploaded_file_content, n_clicks, uploaded_file_name, adhoc_analysis_type, adhoc_parameters):
    # Initialize figures and KPI defaults
    total_customers, avg_charges, churn_rate = "N/A", "N/A", "N/A"
    segments_fig, contract_fig, tenure_fig, payment_methods_fig, prediction_fig = px.bar(), px.pie(), px.line(), px.bar(), px.pie()
    revenue_leakage_fig, churn_heatmap_fig, stacked_bar_fig, cohort_fig, adhoc_fig = px.pie(), px.density_heatmap(), px.bar(), px.line(), px.bar()

    # Fetching Customer Segment Data
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

    # Fetching Contract Distribution Data
    try:
        contracts_response = requests.get(f"{BASE_URL}/netflix/telco/summary/")
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

    # Fetching Tenure Distribution Data
    try:
        tenure_response = requests.get(f"{BASE_URL}/netflix/telco/tenure-distribution/")
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

    # Fetching Payment Methods Data
    try:
        payment_response = requests.get(f"{BASE_URL}/netflix/telco/payment-methods/")
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

    # File Upload for Predictions
    if uploaded_file_content:
        try:
            content_type, content_string = uploaded_file_content.split(",")
            decoded = base64.b64decode(content_string)
            prediction_response = requests.post(
                f"{BASE_URL}/ml/predict/file/",
                files={"file": io.BytesIO(decoded)},
            )
            if prediction_response.status_code == 200:
                prediction_data = prediction_response.json()
                prediction_df = pd.DataFrame(prediction_data)
                prediction_summary = prediction_df["ChurnPrediction"].value_counts().reset_index()
                prediction_summary.columns = ["ChurnPrediction", "Count"]
                prediction_summary["Label"] = prediction_summary["ChurnPrediction"].replace({0: "No Churn", 1: "Churn"})
                prediction_fig = px.pie(
                    prediction_summary,
                    names="Label",
                    values="Count",
                    title="Churn Prediction Summary",
                    color="Label",
                    color_discrete_map={"No Churn": "blue", "Churn": "red"},
                )
        except:
            pass

    # Revenue Leakage Analysis
    try:
        revenue_leakage_response = requests.post(
            f"{BASE_URL}/adhoc/",
            params={"analysis_type": "revenue_leakage"},
            json={"segment": "SeniorCitizen", "include_churned": True},
        )
        if revenue_leakage_response.status_code == 200:
            revenue_leakage_data = revenue_leakage_response.json()
            revenue_leakage_df = pd.DataFrame(revenue_leakage_data)
            revenue_leakage_fig = px.pie(
                revenue_leakage_df,
                names="segment",
                values="revenue_lost",
                title="Revenue Leakage by Segment",
                color_discrete_sequence=px.colors.sequential.RdBu,
            )
    except:
        pass

    # Churn Heatmap Analysis
    try:
        heatmap_response = requests.post(
            f"{BASE_URL}/adhoc/",
            params={"analysis_type": "churn_heatmap"},
            json={},
        )
        if heatmap_response.status_code == 200:
            heatmap_data = heatmap_response.json()
            heatmap_df = pd.DataFrame(heatmap_data)
            churn_heatmap_fig = px.density_heatmap(
                heatmap_df,
                x="InternetService",
                y="MonthlyCharges",
                z="churn_likelihood",
                title="Churn Heatmap: Internet Service vs Monthly Charges",
                color_continuous_scale="Viridis",
            )
    except:
        pass

    # Stacked Bar Chart
    try:
        stacked_response = requests.post(
            f"{BASE_URL}/adhoc/",
            params={"analysis_type": "stacked_bar"},
            json={"fields": ["Contract", "Churn"], "metrics": ["TotalCharges"]},
        )
        if stacked_response.status_code == 200:
            stacked_data = stacked_response.json()
            stacked_df = pd.DataFrame(stacked_data)
            stacked_bar_fig = px.bar(
                stacked_df,
                x="segment",
                y=["total_revenue"],
                color="churn_status",
                title="Churned vs Non-Churned Revenue",
                barmode="stack",
            )
    except:
        pass

    # Cohort Analysis
    try:
        cohort_response = requests.post(
            f"{BASE_URL}/adhoc/",
            params={"analysis_type": "cohort_analysis"},
            json={"cohort_field": "tenure", "target_field": "Churn"},
        )
        if cohort_response.status_code == 200:
            cohort_data = cohort_response.json()
            cohort_df = pd.DataFrame(cohort_data)
            cohort_fig = px.line(
                cohort_df,
                x="tenure_range",
                y="churned_customers",
                title="Cohort Analysis: Churned Customers by Tenure Range",
                markers=True,
            )
    except:
        pass

    # Ad-hoc Analysis
    try:
        if adhoc_analysis_type:
            parameters = eval(adhoc_parameters) if adhoc_parameters else {}
            adhoc_response = requests.post(
                f"{BASE_URL}/adhoc/",
                params={"analysis_type": adhoc_analysis_type},
                json=parameters,
            )
            if adhoc_response.status_code == 200:
                adhoc_data = adhoc_response.json()
                adhoc_df = pd.DataFrame(adhoc_data)
                adhoc_fig = px.bar(
                    adhoc_df,
                    x=list(adhoc_df.columns)[0],
                    y=list(adhoc_df.columns)[1],
                    title=f"Ad-hoc Analysis: {adhoc_analysis_type.title()}",
                )
    except:
        pass

    return (
        segments_fig,
        contract_fig,
        tenure_fig,
        payment_methods_fig,
        prediction_fig,
        revenue_leakage_fig,
        churn_heatmap_fig,
        stacked_bar_fig,
        cohort_fig,
        adhoc_fig,
        total_customers,
        avg_charges,
        churn_rate,
    )


if __name__ == "__main__":
    app.run_server(debug=True)
