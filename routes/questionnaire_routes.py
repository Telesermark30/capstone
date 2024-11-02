# routes/questionnaire_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from flask_login import login_required
from models import SGAResult, StampResult, Patient, db
from models import MnaResult
from flask import Flask, flash, render_template, redirect, url_for, session, request


questionnaire_bp = Blueprint('questionnaire', __name__)

@questionnaire_bp.route('/sga_questionnaire/<int:step>', methods=['GET', 'POST'])
@login_required
def sga_questionnaire(step):
    # Define the questions for each step of the SGA tool (in English and Cebuano)
    sga_questions = {
        'en': {
            1: {
                'question': "Have you had any change in weight over the past six months?",
                'options': [
                    {"text": "Significant weight loss", "score": 3},
                    {"text": "Moderate weight loss", "score": 2},
                    {"text": "Minimal or no weight loss", "score": 0}
                ]
            },
            2: {
                'question': "Have you experienced any change in food intake?",
                'options': [
                    {"text": "Significant decrease in food intake", "score": 3},
                    {"text": "Moderate decrease in food intake", "score": 2},
                    {"text": "No change in food intake", "score": 0}
                ]
            },
            3: {
                'question': "Have you experienced any gastrointestinal symptoms persisting for more than 2 weeks?",
                'options': [
                    {"text": "Significant symptoms", "score": 3},
                    {"text": "Mild symptoms", "score": 2},
                    {"text": "No symptoms", "score": 0}
                ]
            },
            4: {
                'question': "How would you describe your functional capacity (nutrition-related)?",
                'options': [
                    {"text": "Severely limited (bedridden)", "score": 3},
                    {"text": "Moderately limited", "score": 2},
                    {"text": "Normal", "score": 0}
                ]
            },
            5: {
                'question': "Do you have any conditions or illnesses affecting your nutritional needs?",
                'options': [
                    {"text": "Severe condition", "score": 3},
                    {"text": "Mild condition", "score": 2},
                    {"text": "No conditions", "score": 0}
                ]
            },
            6: {
                'question': "Have you noticed any muscle loss?",
                'options': [
                    {"text": "Significant muscle loss", "score": 3},
                    {"text": "Mild muscle loss", "score": 2},
                    {"text": "No muscle loss", "score": 0}
                ]
            },
            7: {
                'question': "Have you experienced any fat loss?",
                'options': [
                    {"text": "Significant fat loss", "score": 3},
                    {"text": "Mild fat loss", "score": 2},
                    {"text": "No fat loss", "score": 0}
                ]
            },
            8: {
                'question': "Do you have any edema (nutrition-related)?",
                'options': [
                    {"text": "Severe edema", "score": 3},
                    {"text": "Mild edema", "score": 2},
                    {"text": "No edema", "score": 0}
                ]
            }
        },
        'ceb': {
            1: {
                'question': "Aduna ba kay mga pagbag-o sa timbang sulod sa miaging unom ka bulan?",
                'options': [
                    {"text": "Grabe nga pagkawala sa timbang", "score": 3},
                    {"text": "Katamtamang pagkawala sa timbang", "score": 2},
                    {"text": "Gamay ra o wala'y pagkawala sa timbang", "score": 0}
                ]
            },
            2: {
                'question': "Aduna ba kay mga pagbag-o sa pagkaon?",
                'options': [
                    {"text": "Grabe nga pagkunhod sa pagkaon", "score": 3},
                    {"text": "Katamtamang pagkunhod sa pagkaon", "score": 2},
                    {"text": "Walay pagbag-o sa pagkaon", "score": 0}
                ]
            },
            3: {
                'question': "Nakasinati ba ka og mga sintomas sa tiyan nga nagpadayon sulod sa labaw sa 2 ka semana?",
                'options': [
                    {"text": "Grabe nga mga sintomas", "score": 3},
                    {"text": "Gamayang mga sintomas", "score": 2},
                    {"text": "Walay sintomas", "score": 0}
                ]
            },
            4: {
                'question': "Giunsa nimo pag-describe ang imong kapasidad sa kalihokan (may kalabutan sa nutrisyon)?",
                'options': [
                    {"text": "Grabe nga limitasyon (nakahigda ra)", "score": 3},
                    {"text": "Katamtamang limitasyon", "score": 2},
                    {"text": "Normal", "score": 0}
                ]
            },
            5: {
                'question': "Aduna ba kay mga kondisyon o sakit nga nakaapekto sa imong panginahanglan sa nutrisyon?",
                'options': [
                    {"text": "Grabe nga kondisyon", "score": 3},
                    {"text": "Katamtamang kondisyon", "score": 2},
                    {"text": "Walay kondisyon", "score": 0}
                ]
            },
            6: {
                'question': "Nakabantay ba ka og pagkawala sa kaunuran?",
                'options': [
                    {"text": "Grabe nga pagkawala sa kaunuran", "score": 3},
                    {"text": "Gamayang pagkawala sa kaunuran", "score": 2},
                    {"text": "Walay pagkawala sa kaunuran", "score": 0}
                ]
            },
            7: {
                'question': "Nakasinati ba ka og pagkawala sa tambok?",
                'options': [
                    {"text": "Grabe nga pagkawala sa tambok", "score": 3},
                    {"text": "Gamayang pagkawala sa tambok", "score": 2},
                    {"text": "Walay pagkawala sa tambok", "score": 0}
                ]
            },
            8: {
                'question': "Aduna ba kay edema (may kalabutan sa nutrisyon)?",
                'options': [
                    {"text": "Grabe nga edema", "score": 3},
                    {"text": "Gamayang edema", "score": 2},
                    {"text": "Walay edema", "score": 0}
                ]
            }
        }
    }

    # Determine the current language from session
    language = session.get('language', 'en')
    current_question = sga_questions.get(language, {}).get(step)

    if not current_question:
        return "Invalid step number", 400

    if request.method == 'POST':
        selected_option = request.form.get('answer')
        if selected_option is not None:
            score = int(selected_option)

            # Save the score in the session
            if 'sga_scores' not in session:
                session['sga_scores'] = []
            session['sga_scores'].append(score)

            # Redirect to the next step or result page
            if step < len(sga_questions[language]):
                return redirect(url_for('questionnaire.sga_questionnaire', step=step + 1))

            else:
                return redirect(url_for('questionnaire.sga_result'))


    # Render the SGA questionnaire template
    return render_template(
        'sga_questionnaire.html',
        step=step,
        question=current_question['question'],
        options=current_question['options']
    )

