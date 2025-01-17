from openai import OpenAI
# from config import API_KEY
import re
import os
API_KEY = os.getenv('API_KEY')
# QUESTION prompt to ask ChatGPT to respond with only emojis
QUESTION_PROMPT_1 = "This is the markdown file of the radar official technical document."

QUESTION_PROMPT_2 = "Can you answer the specific question precicely given the technical document? If question is about getting image, you can return the image location."

OPENAI_MODEL = "gpt-4o-mini"

client = OpenAI(api_key=API_KEY, )


def pdf2qa_our(technical_content, prompt_question):

    # temporal hard coding
    pdf_md_path = 'static/files/radar_5/radar_5.md'
    with open(pdf_md_path, 'r', encoding='utf-8') as md_file:
        technical_content = md_file.read()

    language_prompt_3 = "Please answer the question in the language of the question."

    # Add the prompt to the question
    updated_prompt = QUESTION_PROMPT_1 + str(
        technical_content) + QUESTION_PROMPT_2 + str(
            prompt_question) + language_prompt_3

    # Generate a response using the ChatCompletion API
    response = client.chat.completions.create(model=OPENAI_MODEL,
                                              messages=[{
                                                  "role":
                                                  "user",
                                                  "content":
                                                  updated_prompt
                                              }])
    raw = response.choices[0].message.content
    # tmp = raw
    print("Original String:\n", raw)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', raw).strip()
    # print("\nAfter Replacement:\n", text)
    imgs = re.findall(r'images/[^\)]+', raw)
    # Get the last image path
    last_img = imgs[0] if imgs else None
    print("LAST:\n", last_img)
    # img = re.search(r'images/[^\)]+', raw)
    # if img:
    #     img_path = img.group()
    #     print("\nExtracted Image Path:\n", img_path)
    # else:
    #     img_path = None
    #     print("\nNo Image Path Found.")
    return text, last_img
