from openai import OpenAI
from markdown2 import markdown
from openai.types.beta.threads.message_create_params import Attachment, AttachmentToolFileSearch
import os

secret_path = "/run/secrets/API_KEY"
if os.path.exists(secret_path):
    with open(secret_path, "r") as file:
        os.environ["OPENAI_API_KEY"] = file.read().strip()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# QUESTION prompt to ask ChatGPT to respond with only emojis
QUESTION_PROMPT = "I have a document about radar in PDF. "

OPENAI_MODEL = "gpt-4o-mini"

client = OpenAI(api_key=OPENAI_API_KEY, )


def pdf2qa_baseline(technical_content, prompt_question):
	# temporal hard coding
	pdf_path = 'static/files/radar_5/radar_5_origin.pdf'
	# Upload your pdf(s) to the OpenAI API
	file = client.files.create(file=open(pdf_path, 'rb'), purpose='assistants')

	language_prompt_3 = "Please answer the question in the language of the question."
	# Add the prompt to the question
	updated_prompt = (QUESTION_PROMPT + str(prompt_question) + language_prompt_3 +
					"Please provide your response in Markdown format, using appropriate syntax such as **bold**, *italics*, `code blocks`, and tables. "
    				"Do NOT use JSON formatting."
					"limit your response to 1000 characters.")

	# Create thread
	thread = client.beta.threads.create()

	# Create an Assistant (or fetch it if it was already created). It has to have
	# "file_search" tool enabled to attach files when prompting it.
	def get_assistant():
		for assistant in client.beta.assistants.list():
			if assistant.name == 'My Assistant Name':
				return assistant

		# No Assistant found, create a new one
		return client.beta.assistants.create(
			model=OPENAI_MODEL,
			description='You are a PDF retrieval assistant.',
			instructions=(
				"You are a helpful assistant designed to output only Markdown."
				"Always format responses in Markdown, never JSON or any other format."
				"Use Markdown syntax for tables, lists, and code blocks when necessary."
				"DO NOT use JSON formatting."),
			tools=[{
				"type": "file_search"
			}],
			name='My Assistant Name',
			temperature=0.0,
			max_tokens=1023,
		)

	client.beta.threads.messages.create(
		thread_id=thread.id,
		role='user',
		content=updated_prompt,
		attachments=[
			Attachment(file_id=file.id,
						tools=[AttachmentToolFileSearch(type='file_search')])
		])

	# Run the created thread with the assistant. It will wait until the message is processed.
	run = client.beta.threads.runs.create_and_poll(
		thread_id=thread.id,
		assistant_id=get_assistant().id,
		timeout=300,  # 5 minutes
		# response_format={"type": "json_object"}, # Isn't possible
	)
	print("RUN: ", run)

	# Eg. issue with openai server
	if run.status != "completed":
		raise Exception('Run failed:', run.status)

	# Fetch outputs of the thread
	messages_cursor = client.beta.threads.messages.list(thread_id=thread.id)
	messages = [message for message in messages_cursor]

	message = messages[
		0]  # This is the output from the Assistant (second message is your message)
	assert message.content[0].type == "text"
	markdown_text = message.content[0].text.value
	html_text = markdown(markdown_text)
	print("HTML: ", html_text)
	return html_text
