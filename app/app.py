import streamlit as st
import requests
import json
import aiohttp
import asyncio

API_URL = 'http://127.0.0.1:8000/api/adhoc/'

# OpenAI API Configuration
OPENAI_API_KEY = "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"
MODEL_NAME = "gpt-4o-2024-05-13"  # Replace with the correct model

# Function to send the API request
def send_request_to_api(data, analysis_type):
    url = f"{API_URL}?analysis_type={analysis_type}"
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, json=data, headers=headers)
        return response.json()
    except Exception as e:
        st.error(f"Error sending request: {e}")
        return None

# Function to call GPT to generate interpretation of the analysis result
async def generate_interpretation(prompt):
    url = f"https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('choices') and result['choices'][0].get('message'):
                        return result['choices'][0]['message']['content'].strip()
                else:
                    st.error(f"Error: {response.status} - {await response.text()}")
                    return None
    except Exception as e:
        st.error(f"Error generating interpretation: {str(e)}")
        return None

# App logic
def app():
    st.title("Ad-hoc Analysis")

    # Input section for the user to enter Goal
    goal = st.text_input("Goal", "Calculate the Revenue distribution by payment method.")

    # Selecting analysis type (You can create a dropdown here or a text input)
    analysis_type = st.selectbox("Select Analysis Type", ["Revenue Distribution", "Churn Analysis", "Customer Segmentation"])

    if st.button("Submit"):
        # Forming the correct request payload (no filters in this case)
        data = {
            "Goal": goal
        }

        # Debugging: print the data being sent
        st.write(f"Sending data to API: {data} with analysis_type: {analysis_type}")

        result = send_request_to_api(data, analysis_type)

        if result:
            # Construct the prompt to generate a human-readable interpretation
            prompt = f"""
            Based on the following data and the goal of {goal}, generate a human-readable summary and interpretation of the analysis result:

            {json.dumps(result)}

            The explanation should be clear, concise, and easily understandable by a non-technical user.
            The goal should guide how the data is presented (e.g., focus on revenue for the "Revenue Distribution" goal).
            """

            # Get the interpretation from GPT
            interpretation = asyncio.run(generate_interpretation(prompt))

            if interpretation:
                st.write("Interpretation of Results:")
                st.write(interpretation)  # Show the generated interpretation
        else:
            st.error("Error getting a response from the API")

# Run the app
if __name__ == '__main__':
    app()
