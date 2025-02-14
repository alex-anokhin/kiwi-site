from openai import OpenAI
import re
import os
from markdown2 import markdown
from dotenv import load_dotenv

load_dotenv(dotenv_path="secrets/.env")
# secret_path = "/run/secrets/API_KEY"
# if os.path.exists(secret_path):
#     with open(secret_path, "r") as file:
#         os.environ["OPENAI_API_KEY"] = file.read().strip()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# QUESTION prompt to ask ChatGPT to respond with only emojis
QUESTION_PROMPT_1 = "This is the markdown file of the radar official technical document."

QUESTION_PROMPT_2 = "Can you answer the specific question precicely given the technical document? If question is about getting image, you can return the image location."

OPENAI_MODEL = "gpt-4o-mini"

client = OpenAI(api_key=OPENAI_API_KEY, )


def pdf2qa_our(technical_content, prompt_question):
	# temporal hard coding
	pdf_md_path = 'static/files/radar_5/radar_5.md'
	with open(pdf_md_path, 'r', encoding='utf-8') as md_file:
		technical_content = md_file.read()

	language_prompt_3 = "Please answer the question in the language of the question."

	# Add the prompt to the question
	updated_prompt = (QUESTION_PROMPT_1 + str(
		technical_content) + QUESTION_PROMPT_2 + str(
			prompt_question) + language_prompt_3 +
			"Please provide your response in Markdown format, using appropriate syntax such as **bold**, *italics*, `code blocks`, and tables. limit your response to 1000 characters.")

	# Generate a response using the ChatCompletion API
	response = client.chat.completions.create(model=OPENAI_MODEL,
		messages=[{
			"role": "user",
			"content": updated_prompt}
			],
			temperature=0.0,
			max_tokens=1023,
			)
	raw = response.choices[0].message.content
	# tmp = raw
	print("Original String:\n", raw)

	text = re.sub(r'!\[.*?\]\(.*?\)', '', raw).strip()
	text = markdown(text)
	# print("\nAfter Replacement:\n", text)
	imgs = re.findall(r'images/[^\)]+', raw)
	# Get the last image path
	last_img = imgs[0] if imgs else None
	# print("LAST:\n", last_img)
	return text, last_img
