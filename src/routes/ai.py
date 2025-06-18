from flask import Blueprint, request, jsonify
import json
import time
import random
import os
from datetime import datetime
from src.services.ai_services import ClaudeService, ElevenLabsService, TavusService, AWSRekognitionService
from src.services.prompts import MedicalPrompts

ai_bp = Blueprint('ai', __name__)

# Initialize AI services
claude_service = ClaudeService()
elevenlabs_service = ElevenLabsService()
tavus_service = TavusService()
rekognition_service = AWSRekognitionService()

# Configuration flags
USE_REAL_SERVICES = os.getenv('USE_REAL_AI_SERVICES', 'false').lower() == 'true'
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
TAVUS_API_KEY = os.getenv('TAVUS_API_KEY')

# Initialize real services if credentials are available
if USE_REAL_SERVICES:
    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        claude_service.initialize_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        rekognition_service.initialize_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    
    if ELEVENLABS_API_KEY:
        elevenlabs_service.set_api_key(ELEVENLABS_API_KEY)
    
    if TAVUS_API_KEY:
        tavus_service.set_api_key(TAVUS_API_KEY)

# Mock responses for fallback
MOCK_CLAUDE_RESPONSES = {
    'patient_chat': [
        "I understand your concern. Based on what you've described, it's important to monitor your symptoms. If they persist or worsen, please consider consulting with a healthcare professional.",
        "Thank you for sharing this information. While I can provide general guidance, it's always best to speak with a doctor for personalized medical advice.",
        "Your symptoms could be related to several factors. I recommend keeping track of when they occur and any potential triggers. If you're concerned, please reach out to a healthcare provider."
    ],
    'vitals_analysis': [
        "Based on the vitals provided, the readings appear to be within normal ranges. Continue monitoring and maintain healthy lifestyle habits.",
        "The blood pressure reading is slightly elevated. Consider lifestyle modifications and follow up with a healthcare provider if this persists.",
        "The oxygen saturation level is concerning. Immediate medical attention may be required. Please escalate this case."
    ],
    'case_summary': [
        "Patient presents with respiratory symptoms including cough and shortness of breath. Vital signs show elevated heart rate. Recommend chest X-ray and further evaluation.",
        "Chief complaint involves gastrointestinal symptoms. Patient reports nausea and abdominal pain. Vitals stable. Consider dietary factors and stress levels.",
        "Patient experiencing headache and dizziness. Blood pressure readings are elevated. Recommend neurological assessment and blood pressure monitoring."
    ]
}

