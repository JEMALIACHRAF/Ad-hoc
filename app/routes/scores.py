from fastapi import APIRouter
from app.services.elasticsearch_service import search_data, index_data

router = APIRouter()

@router.get("/")
async def get_scores():
    """
    Fetch all scores from Elasticsearch for the Telco dataset.
    """
    query = {"query": {"match_all": {}}}
    response = search_data("telco_customer_index", query)
    hits = response.get("hits", {}).get("hits", [])
    return [hit["_source"] for hit in hits]


@router.post("/")
async def add_scores(scores: list[dict]):
    """
    Add or update scores in Elasticsearch for the Telco dataset.
    """
    for score in scores:
        index_data("telco_customer_churn_index", score)
    return {"message": "Scores added successfully"}


@router.get("/scores/aggregated/")
async def get_aggregated_scores():
    """
    Retrieve aggregated scores, such as average churn risk and monthly charges, grouped by customer segments.
    """
    query = {
        "size": 0,
        "aggs": {
            "segments": {
                "terms": {"field": "Contract"},  # Group by Contract (e.g., Month-to-month, One year)
                "aggs": {
                    "average_churn_risk": {
                        "avg": {"field": "Churn"}  # Calculate average churn likelihood
                    },
                    "average_monthly_charges": {
                        "avg": {"field": "MonthlyCharges"}  # Calculate average monthly charges
                    }
                }
            }
        }
    }
    response = search_data("telco_customer_churn_index", query)
    buckets = response.get("aggregations", {}).get("segments", {}).get("buckets", [])

    # Debugging: Print the buckets to check what is returned from Elasticsearch
    print("Aggregated buckets:", buckets)

    result = [
        {
            "segment": bucket["key"],
            "average_churn_risk": bucket["average_churn_risk"]["value"],
            "average_monthly_charges": bucket["average_monthly_charges"]["value"]
        }
        for bucket in buckets
    ]
    return result

