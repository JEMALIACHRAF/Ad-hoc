from fastapi import APIRouter
from app.services.elasticsearch_service import search_data, index_data

router = APIRouter()

@router.get("/")
async def get_programs():
    """
    Fetch all program performance data from Elasticsearch.
    """
    query = {"query": {"match_all": {}}}
    response = search_data("programs_index", query)
    hits = response.get("hits", {}).get("hits", [])
    return [hit["_source"] for hit in hits]

@router.post("/")
async def add_programs(programs: list[dict]):
    """
    Add or update program performance data in Elasticsearch.
    """
    for program in programs:
        index_data("programs_index", program)
    return {"message": "Programs added successfully"}

@router.get("/top/")
async def get_top_programs():
    """
    Get top programs by views.
    """
    query = {
        "size": 0,
        "aggs": {
            "top_programs": {
                "terms": {"field": "program_name.keyword", "size": 10},
                "aggs": {"total_views": {"sum": {"field": "views"}}}
            }
        }
    }
    response = search_data("programs_index", query)
    buckets = response.get("aggregations", {}).get("top_programs", {}).get("buckets", [])
    return [
        {"program_name": bucket["key"], "total_views": bucket["total_views"]["value"]}
        for bucket in buckets
    ]
