from openai import OpenAI
# from config import API_KEY
from openai.types.beta.threads.message_create_params import Attachment, AttachmentToolFileSearch
import os
API_KEY = os.getenv('API_KEY')
# QUESTION prompt to ask ChatGPT to respond with only emojis
QUESTION_PROMPT = "I have a document about radar in PDF. "

OPENAI_MODEL = "gpt-4o-mini"

client = OpenAI(api_key=API_KEY, )


def pdf2qa_baseline(technical_content, prompt_question):

    # temporal hard coding
    pdf_path = 'static/files/radar_5/radar_5_origin.pdf'
    # Upload your pdf(s) to the OpenAI API
    file = client.files.create(file=open(pdf_path, 'rb'), purpose='assistants')

    language_prompt_3 = "Please answer the question in the language of the question."
    # Add the prompt to the question
    updated_prompt = QUESTION_PROMPT + str(prompt_question) + language_prompt_3

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
            instructions=
            "You are a helpful assistant designed to output only JSON. Find information from the text and files provided.",
            tools=[{
                "type": "file_search"
            }],
            # response_format={"type": "json_object"}, # Isn't possible with "file_search"
            name='My Assistant Name',
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

    # Eg. issue with openai server
    if run.status != "completed":
        raise Exception('Run failed:', run.status)

    # Fetch outputs of the thread
    messages_cursor = client.beta.threads.messages.list(thread_id=thread.id)
    messages = [message for message in messages_cursor]

    message = messages[
        0]  # This is the output from the Assistant (second message is your message)
    assert message.content[0].type == "text"

    return message.content[0].text.value
