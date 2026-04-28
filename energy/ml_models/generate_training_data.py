import json
import random

intents_config = {
    "saving_tips": {
        "response_keys": ["saving_tips_general", "saving_tips_ac", "saving_tips_lights", "saving_tips_standby", "saving_tips_fridge"],
        "templates": [
            "how do i lower my electricity bill", "bijli ka bill kam kaise kare", "ways to cut power usage", 
            "saving tips", "tips to save energy", "reduce my bill", "how can i save money on electricity",
            "electricity saving ideas", "reduce energy consumption", "how to minimize power usage", 
            "energy efficiency advice", "bill cut off", "lower my bill please", "help me reduce bill"
        ],
        "modifiers": ["", " please", "?", " now", " fast"]
    },
    "appliance_advice": {
        "response_keys": ["appliance_ac", "appliance_fridge", "appliance_tv", "appliance_geyser", "appliance_washing_machine", "appliance_general"],
        "templates": [
            "AC bahut zyada units le raha hai", "how much power does ac use", "is fridge consuming too much",
            "geyser running time", "appliance power consumption", "which appliance is the most expensive",
            "does the tv take a lot of power", "washing machine energy usage", "ac power details",
            "fridge power tips", "how to optimise ac", "what temp for ac", "appliance electricity cost", "how to run geyser efficiently"
        ],
        "modifiers": ["", "?", " tell me", " info"]
    },
    "personal_stats": {
        "response_keys": ["personal_stats"],
        "templates": [
            "my bill?", "show my usage", "what is my bill this month", "my electricity stats",
            "mera bill kitna hai", "how much did i consume", "tell me my bill",
            "current month bill", "my energy dashboard", "how many units did i use",
            "personal usage data", "what's my score", "my efficiency score", "check my bill"
        ],
        "modifiers": ["", "?", " please", " right now"]
    },
    "billing_info": {
        "response_keys": ["billing_slab", "billing_calculation", "billing_fixed_charge", "billing_general"],
        "templates": [
            "what are the tariff slabs", "how is the bill calculated", "meter reading info",
            "electricity rates", "how much per unit", "cost of one unit", "slab details",
            "bill calculation rules", "fixed charges explained", "what is a tariff",
            "per kwh price", "unit price", "rate per unit", "explain the bill"
        ],
        "modifiers": ["", " please", "?", " info"]
    },
    "iea_benchmark": {
        "response_keys": ["iea_benchmark_info"],
        "templates": [
            "how does india compare", "national averages", "iea statistics",
            "what is the average household usage", "compare to average", "iea benchmark",
            "how am i compared to national average", "indian average electricity consumption",
            "global average vs me", "iea data", "what does iea say", "average kwh in india"
        ],
        "modifiers": ["", " please", "?", " stats"]
    },
    "renewables": {
        "response_keys": ["renewables_solar", "renewables_net_metering"],
        "templates": [
            "solar panels", "can i install solar", "net metering explained",
            "green energy", "solar power tips", "how does solar work",
            "renewable energy options", "solar installation", "benefits of solar",
            "is solar worth it", "subsidy for solar", "green electricity"
        ],
        "modifiers": ["", "?", " cost", " info"]
    },
    "prediction_query": {
        "response_keys": ["prediction_general"],
        "templates": [
            "forecast my bill", "predict future usage", "what will my bill be next month",
            "future forecast", "prediction of electricity", "estimate my bill",
            "bill projection", "how much to expect next month", "forecast usage",
            "predict my consumption", "next month bill estimate"
        ],
        "modifiers": ["", "?", " please", " for me"]
    },
    "smalltalk": {
        "response_keys": ["smalltalk_greeting", "smalltalk_thanks", "smalltalk_help"],
        "templates": [
            "hello", "hi there", "hey", "good morning", "thanks", "thank you",
            "what can you do", "help me", "who are you", "what are your features",
            "namaste", "hi", "how are you", "what do you do", "are you an ai"
        ],
        "modifiers": ["", ".", "!"]
    }
}

training_data = []

for intent, data in intents_config.items():
    count = 0
    while count < 40: # Generate at least 40 per intent (320 total)
        for template in data['templates']:
            for modifier in random.sample(data['modifiers'], k=min(2, len(data['modifiers']))):
                phrase = f"{template}{modifier}"
                training_data.append({
                    "text": phrase,
                    "intent": intent,
                    "response_key": random.choice(data['response_keys'])
                })
                count += 1
                if count >= 40:
                    break
            if count >= 40:
                break

# Append Source Credit
# "Curated for EnergyAI training, benchmarked against IEA Energy Statistics Data Browser (CC BY 4.0)"
with open('c:/Users/sumit/Documents/codes/Essentials/Smart-Electricity-Bill-Optimizer/energy/ml_models/training_data.json', 'w') as f:
    json.dump(training_data, f, indent=2)

print(f"Generated {len(training_data)} training examples.")