#Stamp Questionnaire
@questionnaire_bp.route('/stamp_questionnaire/<int:step>', methods=['GET', 'POST'])
def stamp_questionnaire(step):
    # Define the questions for each step of the STAMP tool in both English and Cebuano
    questions = {
        'en': {
            1: {
                'question': "Does the child have a diagnosis that has any nutritional implications?",
                'options': [
                    {"text": "Definitely", "score": 3},
                    {"text": "Possibly", "score": 2},
                    {"text": "No", "score": 0}
                ]
            },
            2: {
                'question': "What is the child's nutritional intake?",
                'options': [
                    {"text": "None", "score": 3},
                    {"text": "Recently decreased / poor", "score": 2},
                    {"text": "No change / good", "score": 0}
                ]
            },
            3: {
                'question': "Use the centile quick reference tables to determine the child's measurements",
                'options': [
                    {"text": "> 3 centile spaces/≥3 columns apart (or weight < 2nd centile)", "score": 3},
                    {"text": "> 2 centile spaces/= 2 columns apart", "score": 1},
                    {"text": "0 to 1 centile spaces/columns apart", "score": 0}
                ]
            }
        },
        'ceb': {
            1: {
                'question': "Ang bata ba adunay kondisyon nga adunay mga implikasyon sa nutrisyon?",
                'options': [
                    {"text": "Sigurado", "score": 3},
                    {"text": "Posible", "score": 2},
                    {"text": "Wala", "score": 0}
                ]
            },
            2: {
                'question': "Unsa ang nutrisyonal nga intake sa bata?",
                'options': [
                    {"text": "Walay bisan unsa", "score": 3},
                    {"text": "Bag-o lang nahinay / dili maayo", "score": 2},
                    {"text": "Walay kausaban / maayo", "score": 0}
                ]
            },
            3: {
                'question': "Gamit ang mga centile quick reference tables aron mahibal-an ang sukat sa bata",
                'options': [
                    {"text": "> 3 ka centile spaces/≥3 ka columns nga layo (o ang timbang < 2nd centile)", "score": 3},
                    {"text": "> 2 ka centile spaces/ = 2 ka columns nga layo", "score": 1},
                    {"text": "0 hangtod 1 ka centile spaces/columns nga layo", "score": 0}
                ]
            }
        }
    }

    # Determine the current language
    language = session.get('language', 'en')
    current_question = questions.get(language, questions['en']).get(step)

    if request.method == 'POST':
        selected_option = request.form.get('answer')
        if selected_option is not None:
            score = int(selected_option)  # Extract score from the button value

            # Save the score in the session
            if 'stamp_scores' not in session:
                session['stamp_scores'] = []
            session['stamp_scores'].append(score)

            # Redirect to the next step or result page
            if step < 3:
                return redirect(url_for('questionnaire.stamp_questionnaire', step=step + 1))
            else:
                return redirect(url_for('questionnaire.stamp_result'))

    # Render the stamp questionnaire template
    return render_template(
        'stamp_questionnaire.html',
        step=step,
        question=current_question['question'],
        options=current_question['options']
    )



