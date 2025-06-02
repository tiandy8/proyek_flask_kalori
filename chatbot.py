# chatbot.py
import os
import base64
import requests
from config import Config

# Configure the OpenRouter API
OPENROUTER_API_KEY = Config.OPENROUTER_API_KEY
if not OPENROUTER_API_KEY:
    raise ValueError("OpenRouter API key not configured. Please set OPENROUTER_API_KEY in your .env file.")

# System prompt for the nutrition bot
NUTRITION_SYSTEM_PROMPT = """You are a helpful nutrition assistant. You can:
1. Answer questions about nutrition and healthy eating
2. Provide information about food and their nutritional values
3. Help with meal planning and suggest balanced meal combinations
4. Give general dietary advice

Please note that you should:
- Always provide accurate, science-based information
- Include relevant nutritional information when discussing foods
- Suggest consulting healthcare professionals for specific medical advice
- Be clear about general guidelines vs. personalized recommendations"""

def get_chat_response(user_message):
    """Get response from the OpenRouter chat API."""
    try:
        print(f"Processing message: {user_message}")
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",  # Your site URL
            "X-Title": "Kalora Nutrition Assistant"  # Your site name
        }
        
        data = {
            "model": "deepseek/deepseek-r1-0528:free",
            "messages": [
                {"role": "system", "content": NUTRITION_SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ]
        }
        
        print("Sending request to OpenRouter API...")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            error_msg = f"API Error: {response.status_code} - {response.text}"
            print(error_msg)
            return f"Sorry, I encountered an error: {error_msg}"
            
    except Exception as e:
        error_msg = f"Error in get_chat_response: {str(e)}"
        print(error_msg)
        return f"Sorry, I encountered an error: {error_msg}"

def analyze_food_image(image_data):
    """Analyze food image using Meta Llama 4 Maverick via OpenRouter."""
    try:
        # Convert image to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "Kalora Nutrition Assistant"
        }
        
        data = {
            "model": "meta-llama/llama-4-maverick:free",
            "messages": [
                {"role": "system", "content": "You are a helpful vision assistant."},
                {"role": "user", "content": [
                    {"type": "text", "text": "Please analyze this food image and provide the following information in a structured format:\n1. Name of the food\n2. Estimated calories\n3. Protein content in grams\n4. Carbohydrates in grams\n5. Fat content in grams\n\nFormat your response as a JSON object with these fields: name, calories, protein, carbs, fat. If you're unsure about any value, use null."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]}
            ],
            "temperature": 0.3,
            "max_tokens": 1024
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            try:
                import json
                food_data = json.loads(content)
                analysis_result = "Food Analysis Results:\n\n"
                analysis_result += f"Food Name: {food_data.get('name', 'Unknown')}\n"
                analysis_result += f"Calories: {food_data.get('calories', 'N/A')} kcal\n"
                analysis_result += f"Protein: {food_data.get('protein', 'N/A')}g\n"
                analysis_result += f"Carbs: {food_data.get('carbs', 'N/A')}g\n"
                analysis_result += f"Fat: {food_data.get('fat', 'N/A')}g\n"
                return analysis_result
            except Exception:
                return f"Food Analysis Results:\n\n{content}"
        else:
            error_msg = f"API Error: {response.status_code} - {response.text}"
            print(error_msg)
            return f"Sorry, I couldn't analyze the image. Error: {error_msg}"
            
    except Exception as e:
        error_msg = f"Error analyzing image: {str(e)}"
        print(error_msg)
        return f"Sorry, I encountered an error while analyzing the image: {error_msg}"