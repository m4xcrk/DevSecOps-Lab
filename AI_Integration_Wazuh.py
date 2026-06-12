import os
import json
import requests
import urllib3
from ollama import chat

# Suppress self-signed SSL warnings for lab environments
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration Variables (Loaded from environment or defaults)
INDEXER_HOST = os.getenv("INDEXER_HOST", "https://127.0.0.1:9200")
INDEXER_USER = os.getenv("INDEXER_USER", "indexer_agentic")
INDEXER_PASS = os.getenv("INDEXER_PASS", "YourSecurePasswordHere")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")

def query_wazuh_indexer(search_keyword, size=5):
    """
    Tool: Queries the Wazuh Indexer search API for historical security alerts.
    """
    endpoint = f"{INDEXER_HOST}/wazuh-alerts-*/_search"
    query_body = {
        "size": size,
        "query": {
            "multi_match": {
                "query": search_keyword,
                "fields": ["rule.description", "full_log", "agent.name", "data.win.eventdata.image"]
            }
        },
        "_source": ["@timestamp", "agent.id", "agent.name", "rule.description", "rule.level", "full_log"]
    }
    
    try:
        response = requests.post(
            endpoint, 
            auth=(INDEXER_USER, INDEXER_PASS), 
            json=query_body, 
            verify=False
        )
        if response.status_code == 200:
            hits = response.json().get("hits", {}).get("hits", [])
            return [hit["_source"] for hit in hits]
        else:
            return f"Error querying indexer: Status Code {response.status_code}"
    except Exception as e:
        return f"Indexer connection exception: {str(e)}"

def run_agentic_hunt(user_prompt):
    """
    Orchestrates the ReAct (Reasoning and Acting) loop using native model tool calling.
    """
    # Define available tools to the LLM
    tools = [{
        'type': 'function',
        'function': {
            'name': 'query_wazuh_indexer',
            'description': 'Search historical Wazuh alerts for specific indicators, attack techniques, or keywords.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'search_keyword': {
                        'type': 'string',
                        'description': 'The security event keyword, rule string, or indicator to hunt for.',
                    },
                    'size': {
                        'type': 'integer',
                        'description': 'Number of log results to return (default is 5).',
                    }
                },
                'required': ['search_keyword'],
            },
        },
    }]

    messages = [
        {"role": "system", "content": "You are an expert autonomous SOC Threat Hunting Agent. Use the provided tools to discover, correlate, and investigate activities inside Wazuh logs before rendering a final analysis report."},
        {"role": "user", "content": user_prompt}
    ]

    print(f"🤖 Initializing Hunt Strategy: '{user_prompt}'")
    
    # First Turn: Model determines if a tool call is required to satisfy the objective
    response = chat(model=OLLAMA_MODEL, messages=messages, tools=tools)
    messages.append(response['message'])

    # Verify if the agent made a decision to execute a tool
    if response['message'].get('tool_calls'):
        for tool_call in response['message']['tool_calls']:
            if tool_call['function']['name'] == 'query_wazuh_indexer':
                args = tool_call['function']['parameters']
                print(f"🔎 Agent selected tool: query_wazuh_indexer(search_keyword='{args['search_keyword']}')")
                
                # Execute the real-world tool action
                tool_output = query_wazuh_indexer(args['search_keyword'])
                
                # Feed results back into the agent's memory bank
                messages.append({
                    "role": "tool",
                    "content": json.dumps(tool_output),
                    "name": "query_wazuh_indexer"
                })
                
        # Second Turn: Model reviews the log payload and formulates its structural analysis
        print("🧠 Analyzing telemetry payload and writing finalized report...")
        final_analysis = chat(model=OLLAMA_MODEL, messages=messages)
        return final_analysis['message']['content']
    else:
        return response['message']['content']

if __name__ == "__main__":
    # Test Example: Prompting the autonomous agent loop to locate explicit privilege escalation patterns
    prompt = "Check my security logs for traces of credential dumping or lsass read attempts."
    report = run_agentic_hunt(prompt)
    print("\n================ 📑 THREAT HUNT REPORT ================\n")
    print(report)