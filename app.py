from flask import Flask, render_template, request, jsonify, session
from model import predict_bill_ml
from database import *
# Replace old chatbot with ML pipeline
from energy.chatbot_engine import EnergyAIChatbot
from datetime import datetime
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key_here_change_in_production'

# Initialize database
init_db()


APPLIANCE_CATALOG = {
    'fan': {
        'label': 'Fan',
        'power_watts': 75,
        'default_count': 3,
        'default_hours': 10,
        'category': 'Cooling',
        'note': 'Typical ceiling fan load',
    },
    'ac': {
        'label': 'AC',
        'power_watts': 1500,
        'default_count': 1,
        'default_hours': 6,
        'category': 'Cooling',
        'note': '1.5 ton split AC average load',
    },
    'fridge': {
        'label': 'Fridge',
        'power_watts': 150,
        'default_count': 1,
        'default_hours': 24,
        'category': 'Kitchen',
        'note': 'Runs through compressor cycles all day',
    },
    'tv': {
        'label': 'TV',
        'power_watts': 100,
        'default_count': 1,
        'default_hours': 4,
        'category': 'Entertainment',
        'note': 'LED TV average usage',
    },
    'induction': {
        'label': 'Induction',
        'power_watts': 1800,
        'default_count': 1,
        'default_hours': 2,
        'category': 'Kitchen',
        'note': 'High-power cooking appliance',
    },
    'ev': {
        'label': 'EV Charger',
        'power_watts': 3300,
        'default_count': 1,
        'default_hours': 2,
        'category': 'Transport',
        'note': 'Best used during off-peak hours',
    },
    'ups': {
        'label': 'UPS / Inverter',
        'power_watts': 900,
        'default_count': 1,
        'default_hours': 4,
        'category': 'Backup',
        'note': 'Includes 15% backup loss overhead',
        'loss_rate': 0.15,
    },
    'lights': {
        'label': 'Lights',
        'power_watts': 15,
        'default_count': 8,
        'default_hours': 6,
        'category': 'Lighting',
        'note': 'Assumes LED lighting',
    },
}

EDUCATION_ITEMS = [
    {
        'title': 'What is a unit?',
        'content': '1 unit means 1 kilowatt-hour (kWh). If a 1000W appliance runs for 1 hour, it uses 1 unit.',
    },
    {
        'title': 'How appliances consume electricity',
        'content': 'Power in watts, time in hours, and quantity of appliances together determine total monthly units.',
    },
    {
        'title': 'Why UPS needs adjustment',
        'content': 'During backup, UPS and inverter systems lose some energy. We add a realistic 15% overhead for accuracy.',
    },
    {
        'title': 'How to reduce usage',
        'content': 'Use AC at 24°C, shift EV charging to off-peak hours, and avoid unnecessary standby loads.',
    },
]

EMERGENCY_SUPPORT = {
    'electricity_board': 'Local Electricity Board / Distribution Office',
    'helplines': [
        {'label': 'National Power Helpline', 'number': '1912', 'note': 'Report outages and supply issues'},
        {'label': 'Consumer Grievance', 'number': '1912 / Local Board', 'note': 'Raise billing or meter complaints'},
        {'label': 'Emergency Services', 'number': '112', 'note': 'Use only when there is immediate danger'},
    ],
    'outage_steps': [
        'Check your main switch, MCB, and nearby homes to confirm the outage.',
        'Report the issue to your electricity board helpline with your consumer number.',
        'Unplug sensitive devices to avoid surge damage when power returns.',
        'If there is a burning smell or sparks, switch off mains and contact an electrician immediately.',
    ],
    'billing_steps': [
        'Compare the current bill with your last bill and meter reading.',
        'Check for meter reading date, tariff slab, and fixed charges.',
        'If the bill seems unusually high, contact customer care and request a recheck.',
    ],
}

# ==================== ELECTRICITY BILLING ====================

