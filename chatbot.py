from database import get_weekly_usage, get_monthly_usage, get_user_profile

class EnergyBot:
    """Rule-based chatbot for electricity optimization queries"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.appliance_consumption = {
            'ac': 1.5,
            'fan': 0.075,
            'fridge': 0.15,
            'tv': 0.1,
            'induction': 1.8,
            'ev': 3.3
        }
        self.profile = get_user_profile(user_id) or {}
        self.monthly_units, self.monthly_bill = get_monthly_usage(user_id)
        self.weekly_data = get_weekly_usage(user_id)

    def get_response_data(self, user_message):
        """Return a structured chatbot response payload."""
        message = (user_message or '').strip().lower()

        if not message:
            return {
                'intent': 'empty',
                'response': self._answer_default()[0],
                'quick_replies': self._default_replies(),
            }

        intent = self._detect_intent(message)
        handler = getattr(self, f'_answer_{intent}', self._answer_default)
        response, quick_replies = handler(message)

        return {
            'intent': intent,
            'response': response,
            'quick_replies': quick_replies,
        }
    
    def get_response(self, user_message):
        """Process user query and return personalized response"""
        return self.get_response_data(user_message)['response']

    def _detect_intent(self, message):
        """Detect the most likely user intent."""
        if self._match_keywords(message, ['hello', 'hi', 'hey', 'good morning', 'good evening', 'greetings']):
            return 'greeting'
        if self._match_keywords(message, ['thank you', 'thanks', 'thankyou', 'appreciate']):
            return 'thanks'
        if self._match_keywords(message, ['reduce my bill', 'reduce bill', 'lower my bill', 'lower bill', 'save money', 'save on bill', 'cut my bill', 'cut bill', 'minimize bill', 'save electricity']):
            return 'reduce_bill'
        if self._match_keywords(message, ['why is my usage high', 'high usage', 'spike', 'surge', 'increase', 'too much', 'bill is high', 'usage is high']):
            return 'high_usage'
        if self._match_keywords(message, ['which appliance', 'appliance consumption', 'device uses', 'uses the most', 'power consumption', 'energy consumption']):
            return 'appliance_consumption'
        if self._match_keywords(message, ['ac', 'air conditioner', 'air conditioning', 'cooling', 'temperature']):
            return 'ac_tips'
        if self._match_keywords(message, ['ev', 'electric vehicle', 'charging', 'charger', 'car battery']):
            return 'ev_tips'
        if self._match_keywords(message, ['track', 'history', 'weekly', 'monthly', 'trend', 'compare', 'analytics']):
            return 'tracking'
        if self._match_keywords(message, ['bill', 'cost', 'tariff', 'slab', 'charge', 'payment', 'rate']):
            return 'bill_info'
        if self._match_keywords(message, ['suggest', 'advice', 'tip', 'recommend', 'ideas', 'help me']):
            return 'suggestions'
        if self._match_keywords(message, ['what can you do', 'help', 'features', 'capabilities', 'how can you help']):
            return 'help'
        return 'default'
    
    def _match_keywords(self, message, keywords):
        """Check if message contains any keywords"""
        for keyword in keywords:
            if keyword in message:
                return True
        return False

    def _profile_prefix(self):
        """Return a short personalized prefix when profile data exists."""
        name = self.profile.get('name') if self.profile else None
        if name and name != 'default_user':
            return f'Hi {name}, '

        family_size = self.profile.get('family_size') if self.profile else None
        property_type = self.profile.get('property_type') if self.profile else None
        parts = []
        if family_size:
            parts.append(f'family size {family_size}')
        if property_type:
            parts.append(property_type)
        if parts:
            return f"For your {' and '.join(parts)}, "

        return ''

    def _summary_line(self):
        """Return a short usage summary."""
        if self.monthly_units > 0:
            return f"You're at {self.monthly_units:.1f} units and ₹{self.monthly_bill:.0f} this month."
        return 'I do not have any usage history for this account yet.'

    def _default_replies(self):
        return [
            'How do I reduce my bill?',
            'Why is my usage high?',
            'Which appliance uses the most?',
            'AC tips',
        ]

    def _reply(self, text, quick_replies=None):
        return text, (quick_replies or self._default_replies())

    def _answer_greeting(self, message):
        response = (
            f"👋 {self._profile_prefix()}I can help you review usage, cut bills, and understand appliance costs.\n\n"
            f"{self._summary_line()}"
        )
        return self._reply(response, ['Reduce my bill', 'Show my usage', 'AC tips', 'EV tips'])

    def _answer_thanks(self, message):
        return self._reply(
            "You’re welcome. If you want, I can also suggest the highest-impact savings actions for your home.",
            ['Reduce my bill', 'Show my usage', 'What can you do?']
        )
    
    def _answer_reduce_bill(self, message):
        """Answer: How to reduce bill"""
        response = (
            f"💡 {self._profile_prefix()}here are the highest-impact ways to cut your bill:\n\n"
            "1. AC optimization - raise the temperature to 24°C and avoid empty-room cooling.\n"
            "2. Shift heavy loads - run EV charging and induction cooking outside peak hours.\n"
            "3. Reduce standby waste - switch off idle chargers, TVs, and adapters.\n"
            "4. Use efficient appliances - 5-star devices usually pay back quickly.\n\n"
            f"{self._summary_line()}"
        )
        return self._reply(response, ['Why is my usage high?', 'AC tips', 'EV tips', 'Show bill details'])
    
    def _answer_high_usage(self, message):
        """Answer: Why is usage high"""
        response = "🔍 **Analysis of your high usage:**\n\n"
        
        if self.monthly_units > 400:
            response += "⚠️ **Critical Level:** Your usage is significantly above average (>400 units/month)\n\n"
            response += "**Likely culprits:**\n"
            response += "• AC running too long or too cold\n"
            response += "• EV charging frequently\n"
            response += "• Induction stove usage patterns\n\n"
            response += "**Immediate action:** Check your AC settings and usage times.\n"
        
        elif self.monthly_units > 250:
            response += "⚠️ **Moderate-High Level:** Your usage is above average (250-400 units/month)\n\n"
            response += "**Check:**\n"
            response += "• AC operating hours and temperature\n"
            response += "• EV charging frequency\n"
            response += "• Other major appliances\n\n"
        
        else:
            response += "✅ **Good News:** Your usage is within normal range!\n\n"
        
        if len(self.weekly_data) > 0:
            response += f"**Weekly Average:** {sum([d[1] for d in self.weekly_data])/len(self.weekly_data):.1f} units/day\n"
        
        response += f"\n📌 **Tip:** {self._summary_line()}"
        
        return self._reply(response, ['Reduce my bill', 'Show usage trend', 'AC tips', 'What can you do?'])
    
    def _answer_appliance_consumption(self, message):
        """Answer: Which appliance consumes most"""
        response = "⚡ **Appliance Power Consumption Ranking:**\n\n"
        response += "🔴 **High Power (>1 kW):**\n"
        response += "• AC: 1.5 kW (6-8 hrs/day = 9-12 units/day)\n"
        response += "• Induction: 1.8 kW (2 hrs/day = 3.6 units/day)\n"
        response += "• EV Charger: 3.3 kW (2 hrs/day = 6.6 units/day)\n\n"
        response += "🟡 **Medium Power (0.1-0.15 kW):**\n"
        response += "• Fridge: 0.15 kW (24 hrs = 3.6 units/day)\n"
        response += "• TV: 0.1 kW (4 hrs/day = 0.4 units/day)\n\n"
        response += "🟢 **Low Power (<0.1 kW):**\n"
        response += "• Fan: 0.075 kW (12 hrs/day = 0.9 units/day)\n\n"
        response += "💡 **Insight:** AC and EV charging usually dominate household consumption."
        
        return self._reply(response, ['AC tips', 'EV tips', 'How do I reduce my bill?', 'Why is my usage high?'])
    
    def _answer_suggestions(self, message):
        """Answer: Get suggestions"""
        response = "💡 **Personalized Energy Saving Tips:**\n\n"
        response += "**For AC:**\n"
        response += "• Set temperature to 24°C\n"
        response += "• Use sleep mode at night\n"
        response += "• Keep filters clean\n\n"
        response += "**For Cooking:**\n"
        response += "• Use flat-base vessels on induction\n"
        response += "• Cover pots to reduce heating time\n\n"
        response += "**For EV:**\n"
        response += "• Charge between 10 PM - 6 AM (off-peak)\n"
        response += "• Use slow charging when possible\n\n"
        response += "**General:**\n"
        response += "• Upgrade to 5-star appliances\n"
        response += "• Use LED bulbs\n"
        response += "• Avoid peak hour usage\n"
        
        return self._reply(response, ['AC tips', 'EV tips', 'Reduce my bill', 'Show tracking'])
    
    def _answer_tracking(self, message):
        """Answer: Tracking and trends"""
        response = "📊 **Your Usage Tracking:**\n\n"
        response += f"**This Month:** {self.monthly_units:.1f} units | ₹{self.monthly_bill:.0f} bill\n\n"
        
        if self.weekly_data:
            daily_avg = sum([d[1] for d in self.weekly_data]) / len(self.weekly_data)
            response += f"**7-Day Average:** {daily_avg:.1f} units/day\n"
            response += f"**7-Day Bill:** ₹{sum([d[2] for d in self.weekly_data]):.0f}\n\n"
        
        response += "**Trend Analysis:**\n"
        if self.monthly_units > 300:
            response += "📈 Your usage trend is HIGH - Focus on optimization\n"
        elif self.monthly_units > 200:
            response += "📊 Your usage trend is MODERATE - Good, but can improve\n"
        else:
            response += "📉 Your usage trend is EFFICIENT - Great job! Maintain it.\n"
        
        response += "\n📌 **Next Step:** Go to Dashboard → Daily Tracking for detailed history"
        
        return self._reply(response, ['Show bill details', 'Why is my usage high?', 'Reduce my bill', 'What can you do?'])
    
    def _answer_bill_info(self, message=None):
        """Answer: Bill information"""
        response = "💰 **Electricity Bill Structure:**\n\n"
        response += "**Our Slab System (per unit):**\n"
        response += "• 0-100 units: ₹3/unit\n"
        response += "• 101-200 units: ₹5/unit\n"
        response += "• 201-500 units: ₹7/unit\n"
        response += "• 500+ units: ₹10/unit\n\n"
        response += "**Example:** 300 units bill\n"
        response += "= (100×₹3) + (100×₹5) + (100×₹7)\n"
        response += "= ₹300 + ₹500 + ₹700 = **₹1500**\n\n"
        response += "**Insight:** Higher slabs cost more per unit, so reducing total usage saves exponentially!"
        
        return self._reply(response, ['Reduce my bill', 'Show my tracking', 'How do slabs work?', 'AC tips'])
    
    def _answer_ac_tips(self, message=None):
        """Answer: AC-specific tips"""
        response = "❄️ **AC Optimization Guide:**\n\n"
        response += "**Temperature Settings:**\n"
        response += "• 18-20°C: Maximum comfort (High bill)\n"
        response += "• 22-24°C: Recommended (Balanced)\n"
        response += "• 26°C+: Energy saver mode (Lower bill)\n\n"
        response += "**Monthly Savings by Temperature:**\n"
        response += "• 1°C lower = +₹20-30 extra cost\n"
        response += "• 1°C higher = -₹20-30 savings\n\n"
        response += "**Best Practices:**\n"
        response += "• Use AC only in used rooms\n"
        response += "• Close doors to unused areas\n"
        response += "• Clean filters every 2 weeks\n"
        response += "• Use sleep mode at night\n"
        response += "• Install reflective window film\n\n"
        response += "💡 **Pro Tip:** AC at 24°C saves 30% vs 20°C!"
        
        return self._reply(response, ['Reduce my bill', 'Why is my usage high?', 'EV tips', 'Show bill details'])
    
    def _answer_ev_tips(self, message=None):
        """Answer: EV charging tips"""
        response = "🔌 **EV Charging Optimization:**\n\n"
        response += "**Charging Schedule:**\n"
        response += "• Off-Peak (10 PM - 6 AM): ₹6-8/unit (Save 30-50%)\n"
        response += "• Peak (6 PM - 9 PM): ₹10-12/unit (Expensive)\n"
        response += "• Normal (9 AM - 6 PM): ₹8-10/unit\n\n"
        response += "**Monthly Savings Example:**\n"
        response += "• Off-peak charging: ₹1200 (40 units × ₹30)\n"
        response += "• Peak charging: ₹1600 (40 units × ₹40)\n"
        response += "• **Savings: ₹400/month**\n\n"
        response += "**Smart Tips:**\n"
        response += "• Charge after 10 PM (minimum billing rate)\n"
        response += "• Use slow charger when possible\n"
        response += "• Track charging times\n"
        response += "• Enable auto-scheduler\n\n"
        response += "⚡ **Insight:** Off-peak charging can save 40% on EV costs!"
        
        return self._reply(response, ['Reduce my bill', 'Show bill details', 'AC tips', 'How do I track usage?'])
    
    def _answer_help(self, message=None):
        """Answer: What can bot do"""
        response = "🤖 **I'm Your Energy Assistant! I can help with:**\n\n"
        response += "✅ **Ask me about:**\n"
        response += "• \"How to reduce my bill?\"\n"
        response += "• \"Why is my usage high?\"\n"
        response += "• \"Which appliance uses most energy?\"\n"
        response += "• \"AC optimization tips\"\n"
        response += "• \"EV charging best practices\"\n"
        response += "• \"My usage trends\"\n"
        response += "• \"Bill breakdown\"\n"
        response += "• \"Energy saving tips\"\n\n"
        response += "📌 **Features & Sections:**\n"
        response += "• 📊 Dashboard: Daily/Weekly/Monthly tracking\n"
        response += "• 💡 Smart Tips: Personalized suggestions\n"
        response += "• 🎯 Eco Score: Your efficiency rating\n"
        response += "• 📈 Bill Comparison: Month-to-month analysis\n"
        response += "• 📚 Knowledge Base: Learn about electricity\n"
        response += "• 🎪 Goal Tracker: Set and track savings goals\n\n"
        response += "💬 **Just type your question above and I'll help!**"
        
        return self._reply(response, ['How do I reduce my bill?', 'Why is my usage high?', 'Show bill details', 'AC tips'])
    
    def _answer_default(self, message=None):
        """Default response"""
        return (
            "👋 **I didn't quite understand that.**\n\n"
            "Try asking:\n"
            "• \"How to reduce my bill?\"\n"
            "• \"Why is my usage high?\"\n"
            "• \"AC tips\"\n"
            "• \"EV charging guide\"\n"
            "• \"Energy saving tips\"\n"
            "• \"What can you do?\"\n\n"
            "Or just describe your energy question naturally! 😊"
        ), self._default_replies()