#Stamp result
@questionnaire_bp.route('/stamp_result', methods=['GET'])
def stamp_result():
    scores = session.get('stamp_scores', [])

    if not scores:
        return "Error: No scores found", 400

    total_score = sum(scores)
    
    # Define risk levels and care plans in both languages
    translations = {
        'en': {
            'high_risk': "High risk",
            'medium_risk': "Medium risk",
            'low_risk': "Low risk",
            'care_high': "Take action. Refer to a Dietitian, nutritional support team or consultant. Monitor as per care plan.",
            'care_medium': "Monitor nutritional intake for 3 days. Repeat STAMP screening after 3 days. Amend care plan as required.",
            'care_low': "Continue routine clinical care. Repeat STAMP screening weekly while child is an in-patient. Amend care plan as required."
        },
        'ceb': {
            'high_risk': "Dako nga risgo",
            'medium_risk': "Katamtamang risgo",
            'low_risk': "Gamay nga risgo",
            'care_high': "Pagkuha og aksyon. I-refer sa Dietitian, nutritional support team o consultant. Monitor sama sa plano sa pag-atiman.",
            'care_medium': "Monitor ang nutritional intake sulod sa 3 ka adlaw. Balika ang STAMP screening human sa 3 ka adlaw. Ayuha ang plano sa pag-atiman kung kinahanglan.",
            'care_low': "Padayon sa naandan nga klinikal nga pag-atiman. Balika ang STAMP screening matag semana samtang ang bata naa sa ospital. Ayuha ang plano sa pag-atiman kung kinahanglan."
        }
    }

    language = session.get('language', 'en')
    texts = translations.get(language, translations['en'])

    # Determine risk level and care plan based on score
    if total_score >= 4:
        risk_level = texts['high_risk']
        care_plan = texts['care_high']
    elif 2 <= total_score <= 3:
        risk_level = texts['medium_risk']
        care_plan = texts['care_medium']
    else:
        risk_level = texts['low_risk']
        care_plan = texts['care_low']

    # Save result to the database
    patient_id = session.get('patient_id')
    if patient_id:
        try:
            # Create a new entry in stamp_results
            new_result = StampResult(
                patient_id=patient_id,
                total_score=total_score,
                risk_level=risk_level,
                care_plan=care_plan
            )
            db.session.add(new_result)
            db.session.commit()
        except Exception as e:
            print(f"Database Error: {e}")
            return "Database error occurred", 500

    # Clear the session scores after use
    session.pop('stamp_scores', None)

    return render_template(
        'stamp_result.html',
        total_score=total_score,
        risk_level=risk_level,
        care_plan=care_plan
    )