def calculate_bill(units):
    """Calculate electricity bill based on slab system"""
    if units <= 100:
        return units * 3
    elif units <= 200:
        return (100 * 3) + (units - 100) * 5
    elif units <= 500:
        return (100 * 3) + (100 * 5) + (units - 200) * 7
    else:
        return (100 * 3) + (100 * 5) + (300 * 7) + (units - 500) * 10


def _coerce_int(value, default=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _coerce_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def get_appliance_catalog():
    """Return the built-in appliance catalog."""
    return APPLIANCE_CATALOG


def build_default_appliance_items():
    """Create default appliance inputs from the catalog."""
    items = []
    for appliance_id, meta in APPLIANCE_CATALOG.items():
        items.append({
            'appliance_id': appliance_id,
            'name': meta['label'],
            'count': meta['default_count'],
            'hours': meta['default_hours'],
            'power_watts': meta['power_watts'],
            'use_default': True,
        })
    return items


def normalize_appliance_items(payload):
    """Convert form or JSON payload into a unified appliance item list."""
    if not payload:
        return build_default_appliance_items()

    raw_items = payload.get('appliances') or payload.get('appliances_json')
    smart_defaults = str(payload.get('smart_defaults', 'false')).lower() in {'1', 'true', 'yes', 'on'}

    if isinstance(raw_items, str) and raw_items.strip():
        try:
            raw_items = json.loads(raw_items)
        except json.JSONDecodeError:
            raw_items = None

    items = []
    if isinstance(raw_items, list) and raw_items:
        for item in raw_items:
            if isinstance(item, dict):
                item = dict(item)
                item['use_default'] = smart_defaults or item.get('use_default', False)
                items.append(item)

    if items:
        return items

    legacy_map = {
        'fan': 'fan',
        'ac': 'ac',
        'fridge': 'fridge',
        'tv': 'tv',
        'induction': 'induction',
        'ev': 'ev',
        'ups': 'ups',
        'lights': 'lights',
    }

    fallback_items = []
    for appliance_id, meta in APPLIANCE_CATALOG.items():
        count = _coerce_int(payload.get(f'{appliance_id}_count'), meta['default_count'])
        hours = _coerce_float(payload.get(f'{appliance_id}_hours'), meta['default_hours'])
        if smart_defaults:
            count = meta['default_count']
            hours = meta['default_hours']
        fallback_items.append({
            'appliance_id': legacy_map.get(appliance_id, appliance_id),
            'name': meta['label'],
            'count': count,
            'hours': hours,
            'power_watts': meta['power_watts'],
            'use_default': smart_defaults,
        })

    return fallback_items


def calculate_appliance_breakdown(appliance_items):
    """Calculate monthly consumption from appliance inputs."""
    breakdown = []
    monthly_total = 0.0
    daily_total = 0.0
    backup_loss_units = 0.0

    for item in appliance_items:
        appliance_id = str(item.get('appliance_id') or item.get('id') or '').strip().lower()
        custom_name = str(item.get('name') or item.get('label') or 'Custom Appliance').strip()
        meta = APPLIANCE_CATALOG.get(appliance_id)

        if meta:
            name = meta['label']
            power_watts = _coerce_float(item.get('power_watts'), meta['power_watts'])
            default_count = meta['default_count']
            default_hours = meta['default_hours']
            loss_rate = meta.get('loss_rate', 0.0)
            note = meta.get('note', '')
        else:
            name = custom_name
            power_watts = _coerce_float(item.get('power_watts'), 0)
            default_count = 1
            default_hours = 1
            loss_rate = 0.0
            note = 'Custom appliance entered by the user'

        use_default = str(item.get('use_default', False)).lower() in {'1', 'true', 'yes', 'on'}
        count = _coerce_int(item.get('count'), default_count if use_default else 1)
        hours = _coerce_float(item.get('hours'), default_hours if use_default else default_hours)

        if count <= 0:
            continue

        power_kw = power_watts / 1000.0
        daily_units = count * power_kw * hours
        if appliance_id == 'ups' and loss_rate:
            extra_loss = daily_units * loss_rate
            daily_units += extra_loss
            backup_loss_units += extra_loss * 30

        monthly_units = daily_units * 30
        daily_total += daily_units
        monthly_total += monthly_units

        breakdown.append({
            'appliance_id': appliance_id or 'custom',
            'name': name,
            'count': count,
            'hours': round(hours, 2),
            'power_watts': round(power_watts, 2),
            'daily_units': round(daily_units, 2),
            'monthly_units': round(monthly_units, 2),
            'note': note,
            'source': 'catalog' if meta else 'custom',
            'is_default': use_default,
        })

    breakdown.sort(key=lambda entry: entry['monthly_units'], reverse=True)
    for entry in breakdown:
        entry['share_percent'] = round((entry['monthly_units'] / monthly_total) * 100, 1) if monthly_total else 0

    return {
        'breakdown': breakdown,
        'daily_units': round(daily_total, 2),
        'monthly_units': round(monthly_total, 2),
        'backup_loss_units': round(backup_loss_units, 2),
    }


def build_transparency_lines(breakdown):
    """Return human-readable calculation explanations."""
    lines = []
    for item in breakdown:
        lines.append(
            f"{item['name']} uses ~{item['monthly_units']:.1f} units/month ({item['share_percent']:.0f}% of total)"
        )
    return lines


# ==================== ECO SCORE & INSIGHTS ====================

def calculate_eco_score(units):
    """Calculate eco efficiency score (0-100)"""
    if units <= 100:
        return 95
    elif units <= 150:
        return 85
    elif units <= 200:
        return 75
    elif units <= 300:
        return 60
    elif units <= 400:
        return 40
    else:
        return 20

def get_eco_label(score):
    """Get eco efficiency label"""
    if score >= 80:
        return "Excellent", "🟢"
    elif score >= 60:
        return "Good", "🟡"
    else:
        return "Needs Improvement", "🔴"

def generate_ai_insights(units, data, monthly_stats):
    """Generate AI insights about usage patterns"""
    insights = []
    
    # Insight 1: Top consumer
    breakdown = data.get('appliance_breakdown') or []
    if breakdown:
        top_app = breakdown[0]
        insights.append(f"🔌 **{top_app['name']} is your top consumer** ({top_app['monthly_units']:.0f} units/month)")
    else:
        appliances = {
            'ac': (int(data.get('ac', 0)), 1.5 * 6 * 30),
            'ev': (int(data.get('ev', 0)), 3.3 * 2 * 30),
            'induction': (int(data.get('induction', 0)), 1.8 * 2 * 30),
            'fridge': (int(data.get('fridge', 0)), 0.15 * 24 * 30),
        }
        top_app = max([(name, count * consumption) for name, (count, consumption) in appliances.items()], 
                      key=lambda x: x[1])
        if top_app[1] > 0:
            insights.append(f"🔌 **{top_app[0].upper()} is your top consumer** ({top_app[1]:.0f} units/month)")
    
    # Insight 2: Savings potential
    if units > 300:
        savings_percent = ((units - 250) / units * 100) if units > 0 else 0
        insights.append(f"💰 **Potential savings: {savings_percent:.0f}%** by optimizing usage to 250 units/month")
    elif units > 200:
        insights.append("✅ **Your usage is moderate.** Focus on AC optimization for 15-20% savings")
    else:
        insights.append("🌟 **Great efficiency!** Maintain current habits and share tips with neighbors")
    
    # Insight 3: Pattern analysis
    if int(data.get('ev', 0)) > 0:
        insights.append("⚡ **EV charging tip:** Use off-peak hours (10 PM - 6 AM) to save 30-50%")
    
    if int(data.get('ac', 0)) > 0:
        insights.append("❄️ **AC optimization:** Increasing temp by 1°C saves ₹20-30/month")
    
    # Insight 4: Bill trajectory
    if monthly_stats and monthly_stats.get('percent_change', 0) > 10:
        insights.append(f"📈 **Alert:** Your bill increased by {monthly_stats['percent_change']}% from last month")
    elif monthly_stats and monthly_stats.get('percent_change', 0) < -5:
        insights.append(f"📉 **Great job!** Your bill decreased by {abs(monthly_stats['percent_change'])}%")
    
    return insights


def generate_personalized_tips(units, data):
    """Generate specific, actionable tips with savings amounts"""
    tips = []
    
    # AC tips
    if int(data.get('ac', 0)) > 0:
        tips.append({
            'icon': '❄️',
            'title': 'AC Temperature Optimization',
            'description': 'Reduce AC temp by 2°C and use sleep mode nights',
            'savings': '₹100-150/month',
            'level': 'High Impact'
        })
    
    # EV tips
    if int(data.get('ev', 0)) > 0:
        tips.append({
            'icon': '🔌',
            'title': 'Off-Peak EV Charging',
            'description': 'Charge between 10 PM - 6 AM for 40% bill reduction',
            'savings': '₹300-400/month',
            'level': 'High Impact'
        })
    
    # Induction tips
    if int(data.get('induction', 0)) > 0:
        tips.append({
            'icon': '🍳',
            'title': 'Smart Cooking Habits',
            'description': 'Use pressure cooker & keep lids on pans',
            'savings': '₹40-60/month',
            'level': 'Medium Impact'
        })
    
    # General tips
    tips.append({
        'icon': '💡',
        'title': 'LED Bulb Upgrade',
        'description': 'Replace all incandescent & CFL with LED',
        'savings': '₹50-80/month',
        'level': 'Medium Impact'
    })
    
    tips.append({
        'icon': '⭐',
        'title': '5-Star Appliances',
        'description': 'Upgrade to energy-efficient appliances',
        'savings': '₹100-200/month',
        'level': 'Long-term'
    })
    
    return tips


def build_support_payload():
    """Build education and emergency support data for the UI."""
    return {
        'education': EDUCATION_ITEMS,
        'emergency': EMERGENCY_SUPPORT,
        'catalog': [
            {
                'id': appliance_id,
                **meta,
            }
            for appliance_id, meta in APPLIANCE_CATALOG.items()
        ],
    }


# ==================== ROUTES ====================

@app.route('/')
def index():
    """Main dashboard"""
    user_id = get_or_create_user()
    
    today_usage, today_bill = get_today_usage(user_id)
    weekly_data = get_weekly_usage(user_id)
    monthly_units, monthly_bill = get_monthly_usage(user_id)
    monthly_stats = get_last_month_comparison(user_id)
    user_profile = get_user_profile(user_id)
    
    # Weekly chart data
    weekly_dates = []
    weekly_units = []
    if weekly_data:
        for date, units, bill in weekly_data:
            weekly_dates.append(date[-5:])  # MM-DD
            weekly_units.append(units)
    
    context = {
        'user_id': user_id,
        'today_usage': today_usage,
        'today_bill': today_bill,
        'monthly_units': monthly_units,
        'monthly_bill': monthly_bill,
        'monthly_stats': monthly_stats,
        'user_profile': user_profile,
        'weekly_dates': json.dumps(weekly_dates),
        'weekly_units': json.dumps(weekly_units),
    }
    
    return render_template('dashboard.html', **context)


@app.route('/api/calculate', methods=['POST'])
def calculate():
    """Calculate bill and save usage"""
    user_id = get_or_create_user()
    
    units_input = request.form.get('units')
    smart_defaults = str(request.form.get('smart_defaults', 'false')).lower() in {'1', 'true', 'yes', 'on'}

    appliance_items = normalize_appliance_items({
        'appliances_json': request.form.get('appliances_json'),
        'smart_defaults': smart_defaults,
        'fan_count': request.form.get('fan_count'),
        'fan_hours': request.form.get('fan_hours'),
        'ac_count': request.form.get('ac_count'),
        'ac_hours': request.form.get('ac_hours'),
        'fridge_count': request.form.get('fridge_count'),
        'fridge_hours': request.form.get('fridge_hours'),
        'tv_count': request.form.get('tv_count'),
        'tv_hours': request.form.get('tv_hours'),
        'induction_count': request.form.get('induction_count'),
        'induction_hours': request.form.get('induction_hours'),
        'ev_count': request.form.get('ev_count'),
        'ev_hours': request.form.get('ev_hours'),
        'ups_count': request.form.get('ups_count'),
        'ups_hours': request.form.get('ups_hours'),
        'lights_count': request.form.get('lights_count'),
        'lights_hours': request.form.get('lights_hours'),
    })

    legacy_data = {appliance_id: 0 for appliance_id in APPLIANCE_CATALOG}

    for item in appliance_items:
        appliance_id = str(item.get('appliance_id') or '').lower()
        if appliance_id in legacy_data:
            legacy_data[appliance_id] = _coerce_int(item.get('count'), 0)

    if units_input:
        units = float(units_input)
        appliance_breakdown = calculate_appliance_breakdown(appliance_items)
        estimated = False
    else:
        appliance_breakdown = calculate_appliance_breakdown(appliance_items)
        units = appliance_breakdown['monthly_units']
        estimated = True

    calculation_summary = build_transparency_lines(appliance_breakdown['breakdown'])
    if appliance_breakdown['backup_loss_units']:
        calculation_summary.append(f"UPS loss overhead adds ~{appliance_breakdown['backup_loss_units']:.1f} units/month")
    
    # Calculate bill
    bill = calculate_bill(units)
    predicted = predict_bill_ml(units)
    
    # Calculate eco score
    eco_score = calculate_eco_score(units)
    eco_label, eco_icon = get_eco_label(eco_score)
    
    # Get insights
    monthly_stats = get_last_month_comparison(user_id)
    payload_for_insights = dict(legacy_data)
    payload_for_insights['appliance_breakdown'] = appliance_breakdown['breakdown']
    insights = generate_ai_insights(units, payload_for_insights, monthly_stats)
    
    # Get personalized tips
    tips = generate_personalized_tips(units, legacy_data)

    top_appliance = appliance_breakdown['breakdown'][0] if appliance_breakdown['breakdown'] else None
    custom_appliances = [item for item in appliance_items if str(item.get('appliance_id', '')).lower() not in APPLIANCE_CATALOG]
    
    # Save to database
    save_daily_usage(user_id, units, bill, {
        'legacy_counts': legacy_data,
        'appliance_items': appliance_items,
        'appliance_breakdown': appliance_breakdown['breakdown'],
        'custom_appliances': custom_appliances,
        'smart_defaults': smart_defaults,
    })
    
    current_monthly_units, current_monthly_bill = get_monthly_usage(user_id)

    response = {
        'success': True,
        'units': round(units, 2),
        'bill': round(bill, 2),
        'predicted': predicted,
        'estimated': estimated,
        'eco_score': eco_score,
        'eco_label': eco_label,
        'eco_icon': eco_icon,
        'insights': insights,
        'tips': tips,
        'appliance_breakdown': appliance_breakdown['breakdown'],
        'calculation_summary': calculation_summary,
        'top_appliance': top_appliance,
        'backup_loss_units': appliance_breakdown['backup_loss_units'],
        'appliance_catalog': [
            {'id': appliance_id, **meta}
            for appliance_id, meta in APPLIANCE_CATALOG.items()
        ],
        'education_items': EDUCATION_ITEMS,
        'emergency_support': EMERGENCY_SUPPORT,
        'monthly_units': round(current_monthly_units, 2),
        'monthly_bill': round(current_monthly_bill, 2),
    }
    
    return jsonify(response)


@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    """Chatbot API endpoint using new ML Engine"""
    user_id = get_or_create_user()
    payload = request.get_json(silent=True) or {}
    message = str(payload.get('message', '')).strip()

    if not message:
        return jsonify({
            'success': False,
            'response': 'Please type a question so I can help.',
            'quick_replies': [
                'How do I reduce my bill?',
                'Why is my usage high?',
                'AC tips',
            ]
        }), 400

    try:
        bot = EnergyAIChatbot()
        
        # Gather user stats to pass to ML engine
        today_usage, today_bill = get_today_usage(user_id)
        monthly_units, monthly_bill = get_monthly_usage(user_id)
        monthly_stats = get_last_month_comparison(user_id)
        
        user_stats = {
            'user_kwh': round(monthly_units, 2),
            'user_cost': round(monthly_bill, 2),
            'score': 85 if monthly_units < 200 else (65 if monthly_units < 400 else 40),
            'comparison': "20% below average" if monthly_units < 110 else "above average"
        }
        
        response_data = bot.get_response(message, user_stats)
        
        return jsonify({
            'success': True,
            'response': response_data['reply'],
            'intent': response_data['intent'],
            'confidence': response_data['confidence'],
            'quick_replies': [
                'Reduce my bill', 'Show my usage', 'AC tips', 'EV tips'
            ]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'response': f"ML Model Error: {str(e)}",
            'quick_replies': []
        }), 500


@app.route('/api/user-profile', methods=['POST'])
def update_profile():
    """Update user profile"""
    user_id = get_or_create_user()
    
    family_size = request.json.get('family_size')
    property_type = request.json.get('property_type')
    
    update_user_profile(user_id, family_size, property_type)
    
    return jsonify({
        'success': True,
        'message': 'Profile updated successfully'
    })


@app.route('/api/set-goal', methods=['POST'])
def set_goal():
    """Set bill reduction goal"""
    user_id = get_or_create_user()
    
    goal_amount = request.json.get('goal_amount')
    
    set_bill_goal(user_id, goal_amount)
    
    return jsonify({
        'success': True,
        'message': f'Goal set: Reduce bill by ₹{goal_amount}'
    })


@app.route('/api/daily-tracking')
def daily_tracking():
    """Get daily tracking data"""
    user_id = get_or_create_user()
    
    weekly_data = get_weekly_usage(user_id)
    monthly_units, monthly_bill = get_monthly_usage(user_id)
    monthly_stats = get_last_month_comparison(user_id)
    
    tracking_data = {
        'weekly': [
            {'date': d[0], 'units': d[1], 'bill': d[2]}
            for d in weekly_data
        ],
        'monthly': {
            'units': monthly_units,
            'bill': monthly_bill,
        },
        'comparison': monthly_stats
    }
    
    return jsonify(tracking_data)


@app.route('/knowledge')
def knowledge():
    """Knowledge base section"""
    knowledge_items = EDUCATION_ITEMS
    
    return render_template('knowledge.html', items=knowledge_items)


@app.route('/api/reference-data')
def reference_data():
    """Return appliance, education, and emergency reference data."""
    return jsonify(build_support_payload())


@app.route('/api/appliance-catalog')
def appliance_catalog():
    """Return the built-in appliance catalog."""
    return jsonify({'success': True, 'catalog': build_support_payload()['catalog']})


@app.route('/api/emergency-support')
def emergency_support():
    """Return emergency helpline and outage guidance data."""
    return jsonify({'success': True, 'emergency': EMERGENCY_SUPPORT})


@app.route('/model-info')
def model_info():
    """Viva Proof UI for the ML Model."""
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'energy', 'ml_models', 'training_report.json')
    report = None
    intents = []
    if os.path.exists(report_path):
        with open(report_path, 'r') as f:
            report = json.load(f)
            # Find the intent keys (ignore macro/micro avg etc)
            intents = [k for k in report.keys() if k not in ('accuracy', 'macro avg', 'weighted avg', 'overall_accuracy', 'total_examples')]
            
    return render_template('model_info.html', report=report, intents=intents)


if __name__ == '__main__':
    app.run(debug=True)