@ai_bp.route('/chat', methods=['POST'])
def patient_chat():
    """
    Patient AI Chat endpoint
    Uses Claude 3 for medical reasoning or falls back to mock responses
    """
    try:
        data = request.get_json()
        patient_message = data.get('message', '')
        patient_id = data.get('patient_id', '')
        session_id = data.get('session_id', '')
        patient_history = data.get('patient_history', '')
        
        if USE_REAL_SERVICES and claude_service.bedrock_client:
            # Use real Claude service
            prompt = MedicalPrompts.patient_chat_prompt(patient_message, patient_history)
            claude_response = claude_service.generate_response(prompt)
            
            if claude_response['success']:
                response_text = claude_response['response']
                confidence = 0.9  # High confidence for real AI
            else:
                # Fallback to mock if real service fails
                response_text = random.choice(MOCK_CLAUDE_RESPONSES['patient_chat'])
                confidence = 0.7
        else:
            # Use mock response
            response_text = random.choice(MOCK_CLAUDE_RESPONSES['patient_chat'])
            confidence = random.uniform(0.7, 0.85)
            time.sleep(random.uniform(1, 3))  # Simulate processing time
        
        response = {
            'success': True,
            'response': response_text,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'requires_escalation': confidence < 0.8,
            'suggested_actions': [
                'Monitor symptoms',
                'Stay hydrated',
                'Rest as needed'
            ] if confidence > 0.8 else [
                'Consult healthcare provider',
                'Monitor closely',
                'Seek immediate care if symptoms worsen'
            ],
            'service_used': 'claude' if USE_REAL_SERVICES and claude_service.bedrock_client else 'mock'
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@ai_bp.route('/analyze-vitals', methods=['POST'])
def analyze_vitals():
    """
    Health Worker Vitals Analysis endpoint
    Uses Claude 3 for analysis or falls back to mock responses
    """
    try:
        data = request.get_json()
        vitals = data.get('vitals', {})
        patient_id = data.get('patient_id', '')
        
        # Extract vital signs
        bp_systolic = vitals.get('bp_systolic', 120)
        bp_diastolic = vitals.get('bp_diastolic', 80)
        heart_rate = vitals.get('heart_rate', 70)
        oxygen_saturation = vitals.get('oxygen_saturation', 98)
        temperature = vitals.get('temperature', 98.6)
        
        if USE_REAL_SERVICES and claude_service.bedrock_client:
            # Use real Claude service
            prompt = MedicalPrompts.vitals_analysis_prompt(vitals)
            claude_response = claude_service.generate_response(prompt)
            
            if claude_response['success']:
                response_text = claude_response['response']
            else:
                response_text = random.choice(MOCK_CLAUDE_RESPONSES['vitals_analysis'])
        else:
            # Use mock response
            response_text = random.choice(MOCK_CLAUDE_RESPONSES['vitals_analysis'])
            time.sleep(random.uniform(1, 2))  # Simulate processing time
        
        # Simple risk assessment logic
        risk_level = 'low'
        urgency = 'routine'
        
        if bp_systolic > 140 or bp_diastolic > 90:
            risk_level = 'medium'
            urgency = 'elevated'
        
        if oxygen_saturation < 95 or heart_rate > 100 or temperature > 101:
            risk_level = 'high'
            urgency = 'urgent'
        
        response = {
            'success': True,
            'analysis': response_text,
            'risk_level': risk_level,
            'urgency': urgency,
            'timestamp': datetime.now().isoformat(),
            'vitals_summary': {
                'blood_pressure': f"{bp_systolic}/{bp_diastolic}",
                'heart_rate': heart_rate,
                'oxygen_saturation': oxygen_saturation,
                'temperature': temperature
            },
            'recommendations': [
                'Continue monitoring',
                'Maintain current treatment plan'
            ] if risk_level == 'low' else [
                'Escalate to doctor',
                'Increase monitoring frequency',
                'Consider immediate intervention'
            ],
            'service_used': 'claude' if USE_REAL_SERVICES and claude_service.bedrock_client else 'mock'
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@ai_bp.route('/summarize-case', methods=['POST'])
def summarize_case():
    """
    Doctor Case Summary endpoint
    Uses Claude 3 for case summarization or falls back to mock responses
    """
    try:
        data = request.get_json()
        case_data = data.get('case_data', {})
        patient_id = data.get('patient_id', '')
        
        if USE_REAL_SERVICES and claude_service.bedrock_client:
            # Use real Claude service
            prompt = MedicalPrompts.case_summary_prompt(case_data)
            claude_response = claude_service.generate_response(prompt, max_tokens=1500)
            
            if claude_response['success']:
                response_text = claude_response['response']
            else:
                response_text = random.choice(MOCK_CLAUDE_RESPONSES['case_summary'])
        else:
            # Use mock response
            response_text = random.choice(MOCK_CLAUDE_RESPONSES['case_summary'])
            time.sleep(random.uniform(2, 4))  # Simulate processing time
        
        response = {
            'success': True,
            'summary': response_text,
            'key_symptoms': [
                'Primary complaint identified',
                'Vital signs reviewed',
                'Patient history considered'
            ],
            'red_flags': [
                'Monitor for symptom progression',
                'Watch for complications'
            ],
            'differential_diagnoses': [
                'Primary diagnosis consideration',
                'Alternative diagnosis possibility',
                'Rule out serious conditions'
            ],
            'recommended_actions': [
                'Schedule follow-up',
                'Order additional tests if needed',
                'Provide patient education'
            ],
            'timestamp': datetime.now().isoformat(),
            'service_used': 'claude' if USE_REAL_SERVICES and claude_service.bedrock_client else 'mock'
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@ai_bp.route('/generate-tts', methods=['POST'])
def generate_tts():
    """
    Text-to-Speech endpoint
    Uses ElevenLabs or falls back to mock response
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        voice_id = data.get('voice_id', 'default')
        
        if USE_REAL_SERVICES and elevenlabs_service.api_key:
            # Use real ElevenLabs service
            tts_response = elevenlabs_service.generate_speech(text, voice_id)
            
            if tts_response['success']:
                # In a real implementation, save the audio file and return URL
                response = {
                    'success': True,
                    'audio_url': f"https://your-storage.com/audio/{random.randint(1000, 9999)}.mp3",
                    'duration': len(text) * 0.1,
                    'voice_id': voice_id,
                    'timestamp': datetime.now().isoformat(),
                    'text_length': len(text),
                    'service_used': 'elevenlabs'
                }
            else:
                # Fallback to mock
                response = {
                    'success': True,
                    'audio_url': f"https://mock-audio-service.com/audio/{random.randint(1000, 9999)}.mp3",
                    'duration': len(text) * 0.1,
                    'voice_id': voice_id,
                    'timestamp': datetime.now().isoformat(),
                    'text_length': len(text),
                    'service_used': 'mock'
                }
        else:
            # Use mock response
            time.sleep(random.uniform(2, 5))  # Simulate processing time
            response = {
                'success': True,
                'audio_url': f"https://mock-audio-service.com/audio/{random.randint(1000, 9999)}.mp3",
                'duration': len(text) * 0.1,
                'voice_id': voice_id,
                'timestamp': datetime.now().isoformat(),
                'text_length': len(text),
                'service_used': 'mock'
            }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@ai_bp.route('/create-video-summary', methods=['POST'])
def create_video_summary():
    """
    Personalized Video Summary endpoint
    Uses Claude + Tavus or falls back to mock response
    """
    try:
        data = request.get_json()
        diagnosis = data.get('diagnosis', '')
        treatment_plan = data.get('treatment_plan', '')
        patient_name = data.get('patient_name', 'Patient')
        doctor_name = data.get('doctor_name', 'Dr. Smith')
        
        # First, generate script using Claude
        if USE_REAL_SERVICES and claude_service.bedrock_client:
            prompt = MedicalPrompts.video_summary_prompt(diagnosis, treatment_plan, doctor_name, patient_name)
            claude_response = claude_service.generate_response(prompt)
            
            if claude_response['success']:
                script = claude_response['response']
            else:
                script = f"Hello {patient_name}, this is a summary of your consultation with {doctor_name}. {diagnosis} {treatment_plan}"
        else:
            script = f"Hello {patient_name}, this is a summary of your consultation with {doctor_name}. {diagnosis} {treatment_plan}"
        
        # Then, create video using Tavus
        if USE_REAL_SERVICES and tavus_service.api_key:
            video_response = tavus_service.create_video(script)
            
            if video_response['success']:
                response = {
                    'success': True,
                    'video_url': video_response['video_url'],
                    'thumbnail_url': video_response['thumbnail_url'],
                    'video_id': video_response['video_id'],
                    'script': script,
                    'duration': 60,
                    'patient_name': patient_name,
                    'doctor_name': doctor_name,
                    'timestamp': datetime.now().isoformat(),
                    'service_used': 'tavus'
                }
            else:
                # Fallback to mock
                response = {
                    'success': True,
                    'video_url': f"https://mock-video-service.com/video/{random.randint(1000, 9999)}.mp4",
                    'thumbnail_url': f"https://mock-video-service.com/thumbnail/{random.randint(1000, 9999)}.jpg",
                    'script': script,
                    'duration': 60,
                    'patient_name': patient_name,
                    'doctor_name': doctor_name,
                    'timestamp': datetime.now().isoformat(),
                    'service_used': 'mock'
                }
        else:
            # Use mock response
            time.sleep(random.uniform(5, 10))  # Simulate processing time
            response = {
                'success': True,
                'video_url': f"https://mock-video-service.com/video/{random.randint(1000, 9999)}.mp4",
                'thumbnail_url': f"https://mock-video-service.com/thumbnail/{random.randint(1000, 9999)}.jpg",
                'script': script,
                'duration': 60,
                'patient_name': patient_name,
                'doctor_name': doctor_name,
                'timestamp': datetime.now().isoformat(),
                'service_used': 'mock'
            }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@ai_bp.route('/analyze-image', methods=['POST'])
def analyze_image():
    """
    Medical Image Analysis endpoint
    Uses AWS Rekognition or falls back to mock response
    """
    try:
        data = request.get_json()
        image_url = data.get('image_url', '')
        image_data = data.get('image_data', '')  # Base64 encoded image
        analysis_type = data.get('analysis_type', 'general')
        
        if USE_REAL_SERVICES and rekognition_service.rekognition_client and image_data:
            # Convert base64 to bytes
            import base64
            image_bytes = base64.b64decode(image_data)
            
            rekognition_response = rekognition_service.analyze_image(image_bytes, analysis_type)
            
            if rekognition_response['success']:
                # Process Rekognition results into medical context
                findings = []
                if 'labels' in rekognition_response:
                    for label in rekognition_response['labels'][:5]:  # Top 5 labels
                        findings.append(f"Detected: {label['Name']} (confidence: {label['Confidence']:.1f}%)")
                
                response = {
                    'success': True,
                    'findings': findings,
                    'confidence': 0.85,
                    'analysis_type': analysis_type,
                    'recommendations': [
                        'Clinical correlation advised',
                        'Follow up as needed',
                        'Document changes over time'
                    ],
                    'timestamp': datetime.now().isoformat(),
                    'service_used': 'rekognition'
                }
            else:
                # Fallback to mock
                response = {
                    'success': True,
                    'findings': ['Image quality adequate for analysis', 'No obvious abnormalities detected'],
                    'confidence': 0.75,
                    'analysis_type': analysis_type,
                    'recommendations': ['Clinical correlation advised'],
                    'timestamp': datetime.now().isoformat(),
                    'service_used': 'mock'
                }
        else:
            # Use mock response
            time.sleep(random.uniform(3, 6))  # Simulate processing time
            
            mock_findings = [
                "Image quality is adequate for analysis",
                "No obvious abnormalities detected",
                "Recommend clinical correlation"
            ]
            
            if analysis_type == 'skin':
                mock_findings = [
                    "Skin lesion appears benign",
                    "Regular monitoring recommended",
                    "Consider dermatology consultation if changes occur"
                ]
            elif analysis_type == 'wound':
                mock_findings = [
                    "Wound healing appears normal",
                    "No signs of infection visible",
                    "Continue current treatment plan"
                ]
            
            response = {
                'success': True,
                'findings': mock_findings,
                'confidence': random.uniform(0.7, 0.9),
                'analysis_type': analysis_type,
                'recommendations': [
                    'Clinical correlation advised',
                    'Follow up as needed',
                    'Document changes over time'
                ],
                'timestamp': datetime.now().isoformat(),
                'service_used': 'mock'
            }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@ai_bp.route('/emergency-triage', methods=['POST'])
def emergency_triage():
    """
    Emergency Triage Assessment endpoint
    Uses Claude 3 for triage or falls back to rule-based assessment
    """
    try:
        data = request.get_json()
        symptoms = data.get('symptoms', '')
        vitals = data.get('vitals', {})
        patient_id = data.get('patient_id', '')
        
        if USE_REAL_SERVICES and claude_service.bedrock_client:
            # Use real Claude service
            prompt = MedicalPrompts.emergency_triage_prompt(symptoms, vitals)
            claude_response = claude_service.generate_response(prompt)
            
            if claude_response['success']:
                triage_analysis = claude_response['response']
            else:
                triage_analysis = "Unable to complete AI analysis. Using rule-based assessment."
        else:
            triage_analysis = "Rule-based triage assessment completed."
        
        # Rule-based triage logic as fallback
        triage_level = 'NON-URGENT'
        call_emergency = False
        
        # Check for emergency keywords
        emergency_keywords = ['chest pain', 'difficulty breathing', 'unconscious', 'severe bleeding', 'stroke']
        urgent_keywords = ['severe pain', 'high fever', 'vomiting blood', 'severe headache']
        
        symptoms_lower = symptoms.lower()
        
        for keyword in emergency_keywords:
            if keyword in symptoms_lower:
                triage_level = 'IMMEDIATE'
                call_emergency = True
                break
        
        if triage_level != 'IMMEDIATE':
            for keyword in urgent_keywords:
                if keyword in symptoms_lower:
                    triage_level = 'URGENT'
                    break
        
        # Check vitals for emergency conditions
        if vitals:
            oxygen_sat = vitals.get('oxygen_saturation', 100)
            heart_rate = vitals.get('heart_rate', 70)
            bp_systolic = vitals.get('bp_systolic', 120)
            
            if oxygen_sat < 90 or heart_rate > 120 or bp_systolic > 180:
                triage_level = 'IMMEDIATE'
                call_emergency = True
        
        response = {
            'success': True,
            'triage_level': triage_level,
            'call_emergency': call_emergency,
            'analysis': triage_analysis,
            'reasoning': f"Assessment based on symptoms: {symptoms[:100]}...",
            'immediate_actions': [
                'Call emergency services immediately' if call_emergency else 'Seek medical attention',
                'Monitor vital signs',
                'Stay with patient'
            ],
            'timestamp': datetime.now().isoformat(),
            'service_used': 'claude' if USE_REAL_SERVICES and claude_service.bedrock_client else 'rule-based'
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@ai_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for the AI service
    """
    service_status = {
        'claude': 'available' if USE_REAL_SERVICES and claude_service.bedrock_client else 'mock',
        'elevenlabs': 'available' if USE_REAL_SERVICES and elevenlabs_service.api_key else 'mock',
        'tavus': 'available' if USE_REAL_SERVICES and tavus_service.api_key else 'mock',
        'rekognition': 'available' if USE_REAL_SERVICES and rekognition_service.rekognition_client else 'mock'
    }
    
    return jsonify({
        'status': 'healthy',
        'service': 'VirtuDoc AI Backend',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'use_real_services': USE_REAL_SERVICES,
        'services': service_status
    })

@ai_bp.route('/config', methods=['POST'])
def update_config():
    """
    Update AI service configuration
    """
    try:
        data = request.get_json()
        
        # Update API keys if provided
        if 'elevenlabs_api_key' in data:
            elevenlabs_service.set_api_key(data['elevenlabs_api_key'])
        
        if 'tavus_api_key' in data:
            tavus_service.set_api_key(data['tavus_api_key'])
        
        if 'aws_access_key_id' in data and 'aws_secret_access_key' in data:
            claude_service.initialize_client(data['aws_access_key_id'], data['aws_secret_access_key'])
            rekognition_service.initialize_client(data['aws_access_key_id'], data['aws_secret_access_key'])
        
        return jsonify({
            'success': True,
            'message': 'Configuration updated successfully',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

