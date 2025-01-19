from fastapi import APIRouter
from app.services.elasticsearch_service import search_data

router = APIRouter()

@router.get("/telco/summary/")
async def get_telco_summary():
    """
    Retrieve a summary of the Telco userbase, including average churn likelihood,
    total charges, and counts of contract types.
    """
    query = {
        "size": 0,  # Only aggregation results
        "aggs": {
            "avg_churn_likelihood": {"avg": {"field": "Churn"}},  # Churn encoded as binary (0/1)
            "total_monthly_charges": {"sum": {"field": "MonthlyCharges"}},  # Total of monthly charges
            "contract_types": {"terms": {"field": "Contract"}}  # Breakdown by contract type
        }
    }
    response = search_data("telco_customer_churn_index", query)
    return {
        "average_churn_likelihood": response["aggregations"]["avg_churn_likelihood"]["value"],
        "total_monthly_charges": response["aggregations"]["total_monthly_charges"]["value"],
        "contract_types": response["aggregations"]["contract_types"]["buckets"]
    }

@router.get("/telco/payment-methods/")
async def get_payment_methods():
    """
    Retrieve the distribution of payment methods among Telco users.
    """
    query = {
        "size": 0,  # Only aggregation results
        "aggs": {
            "payment_methods": {"terms": {"field": "PaymentMethod"}}
        }
    }
    response = search_data("telco_customer_churn_index", query)
    return response["aggregations"]["payment_methods"]["buckets"]

@router.get("/telco/tenure-distribution/")
async def get_tenure_distribution():
    """
    Retrieve the distribution of user tenure among Telco users.
    """
    query = {
        "size": 0,  # Only aggregation results
        "aggs": {
            "tenure_distribution": {
                "histogram": {"field": "tenure", "interval": 12}  # Group by yearly intervals
            }
        }
    }
    response = search_data("telco_customer_churn_index", query)
    return response["aggregations"]["tenure_distribution"]["buckets"]
