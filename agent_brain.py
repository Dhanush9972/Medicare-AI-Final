import requests
import json

# 1. The Tool (Symptom Checker Logic)
def symptom_checker_tool(text):
    text = text.lower()
    if "headache" in text and "light" in text:
        return "⚠️ Possible Migraine. Suggestion: Rest in a dark room and drink water."
    elif "fever" in text and "shiver" in text:
        return "⚠️ Possible Viral Infection. Suggestion: Monitor temperature and stay hydrated."
    elif "chest" in text and "pain" in text:
        return "🚨 CRITICAL: Possible Heart Issue. Advice: Call Emergency Services immediately."
    elif "stomach" in text or "pain" in text:
        return "⚠️ General Pain detected. Suggestion: Consult a doctor if pain persists."
    else:
        return None  # No medical advice needed, let the AI chat normally

# 2. The Agent Logic (Manual)
def query_agent(user_input):
    # Step A: Check if we need the Medical Tool
    tool_result = symptom_checker_tool(user_input)
    
    if tool_result:
        # If the tool found a medical issue, return that directly
        return tool_result
    
    # Step B: If no medical issue, ask Ollama to chat
    # We use direct HTTP request to avoid library compatibility issues
    try:
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "llama3",
            "prompt": f"You are a helpful medical receptionist. The user says: '{user_input}'. Reply briefly and politely.",
            "stream": False
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return response.json()['response']
        else:
            return "Error: Could not connect to Ollama."
            
    except Exception as e:
        return f"Error connecting to AI: {str(e)}. Make sure Ollama is running."

# Test it locally
if __name__ == "__main__":
    print(query_agent("I have a headache"))