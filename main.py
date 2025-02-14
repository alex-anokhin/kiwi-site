from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from datetime import datetime
import os
import requests
import uuid
import uvicorn
from dotenv import load_dotenv
from QA_text import pdf2qa_our
from QA_pdf import pdf2qa_baseline

# Load environment variables from .env file
load_dotenv(dotenv_path="secrets/.env")
CONTACT_API = os.getenv('CONTACT_API')

app = FastAPI()  # Initialize the FastAPI application (your server)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get('/')
async def index(request: Request):
	return RedirectResponse(url='/home')

# Render your homepage using the index.html file
@app.get('/home')
async def home(request: Request):
	user_id = request.cookies.get('user_id', str(uuid.uuid4()))
	response = templates.TemplateResponse('home.html', {'request': request})
	response.set_cookie('user_id', user_id, max_age=30 * 24 * 60 * 60)
	return response

# Render your /solution page with the solution.html file
@app.get('/solution')
async def solution(request: Request):
	user_id = request.cookies.get('user_id', str(uuid.uuid4()))
	response = templates.TemplateResponse('solution.html', {'request': request})
	response.set_cookie('user_id', user_id, max_age=30 * 24 * 60 * 60)
	return response

# Render your /contact page with the contact.html file
@app.get('/contact')
async def contact(request: Request):
	user_id = request.cookies.get('user_id', str(uuid.uuid4()))
	response = templates.TemplateResponse('contact.html', {'request': request})
	response.set_cookie('user_id', user_id, max_age=30 * 24 * 60 * 60)
	return response

# Uncomment and convert the solution route to FastAPI
@app.post('/original')
async def original(request: Request):
	form = await request.form()
	prompt = form['prompt']
	res1_text = pdf2qa_baseline(None, prompt)
	user_id = request.cookies.get('user_id', str(uuid.uuid4()))
	response = templates.TemplateResponse('solution.html', {
		'request': request,
		'response1': res1_text,
		# 'response1': "res1_text",
		'response2': None
	})
	response.set_cookie('user_id', user_id, max_age=30 * 24 * 60 * 60)
	return response

@app.post('/solution')
async def solution(request: Request):
	form = await request.form()
	prompt = form['prompt']
	res1_text = pdf2qa_baseline(None, prompt)
	res2_text, res2_img_path = pdf2qa_our(None, prompt)
	user_id = request.cookies.get('user_id', str(uuid.uuid4()))
	response = templates.TemplateResponse('solution.html', {
		'request': request,
		'response1': res1_text,
		# 'response1': "res1_text",
		'response2': {"text": res2_text, "img": res2_img_path}
	})
	response.set_cookie('user_id', user_id, max_age=30 * 24 * 60 * 60)
	return response

# Uncomment and convert the contact route to FastAPI
@app.post('/contact')
async def contact(request: Request):
	form = await request.form()
	name = form['name']
	email = form['email']
	submit_time = datetime.utcnow().isoformat()
	headers = {
		'Content-Type': 'application/json'
	}
	data = {
		"name": name,
		"email": email,
		"timestamp": submit_time
	}
	r = requests.post(CONTACT_API, headers=headers, json=data)
	if r.status_code in [200, 201]:
		response = templates.TemplateResponse('contact.html', {
			'request': request,
			'message': 'Thank you for subscription! We\'ve received your request! Check your email for a confirmation.',
			'success': True
		})
	else:
		response = templates.TemplateResponse('contact.html', {
			'request': request,
			'error': 'There was an error submitting your subscription. Please try again.',
			'success': True
		})
	return response

if __name__ == "__main__":
	uvicorn.run("main:app", host="0.0.0.0", port=7860, reload=True)