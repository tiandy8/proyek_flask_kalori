# chatbot.py
import os
import google.generativeai as genai
from config import Config # Import Config to get the key if needed

# Configure the Gemini API key
try:
    api_key = Config.GEMINI_API_KEY
    if not api_key or api_key == 'YOUR_API_KEY_HERE': # Basic check if placeholder is still there
        print("ERROR: GEMINI_API_KEY not configured correctly in config.py or environment variables.")
        # You might want to raise an exception or handle this more gracefully
        api_key = None
    else:
         genai.configure(api_key=api_key)
except AttributeError:
    print("ERROR: GEMINI_API_KEY not found in Config class.")
    api_key = None
except Exception as e:
    print(f"An error occurred during Gemini configuration: {e}")
    api_key = None


# Define the system prompt/instruction for the nutrition bot
NUTRITION_SYSTEM_PROMPT = """You are NutriBot, a friendly and knowledgeable AI assistant specializing in healthy nutrition, food facts, calorie information, basic meal planning ideas, and general wellness advice directly related to diet and food.

Your primary functions are:
- Provide factual information about nutrients (vitamins, minerals, macros).
- Explain nutritional benefits of different foods.
- Give approximate calorie counts for common foods (clearly state these are estimates).
- Offer general healthy eating tips and simple meal ideas.
- Answer questions about food safety basics.

Do NOT:
- Provide specific medical advice or diagnoses. Refer users to healthcare professionals for medical concerns.
- Create complex, personalized meal plans (offer only general ideas).
- Answer questions unrelated to food, nutrition, health, and wellness. If asked unrelated questions, politely state that you specialize in nutrition-related topics.
- Make definitive health claims; use cautious language like "may help," "is associated with," etc.

Keep your answers concise, easy to understand, and encouraging. Be positive and supportive.
"""

# --- Option 1: Using generate_content (Simpler for single turns) ---
def get_gemini_response(user_message):
    if not api_key:
        return "Sorry, the chatbot is not configured correctly due to an API key issue."

    try:
        # Choose a model suitable for chat and available in free tier (e.g., 'gemini-1.5-flash-latest')
        # Check Google AI Studio or docs for currently available free models
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        # Combine system prompt and user message
        full_prompt = f"{NUTRITION_SYSTEM_PROMPT}\n\nUser Question: {user_message}\n\nNutriBot Answer:"

        # Generate response
        response = model.generate_content(full_prompt)

        # Basic safety check (can be more robust)
        if response.parts:
             return response.text
        elif response.prompt_feedback and response.prompt_feedback.block_reason:
             print(f"Gemini response blocked. Reason: {response.prompt_feedback.block_reason}")
             return "I cannot provide a response to that request due to safety guidelines."
        else:
             # Handle cases where response might be empty without being explicitly blocked
             return "Sorry, I couldn't generate a response for that. Please try rephrasing."

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        # Provide a generic error to the user
        return "Sorry, I encountered an error trying to get a response. Please try again later."


# --- Option 2: Using Chat Session (Better for conversational history, more complex setup) ---
# You might want to implement this later if you need conversation memory.
# It involves storing chat history server-side or client-side.
# Example structure (incomplete):
# model = genai.GenerativeModel('gemini-1.5-flash-latest', system_instruction=NUTRITION_SYSTEM_PROMPT)
# chat = model.start_chat(history=[]) # Need to load/save history
# response = chat.send_message(user_message)
# return response.text

def analyze_food_image(image_data):
    if not api_key:
        return "Sorry, the image analysis is not configured correctly due to an API key issue."

    try:
        # Initialize the Gemini Pro Vision model
        model = genai.GenerativeModel('gemini-pro-vision')
        
        # Create the prompt for food analysis
        prompt = """Analyze this food image and provide:
1. A description of the food
2. Estimated calories (if possible to identify)
3. Key nutritional information
4. Any health benefits or concerns

Please be specific but acknowledge that calorie estimates are approximate."""

        # Generate response from the image
        response = model.generate_content([prompt, image_data])
        
        if response.parts:
            return response.text
        elif response.prompt_feedback and response.prompt_feedback.block_reason:
            print(f"Gemini response blocked. Reason: {response.prompt_feedback.block_reason}")
            return "I cannot analyze this image due to safety guidelines."
        else:
            return "Sorry, I couldn't analyze this image. Please try a different image."

    except Exception as e:
        print(f"Error analyzing image with Gemini API: {e}")
        return "Sorry, I encountered an error trying to analyze the image. Please try again later."