# Save result
@questionnaire_bp.route('/save_result', methods=['POST'])
@login_required
def save_result():
    try:
        # Get data from the POST request
        score = request.json.get('score')
        status = request.json.get('status')

        print(f"Received score: {score}, status: {status}")

        # Ensure the patient is logged in
        patient_id = session.get('patient_id')
        if not patient_id:
            return jsonify({'error': 'No patient logged in'}), 400

        # Update the patient status in the database
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404

        # Check if an existing MnaResult record exists for the patient
        mna_result = MnaResult.query.filter_by(patient_id=patient.id).first()
        if mna_result:
            mna_result.status = status  # Update status
        else:
            # Create a new record if one doesn't exist
            mna_result = MnaResult(patient_id=patient.id, status=status)
            db.session.add(mna_result)

        # Commit the changes to the database
        db.session.commit()

        return jsonify({'success': True, 'message': 'Result saved successfully'})

    except Exception as e:
        print(f"Error saving result: {str(e)}")
        return jsonify({'error': str(e)}), 500



    except Exception as e:
        print(f"Error saving result: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@questionnaire_bp.route('/select_age_group', methods=['GET', 'POST'])
def select_age_group():
    if request.method == 'POST':
        age_group = request.form['age_group']
        
        # Redirect based on the age group selected
        if age_group == "adolescent":
            session['age_group'] = "adolescent"
            return redirect(url_for('questionnaire.stamp_questionnaire', step=1))
        elif age_group == "adult":
            session['age_group'] = "adult"
            return redirect(url_for('questionnaire.sga_questionnaire', step=1))
        elif age_group == "senior":
            session['age_group'] = "senior"
            return redirect(url_for('questionnaire.nutritional_screening', question_num=1, lang=session.get('language', 'en')))

    language = session.get('language', 'en')
    translations = {
        'en': {'title': 'Select Age Group', 'adolescent': 'Adolescent (13-19 years)', 'adult': 'Adult (20-59 years)', 'senior': 'Senior (60+ years)'},
        'ceb': {'title': 'PILI UG ASA KA NA BAHIN SA EDAD NA SAKOP', 'adolescent': 'Batan-on (13-19 ka tuig)', 'adult': 'Hamtong (20-59 ka tuig)', 'senior': 'Tigulang (60+ ka tuig)'}
    }
    translated_text = translations.get(language, translations['en'])
    return render_template('select_age_group.html', title=translated_text['title'],
                           adolescent=translated_text['adolescent'], adult=translated_text['adult'], senior=translated_text['senior'])


@questionnaire_bp.route('/sga_result', methods=['GET'])
@login_required
def sga_result():
    scores = session.get('sga_scores', [])
    if not scores:
        return "Error: No scores found", 400

    total_score = sum(scores)

    # Define the assessment results based on the total score
    if total_score >= 6:
        assessment = "Severely malnourished"
    elif total_score >= 3:
        assessment = "Moderately malnourished"
    else:
        assessment = "Well nourished"

    # Save the result in the database
    patient_id = session.get('patient_id')
    if patient_id:
        sga_result = SGAResult(patient_id=patient_id, total_score=total_score, assessment=assessment)
        db.session.add(sga_result)
        db.session.commit()

    # Clear the session scores after use
    session.pop('sga_scores', None)

    return render_template('sga_result.html', total_score=total_score, assessment=assessment)

@questionnaire_bp.route('/nutritional_screening/<int:question_num>/<string:lang>', methods=['GET', 'POST'])
def nutritional_screening(question_num, lang):
    # Nutritional questions and options with image paths
    translations = {
        'en': {
            'questions': [
                "Has food intake declined over the past 3 months due to loss of appetite, digestive problems, chewing or swallowing difficulties?",
                "Weight loss during the last 3 months?",
                "Mobility?",
                "Has suffered psychological stress or acute disease in the past 3 months?",
                "Neuropsychological problems?",
                "Body Mass Index (BMI) (weight in kg) / (height in m)^2",
                "Calf circumference (CC) in cm (if BMI not available)"
            ],
            'options': [
                [{"text": "0 = Severe decrease", "image": "/static/images/food1.png"},
                 {"text": "1 = Moderate decrease", "image": "/static/images/food2.png"},
                 {"text": "2 = No decrease", "image": "/static/images/food3.png"}],
                
                [{"text": "0 = Greater than 3 kg", "image": "/static/images/weight1.png"},
                 {"text": "1 = Does not know", "image": "/static/images/weight2.png"},
                 {"text": "2 = 1-3 kg", "image": "/static/images/weight3.png"},
                 {"text": "3 = No weight loss", "image": "/static/images/weight4.png"}],

                [{"text": "0 = Bed/chair bound", "image": "/static/images/mobility1.png"},
                 {"text": "1 = Able to get out but does not go out", "image": "/static/images/mobility2.png"},
                 {"text": "2 = Goes out", "image": "/static/images/mobility3.png"}],

                [{"text": "0 = Yes", "image": "/static/images/stress1.png"},
                 {"text": "2 = No", "image": "/static/images/stress2.png"}],

                [{"text": "0 = Severe dementia or depression", "image": "/static/images/dimentia1.png"},
                 {"text": "1 = Mild dementia", "image": "/static/images/dimentia2.png"},
                 {"text": "2 = No psychological problems", "image": "/static/images/stress2.png"}],

                [{"text": "0 = BMI less than 19", "image": "/static/images/weight8.png"},
                 {"text": "1 = BMI 19 to less than 21", "image": "/static/images/weight6.png"},
                 {"text": "2 = BMI 21 to less than 23", "image": "/static/images/weight7.png"},
                 {"text": "3 = BMI 23 or greater", "image": "/static/images/weight5.png"}],

                [{"text": "0 = CC less than 31", "image": "/static/images/calf2.png"},
                 {"text": "3 = CC 31 or greater", "image": "/static/images/calf1.png"}]
            ]
        },
        'ceb': {
            'questions': [
                "Nag kahinay ba ang imong pagkaon sa miaging tulo ka bulan tungod sa pagkawala sa gana ?, problema sa pagtunaw?, o sa pagka lisod sa pag nga-nga o pagtulon?",
                "Naa bay pag bawas sa imong timbang sa miaging tulo ka bulan?",
                "Kamusta imohang paglihok?",
                "Nakaagum ba ka og psychological nga stress o sakit sa miaging 3 ka bulan?",
                "Aduna ba kay problema sa neurosikolohiya? o sakit bahin sa huna huna?",
                " Body Mass Index (BMI) (timbang sa kg) / (gitas-on sa m)^2",
                "Calf circumference (CC) sa cm (kung ang BMI wala magamit)"
            ],
            'options': [
                [{"text": "0 = Grabe nga pagkunhod", "image": "/static/images/food1.png"},
                 {"text": "1 = Katamtaman nga pagkunhod", "image": "/static/images/food2.png"},
                 {"text": "2 = Wala'y pagkunhod", "image": "/static/images/food3.png"}],

                [{"text": "0 = Mas dako kaysa 3 kg", "image": "/static/images/weight1.png"},
                 {"text": "1 = Wala kahibalo", "image": "/static/images/weight2.png"},
                 {"text": "2 = Na bawasan ug 1-3 kg", "image": "/static/images/weight3.png"},
                 {"text": "3 = Wala'y pagkawala sa timbang", "image": "/static/images/weight4.png"}],

                [{"text": "0 = Higda/lingkuranan ra", "image": "/static/images/mobility1.png"},
                 {"text": "1 = Maka lakaw apan dili mogawas", "image": "/static/images/mobility2.png"},
                 {"text": "2 = Mogawas sa balay", "image": "/static/images/mobility3.png"}],

                [{"text": "0 = Oo", "image": "/static/images/stress1.png"},
                 {"text": "2 = Wala", "image": "/static/images/stress2.png"}],

                [{"text": "0 = Grabe nga dementia o depresyon", "image": "/static/images/dimentia1.png"},
                 {"text": "1 = Huyang nga dementia", "image": "/static/images/dimentia2.png"},
                 {"text": "2 = Wala'y mga problema sa neuropsychological", "image": "/static/images/stress2.png"}],

                [{"text": "0 = BMI ubos sa 19", "image": "/static/images/weight8.png"},
                 {"text": "1 = BMI 19 hangtod ubos sa 21", "image": "/static/images/weight6.png"},
                 {"text": "2 = BMI 21 hangtod ubos sa 23", "image": "/static/images/weight7.png"},
                 {"text": "3 = BMI 23 o labaw pa", "image": "/static/images/weight5.png"}],

                [{"text": "0 = CC ubos sa 31", "image": "/static/images/calf2.png"},
                 {"text": "3 = CC 31 o labaw pa", "image": "/static/images/calf1.png"}]
            ]
        }
    }
  
    # Get the questions and options from the translation dictionary
    translated_questions = translations.get(lang, {}).get('questions', [])
    translated_options = translations.get(lang, {}).get('options', [])

    # Fetch the specific question and its options
    question = translated_questions[question_num - 1]
    options = translated_options[question_num - 1]

    if request.method == 'POST':
        # Initialize session to store answers if not already done
        if 'answers' not in session:
            session['answers'] = {}

        selected_answer = request.form.get('answer')

        # Only store the answer if the question hasn't been answered before
        if selected_answer is not None:
            session['answers'][question_num] = int(selected_answer)  # Ensure it is an integer
            print(f"Answers so far: {session['answers']}")

        # Redirect to the next question if available
        if question_num < len(translated_questions):
            return redirect(url_for('questionnaire.nutritional_screening', question_num=question_num + 1, lang=lang))
        else:
           return redirect(url_for('questionnaire.result', lang=lang))

    # This part renders the template only if it's a GET request (or after POST handling ends).
    return render_template('question.html', question=question, options=options, question_num=question_num, lang=lang)

@questionnaire_bp.route('/result/<string:lang>')
@login_required
def result(lang):
    # Ensure session data is intact
    answers = session.get('answers', {})
    user_info = session.get('user_info', {})
    selected_nutritionist_id = session.get('selected_nutritionist_id')

    if not answers:
        flash("Error: No answers found", "danger")
        return redirect(url_for("questionnaire.sga_questionnaire", step=1))

    # Calculate score and determine status
    score = sum(answers.values())
    if score >= 12:
        status = "Normal nutritional status"
    elif score >= 8:
        status = "At risk of malnutrition"
    else:
        status = "Malnourished"

    translations = {
        'en': {
            "Normal nutritional status": "Normal nutritional status",
            "At risk of malnutrition": "At risk of malnutrition",
            "Malnourished": "Malnourished",
            "consult_message": "Please consult with a nutritionist or dietitian for a more detailed evaluation."
        },
        'ceb': {
            "Normal nutritional status": "Normal nga nutrisyon",
            "At risk of malnutrition": "Delikado nga pagkaon sa kakulangan sa nutrisyon",
            "Malnourished": "Kulang sa nutrisyon",
            "consult_message": "Palihug pangonsulta sa usa ka nutrisyonista o dietitian para sa usa ka detalyadong ebalwasyon."
        }
    }

    # Get the translated status and consult message based on the selected language
    translated_status = translations.get(lang, translations['en']).get(status, status)
    consult_message = translations.get(lang, translations['en']).get("consult_message", "")

    try:
        # Create or update patient records and results in the database
        patient = Patient.query.filter_by(
            first_name=user_info.get('first_name'),
            last_name=user_info.get('last_name'),
            sex=user_info.get('sex'),
            age=int(user_info.get('age', 0)),
            nutritionist_id=selected_nutritionist_id
        ).first()

        if patient:
            mna_result = MnaResult.query.filter_by(patient_id=patient.id).first()
            if mna_result:
                mna_result.status = status
            else:
                db.session.add(MnaResult(patient_id=patient.id, status=status))
        else:
            flash("Error: Missing patient information", "danger")
            return redirect(url_for("patient.create_patient_account"))

        db.session.commit()

        # Clear session data
        session.pop("answers", None)
        session.pop("user_info", None)
        session.pop("selected_nutritionist_id", None)

    except Exception as e:
        db.session.rollback()
        flash(f"Database error: {str(e)}", "danger")
        return redirect(url_for("questionnaire.select_age_group"))

    return render_template('result.html', score=score, status=translated_status, consult_message=consult_message)