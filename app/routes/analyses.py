import nest_asyncio
import asyncio
import aiohttp
import json
import logging
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict
from app.services.elasticsearch_service import search_data  # Adjust import as per your project structure
import logging
from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, Dict, Any
from app.services.elasticsearch_service import search_data
# Apply nest_asyncio to allow asyncio in Jupyter notebooks (if needed)
nest_asyncio.apply()

# OpenAI API configuration
OPENAI_API_KEY = "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"
model_name = "gpt-4o-2024-05-13"  # Adjust the model name as per your OpenAI account

router = APIRouter()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)



import re

async def generate_async(model, analysis_type, parameters):
    """
    Generates an Elasticsearch query using OpenAI's API based on analysis type and parameters.
    """
    prompt = f"""
    Generate a valid Elasticsearch query for {analysis_type} analysis based on the following parameters: {parameters}.
    The query must:
    1. Use the following field mappings for the Elasticsearch index:
    - `customerID`: keyword
    - `gender`: keyword
    - `SeniorCitizen`: integer
    - `Partner`: keyword
    - `Dependents`: keyword
    - `tenure`: integer
    - `PhoneService`: keyword
    - `MultipleLines`: keyword
    - `InternetService`: keyword
    - `OnlineSecurity`: keyword
    - `OnlineBackup`: keyword
    - `DeviceProtection`: keyword
    - `TechSupport`: keyword
    - `StreamingTV`: keyword
    - `StreamingMovies`: keyword
    - `Contract`: keyword
    - `PaperlessBilling`: keyword
    - `PaymentMethod`: keyword
    - `MonthlyCharges`: float
    - `TotalCharges`: float
    - `Churn`: boolean
    2. Include filters or aggregations as specified in the parameters.
    3. Be well-formed JSON that is directly executable in Elasticsearch.
    4. Do not include any explanations, only the JSON query wrapped in ```json``` code block.
    """

    logger.info(f"Sending prompt to GPT for {analysis_type} analysis with parameters: {parameters}")
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                raw_response = await response.text()
                logger.debug(f"Raw response from OpenAI API: {raw_response}")

                if response.status == 200:
                    result = json.loads(raw_response)
                    if result.get('choices') and result['choices'][0].get('message'):
                        response_content = result['choices'][0]['message']['content']
                        
                        # Extract the JSON block using regex
                        match = re.search(r"```json(.*?)```", response_content, re.DOTALL)
                        if match:
                            json_query = match.group(1).strip()
                            query_json = json.loads(json_query)  # Parse the JSON
                            logger.info(f"Generated valid Elasticsearch query: {query_json}")
                            return query_json
                        else:
                            logger.error(f"Could not extract JSON from GPT response: {response_content}")
                            return None
                    else:
                        logger.error(f"Unexpected GPT response structure: {result}")
                        return None
                else:
                    logger.error(f"GPT API Error {response.status}: {raw_response}")
                    return None
    except Exception as e:
        logger.error(f"Error generating query with GPT: {str(e)}")
        return None

# Logging setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@router.post("/adhoc/")
async def perform_adhoc_analysis(
    analysis_type: str = Query(..., description="Type of analysis to perform"),
    body: Optional[Dict[str, Any]] = Body(default=None, example={
        "filters": {
            "Churn": True,
            "InternetService": "Fiber optic"
        },
        "aggregations": {
            "tenure": "range",
            "MonthlyCharges": "avg"
        }
    })
):
    """
    Perform ad-hoc analysis.
    Activates GPT for query generation if input is empty, partial, or ambiguous.
    """
    try:
        # Determine if GPT is needed
        use_gpt = False
        if not body:  # Empty input
            use_gpt = True
            logger.info("Empty input detected. Activating GPT for query generation.")
        elif not body.get("filters") or not body.get("aggregations"):  # Partial input
            use_gpt = True
            logger.info("Partial input detected. Activating GPT for query generation.")
        elif analysis_type and analysis_type not in ["basic", "predefined"]:  # Abstract input
            use_gpt = True
            logger.info(f"Abstract analysis_type '{analysis_type}' detected. Activating GPT.")

        # Use GPT to generate query if needed
        if use_gpt:
            gpt_generated_query = await generate_async(
                model=model_name,
                analysis_type=analysis_type,
                parameters=body or {}
            )
            if not gpt_generated_query:
                raise HTTPException(status_code=500, detail="Failed to generate query using GPT")
            es_query = gpt_generated_query
        else:
            # Manually construct Elasticsearch query
            es_query = {"size": 0, "query": {"bool": {"filter": []}}, "aggs": {}}

            # Add filters
            if "filters" in body:
                for field, value in body["filters"].items():
                    if isinstance(value, dict):  # Range query
                        es_query["query"]["bool"]["filter"].append({"range": {field: value}})
                    else:  # Term query
                        es_query["query"]["bool"]["filter"].append({"term": {field: value}})
            
            # Add aggregations
            if "aggregations" in body:
                for field, agg_type in body["aggregations"].items():
                    if agg_type == "range":
                        es_query["aggs"][field] = {
                            "range": {
                                "field": field,
                                "ranges": [
                                    {"key": "short", "to": 12},
                                    {"key": "medium", "from": 12, "to": 24},
                                    {"key": "long", "from": 24}
                                ]
                            }
                        }
                    elif agg_type == "avg":
                        es_query["aggs"][field] = {"avg": {"field": field}}
                    elif agg_type == "sum":
                        es_query["aggs"][field] = {"sum": {"field": field}}
                    elif agg_type == "terms":
                        es_query["aggs"][field] = {"terms": {"field": field}}

        # Log and execute query
        logger.debug(f"Elasticsearch Query: {json.dumps(es_query, indent=2)}")
        response = search_data("telco_customer_churn_index", es_query)

        # Process response
        response_data = response.body if hasattr(response, "body") else dict(response)
        return {
            "results": response_data.get("hits", {}).get("hits", []),
            "aggregations": response_data.get("aggregations", {})
        }

    except Exception as e:
        logger.error(f"Error performing ad-hoc analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
