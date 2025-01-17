from flask import Flask, render_template, request, make_response
from text2emoji import text2emoji, text2emoji_2
from QA_text import pdf2qa_our
from QA_pdf import pdf2qa_baseline
from datetime import datetime
import requests
import uuid
from config import (
    AIRTABLE_API_KEY,
    AIRTABLE_BASE_ID,
    AIRTABLE_CONTACTS_API_URL,
    AIRTABLE_TRANSLATOR_API_URL,
)

import os
CONTACT_API = os.getenv('CONTACT_API')

app = Flask(__name__)  # Initialize the Flask application (your server)


# Render your homepage using the index.thml file
@app.route('/', methods=['GET', 'POST'])
def index():
    """Main route for text-to-emoji conversion and saving inputs/outputs to Airtable."""
    if request.method == 'POST':
        prompt = request.form['prompt']
        # emoji_response = text2emoji(prompt) # Use the text2emoji function to convert text to emoji
        technical_content = None
        # emoji_response = pdf2qa_our(technical_content, prompt)
        user_id = request.cookies.get('user_id', str(uuid.uuid4()))

        return None  #response
    else:
        # Render index page for GET requests
        user_id = request.cookies.get('user_id', str(uuid.uuid4()))
        response = make_response(render_template('index.html'))
        response.set_cookie('user_id', user_id, max_age=30 * 24 * 60 * 60)
        return response


# Render your /contact page with the contact.html file
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page for handling user messages and saving them in Airtable."""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        # message = request.form['message']
        submit_time = datetime.utcnow().isoformat()

        headers = {
            # 'Authorization': f'Bearer {AIRTABLE_API_KEY}',
            'Content-Type': 'application/json'
        }
        data = {
            "name": name,
            "email": email,
            # "message": message,
            "timestamp": submit_time
        }

        # Send data to Airtable and handle response
        # r = requests.post(AIRTABLE_CONTACTS_API_URL,
        r = requests.post(CONTACT_API,
                          headers=headers,
                          json=data)
        if r.status_code in [200, 201]:
            return render_template(
                'contact.html',
                message='Thank you for subscription! We\'ve received your request! You\'ll be notified when we launch. 🎉', success=True)
        else:
            return render_template(
                'contact.html',
                error=
                'There was an error submitting your subscription. Please try again.', success=True)
    else:
        # Render contact page for GET requests
        return render_template('contact.html', success=False)


@app.route('/solution', methods=['GET', 'POST'])
def solution():
    """Main route for text-to-emoji conversion and saving inputs/outputs to Airtable."""
    if request.method == 'POST':
        prompt = request.form['prompt']
        emoji_response1 = pdf2qa_baseline(
            None,
            prompt)  # Use the text2emoji function to convert text to emoji
        res2_text, res2_img_path = pdf2qa_our(None, prompt)
        user_id = request.cookies.get('user_id', str(uuid.uuid4()))
        # response = make_response
        response = make_response(
            render_template('solution.html',
                            response1=emoji_response1,
                            response2={"text": res2_text, "img": res2_img_path}))
        response.set_cookie('user_id', user_id, max_age=30 * 24 * 60 *
                            60)  # Set a cookie to remember the user's ID

        # Save the input and output to Airtable
        headers = {
            'Authorization': f'Bearer {AIRTABLE_API_KEY}',
            'Content-Type': 'application/json'
        }
        data = {
            "records": [{
                "fields": {
                    "User ID": user_id,
                    "Input": prompt,
                    "Output": emoji_response1,
                    "Submit time": datetime.utcnow().isoformat()
                }
            }]
        }

        # Send data to Airtable and handle errors
        r = requests.post(AIRTABLE_TRANSLATOR_API_URL,
                          headers=headers,
                          json=data)
        if r.status_code not in [200, 201]:
            print(f'Error storing input in Airtable: {r.status_code}')

        return response
    else:
        # Render index page for GET requests
        user_id = request.cookies.get('user_id', str(uuid.uuid4()))
        response = make_response(render_template('solution.html'))
        response.set_cookie('user_id', user_id, max_age=30 * 24 * 60 * 60)
        return response


if __name__ == '__main__':
    # Run the Flask app
    app.run(host="0.0.0.0", port=7860, debug=True)
