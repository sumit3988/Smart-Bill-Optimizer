import os
import json
import google.generativeai as genai

class EnergyAIChatbot:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(EnergyAIChatbot, cls).__new__(cls)
            cls._instance._initialize(*args, **kwargs)
        return cls._instance

    def _initialize(self, force_reload=False):
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            
        self.system_prompt = """You are EcoSmart AI, an expert assistant trained on energy sector knowledge. 
Your specific goal is to help users track their energy consumption, lower their electricity bills, and optimize appliance usage. 
Always stay within the energy domain. If a question is outside the energy domain, politely redirect the user back to energy topics. 
Keep responses clear, structured, practical, and friendly.

When the user provides their personal usage statistics (units, cost, efficiency score), use them to provide personalized insights and actionable advice."""
        
        # We use gemini-2.5-flash as the older models like 1.5-flash and gemini-pro are no longer available for this key.
        try:
            self.model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=self.system_prompt)
        except Exception:
            self.model = None

    def get_response(self, user_message, user_stats=None):
        if not self.model:
            return {
                "reply": "Error: Gemini model not initialized. Please ensure GOOGLE_API_KEY is set in your .env file or environment variables.",
                "intent": "error",
                "confidence": 0.0
            }
            
        if not user_stats:
            user_stats = {}
            
        # Construct the context prompt with user stats
        context = ""
        if user_stats:
            context = f"User's current month statistics:\n- Usage: {user_stats.get('user_kwh', 0)} units (kWh)\n- Estimated Cost: ₹{user_stats.get('user_cost', 0)}\n- Efficiency Score: {user_stats.get('score', 0)}/100\n- Comparison: {user_stats.get('comparison', 'average')}\n\n"
        
        full_prompt = context + f"User Message: {user_message}"
        
        try:
            chat = self.model.start_chat(history=[])
            response = chat.send_message(full_prompt)
            reply = response.text
            intent = "gemini_response"
            confidence = 0.99
        except Exception as e:
            reply = f"I'm sorry, I encountered an error connecting to the AI service. Please try again later. (Error: {str(e)})"
            intent = "fallback"
            confidence = 0.0
            
        return {"reply": reply, "intent": intent, "confidence": confidence}

