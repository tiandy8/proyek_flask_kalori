# chatbot.py
import os
import base64
import requests
from config import Config

# Configure the Chat API (OpenRouter)
CHAT_API_KEY = Config.CHAT_API_KEY
if not CHAT_API_KEY or CHAT_API_KEY == 'YOUR_API_KEY_HERE':
    raise ValueError("Chat API key not configured. Please set CHAT_API_KEY in your .env file.")

# Configure OpenAI API
OPENAI_API_KEY = Config.OPENAI_API_KEY
if not OPENAI_API_KEY or OPENAI_API_KEY == 'YOUR_API_KEY_HERE':
    raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY in your .env file.")

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
    """Get response from the chat API."""
    try:
        print(f"Processing message: {user_message}")
        print(f"Using API key: {CHAT_API_KEY[:5]}...")  # Print first 5 chars for debugging
        
        headers = {
            "Authorization": f"Bearer {CHAT_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek/deepseek-coder-1.3b-base",
            "messages": [
                {"role": "system", "content": NUTRITION_SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ]
        }
        
        print("Sending request to API...")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        print(f"API Response Status: {response.status_code}")
        print(f"API Response Headers: {response.headers}")
        print(f"API Response Content: {response.text[:200]}...")  # Print first 200 chars
        
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
    """Analyze food image using OpenAI's vision API."""
    try:
        # Convert image to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Prepare the request
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please analyze this food image and provide the following information in a structured format:\n1. Name of the food\n2. Estimated calories\n3. Protein content in grams\n4. Carbohydrates in grams\n5. Fat content in grams\n\nFormat your response as a JSON object with these fields: name, calories, protein, carbs, fat. If you're unsure about any value, use null."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }
        
        # Make the API request
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Try to parse the JSON response
            try:
                import json
                food_data = json.loads(content)
                
                # Format the analysis result
                analysis_result = "Food Analysis Results:\n\n"
                analysis_result += f"Food Name: {food_data.get('name', 'Unknown')}\n"
                analysis_result += f"Calories: {food_data.get('calories', 'N/A')} kcal\n"
                analysis_result += f"Protein: {food_data.get('protein', 'N/A')}g\n"
                analysis_result += f"Carbs: {food_data.get('carbs', 'N/A')}g\n"
                analysis_result += f"Fat: {food_data.get('fat', 'N/A')}g\n"
                
                return analysis_result
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw response
                return f"Food Analysis Results:\n\n{content}"
        else:
            error_msg = f"API Error: {response.status_code} - {response.text}"
            print(error_msg)
            return f"Sorry, I couldn't analyze the image. Error: {error_msg}"
            
    except Exception as e:
        error_msg = f"Error analyzing image: {str(e)}"
        print(error_msg)
        return f"Sorry, I encountered an error while analyzing the image: {error_msg}"