from fastapi import APIRouter, HTTPException
from app.services.elasticsearch_service import search_data

router = APIRouter()

@router.post("/adhoc/")
async def perform_adhoc_analysis(analysis_type: str, parameters: dict):
    """
    Perform ad-hoc analysis based on the provided type and parameters.
    
    Parameters:
    - analysis_type: Type of analysis to perform (e.g., "retention", "engagement", "revenue_leakage").
    - parameters: Additional filters or options for the analysis.
    """
    if analysis_type == "retention":
        return await retention_analysis(parameters)
    elif analysis_type == "engagement":
        return await engagement_analysis(parameters)
    elif analysis_type == "revenue_leakage":
        return await revenue_leakage_analysis(parameters)
    elif analysis_type == "churn_heatmap":
        return await churn_heatmap_analysis(parameters)
    elif analysis_type == "stacked_bar":
        return await stacked_bar_analysis(parameters)
    elif analysis_type == "cohort_analysis":
        return await cohort_analysis(parameters)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown analysis type: {analysis_type}")


async def retention_analysis(parameters: dict):
    """
    Retention analysis: Analyze churned customers grouped by contract type.
    """
    query = {
        "query": {"match_all": {}},
        "aggs": {
            "contract_retention": {
                "terms": {"field": "Contract"},
                "aggs": {
                    "churned_customers": {"filter": {"term": {"Churn": True}}}
                }
            }
        }
    }

    if "contract" in parameters:
        query["query"] = {"term": {"Contract": parameters["contract"]}}

    response = search_data("telco_customer_churn_index", query)
    buckets = response.get("aggregations", {}).get("contract_retention", {}).get("buckets", [])
    return [{"contract": b["key"], "churned_customers": b["churned_customers"]["doc_count"]} for b in buckets]


async def engagement_analysis(parameters: dict):
    """
    Engagement analysis: Analyze total revenue grouped by payment method.
    """
    query = {
        "query": {"match_all": {}},
        "aggs": {
            "payment_engagement": {
                "terms": {"field": "PaymentMethod"},
                "aggs": {"total_revenue": {"sum": {"field": "TotalCharges"}}}
            }
        }
    }

    response = search_data("telco_customer_churn_index", query)
    buckets = response.get("aggregations", {}).get("payment_engagement", {}).get("buckets", [])
    return [{"payment_method": b["key"], "total_revenue": b["total_revenue"]["value"]} for b in buckets]


async def revenue_leakage_analysis(parameters: dict):
    """
    Revenue leakage: Analyze revenue lost by churned customers grouped by a segment.
    """
    segment_field = parameters.get("segment", "Contract")
    query = {
        "query": {"term": {"Churn": True}},  # Filter churned customers
        "aggs": {
            "segment_revenue": {
                "terms": {"field": segment_field},
                "aggs": {"total_revenue_lost": {"sum": {"field": "TotalCharges"}}}
            }
        }
    }

    response = search_data("telco_customer_churn_index", query)
    buckets = response.get("aggregations", {}).get("segment_revenue", {}).get("buckets", [])
    return [{"segment": b["key"], "revenue_lost": b["total_revenue_lost"]["value"]} for b in buckets]


async def churn_heatmap_analysis(parameters: dict):
    """
    Churn heatmap: Analyze churn likelihood across multiple dimensions.
    """
    x_field = parameters.get("x_field", "InternetService")
    y_field = parameters.get("y_field", "MonthlyCharges")
    query = {
        "query": {"match_all": {}},
        "aggs": {
            "x_field_buckets": {
                "terms": {"field": x_field},
                "aggs": {
                    "y_field_buckets": {
                        "terms": {"field": y_field},
                        "aggs": {"churn_likelihood": {"avg": {"field": "Churn"}}}
                    }
                }
            }
        }
    }

    response = search_data("telco_customer_churn_index", query)
    x_buckets = response.get("aggregations", {}).get("x_field_buckets", {}).get("buckets", [])
    heatmap_data = []
    for x_bucket in x_buckets:
        for y_bucket in x_bucket.get("y_field_buckets", {}).get("buckets", []):
            heatmap_data.append({
                "x_field": x_bucket["key"],
                "y_field": y_bucket["key"],
                "churn_likelihood": y_bucket["churn_likelihood"]["value"]
            })
    return heatmap_data


async def stacked_bar_analysis(parameters: dict):
    """
    Stacked bar analysis: Analyze churned vs. non-churned revenue contribution by segments.
    """
    fields = parameters.get("fields", ["Contract", "Churn"])
    query = {
        "query": {"match_all": {}},
        "aggs": {
            "field_buckets": {
                "terms": {"field": fields[0]},
                "aggs": {
                    "churn_buckets": {
                        "terms": {"field": fields[1]},
                        "aggs": {"total_revenue": {"sum": {"field": "TotalCharges"}}}
                    }
                }
            }
        }
    }

    response = search_data("telco_customer_churn_index", query)
    field_buckets = response.get("aggregations", {}).get("field_buckets", {}).get("buckets", [])
    stacked_data = []
    for field_bucket in field_buckets:
        for churn_bucket in field_bucket.get("churn_buckets", {}).get("buckets", []):
            stacked_data.append({
                "segment": field_bucket["key"],
                "churn_status": churn_bucket["key"],
                "total_revenue": churn_bucket["total_revenue"]["value"]
            })
    return stacked_data


async def cohort_analysis(parameters: dict):
    """
    Cohort analysis: Analyze churn patterns over tenure cohorts.
    """
    query = {
        "query": {"match_all": {}},
        "aggs": {
            "tenure_cohorts": {
                "range": {
                    "field": "tenure",
                    "ranges": [
                        {"to": 12}, {"from": 12, "to": 24}, {"from": 24, "to": 36},
                        {"from": 36, "to": 48}, {"from": 48, "to": 60}, {"from": 60}
                    ]
                },
                "aggs": {
                    "churned_customers": {"filter": {"term": {"Churn": True}}}
                }
            }
        }
    }

    response = search_data("telco_customer_churn_index", query)
    tenure_buckets = response.get("aggregations", {}).get("tenure_cohorts", {}).get("buckets", [])
    return [{"tenure_range": b["key"], "churned_customers": b["churned_customers"]["doc_count"]} for b in tenure_buckets]
