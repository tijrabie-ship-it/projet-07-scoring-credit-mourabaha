import joblib
import pandas as pd
from flask import Flask, request, jsonify, render_template
import logging

app = Flask(__name__)

# Load the model
try:
    model = joblib.load('xgboost_mourabaha_final.pkl')
    # Expected feature order based on inspection
    FEATURES = [
        'age_client', 'monthly_salary', 'financing_amount', 'monthly_installment',
        'employment_years', 'nb_children', 'gender', 'education_level',
        'family_status', 'murabaha_type', 'margin_rate', 'contract_duration_months',
        'collateral_value', 'contract_year', 'ead', 'dti', 'ltv',
        'collateral_coverage', 'ead_ratio', 'installment_to_amount'
    ]
except Exception as e:
    logging.error(f"Error loading model: {e}")
    model = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'status': 'error', 'message': 'The model failed to load.'})

    try:
        # Extract features from form (only the basic ones)
        FORM_FEATURES = [
            'age_client', 'monthly_salary', 'financing_amount', 'monthly_installment',
            'employment_years', 'nb_children', 'gender', 'education_level',
            'family_status', 'murabaha_type', 'margin_rate', 'contract_duration_months',
            'collateral_value', 'contract_year'
        ]
        
        data = {}
        for feature in FORM_FEATURES:
            val = request.form.get(feature)
            if val is None:
                return jsonify({'status': 'error', 'message': f'Missing field: {feature}'})
            
            # Convert to numeric if it's a number
            if feature in ['gender', 'education_level', 'family_status', 'murabaha_type']:
                data[feature] = val
            else:
                if val.strip() == '':
                    return jsonify({'status': 'error', 'message': f'يرجى التأكد من إدخال جميع البيانات (الحقل المفقود: {feature})'})
                try:
                    data[feature] = float(val)
                except ValueError:
                    return jsonify({'status': 'error', 'message': f'قيمة غير صالحة في الحقل: {feature}'})

        # Feature Engineering: Auto-calculate derived features
        monthly_salary = data['monthly_salary']
        financing_amount = data['financing_amount']
        monthly_installment = data['monthly_installment']
        collateral_value = data['collateral_value']
        
        data['dti'] = monthly_installment / monthly_salary if monthly_salary > 0 else 0
        data['ltv'] = financing_amount / collateral_value if collateral_value > 0 else 0
        data['ead'] = financing_amount * 0.8  # Defaulting EAD to 80% of financing amount
        data['ead_ratio'] = data['ead'] / financing_amount if financing_amount > 0 else 0
        data['collateral_coverage'] = collateral_value / financing_amount if financing_amount > 0 else 0
        data['installment_to_amount'] = monthly_installment / financing_amount if financing_amount > 0 else 0

        # Create DataFrame for prediction
        df = pd.DataFrame([data])
        
        # Ensure order
        df = df[FEATURES]

        # Business Rule: Reject if age at end of contract > 75
        age_at_end = data['age_client'] + (data['contract_duration_months'] / 12.0)
        if age_at_end > 75:
            prediction = 1
            probability = 0.99
        else:
            # Predict using the ML Model
            prediction = model.predict(df)[0]
            if hasattr(model, 'predict_proba'):
                probability = model.predict_proba(df)[0][1] # Probability of default
            else:
                probability = float(prediction)

            # --- Expert Risk Calibration Layer (طبقة تعديل المخاطر) ---
            age = data['age_client']
            employment_years = data['employment_years']

            # 1. Age rules
            if age < 20:
                probability += 0.40  # +40% risk for very young clients
            elif age > 55:
                probability += (age - 55) * 0.025  # +2.5% risk for each year over 55

            # 2. Employment rules
            if employment_years < 1:
                probability += 0.30  # +30% risk for less than 1 year of work
            elif employment_years < 3:
                probability += 0.15  # +15% risk for less than 3 years
            elif employment_years >= 10:
                probability -= 0.05  # -5% risk (Bonus) for stable employment > 10 years

            # Bound the probability between 0 and 0.98 (leave 0.99 for hard rejections)
            probability = max(0.0, min(0.98, probability))

            # Re-evaluate final decision based on new calibrated probability
            prediction = 1 if probability >= 0.5 else 0

        return jsonify({
            'status': 'success',
            'prediction': int(prediction),
            'probability': float(probability)
        })

    except Exception as e:
        logging.error(f"Prediction error: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
