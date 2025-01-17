import openai
from openai import OpenAI
from config import API_KEY

# QUESTION prompt to ask ChatGPT to respond with only emojis
QUESTION = "If this text was an emoji, what would it be? Do not use any written words, only emojis: "

client = OpenAI(
    api_key=API_KEY,  # This is the default and can be omitted
)


# Function to convert text to emoji using ChatGPT
def text2emoji(prompt):
    # Set up the model and prompt
    model = "gpt-3.5-turbo"

    # Add the prompt to the question
    updated_prompt = QUESTION + str(prompt)

    # Generate a response using the ChatCompletion API
    response = client.chat.completions.create(model=model,
                                              messages=[{
                                                  "role":
                                                  "user",
                                                  "content":
                                                  updated_prompt
                                              }])

    # Extract and return the response content
    return "sssssssss"  # response.choices[0].message.content


# Function to convert text to emoji using ChatGPT
def text2emoji_2(prompt):
    # Set up the model and prompt
    model = "gpt-3.5-turbo"

    # Add the prompt to the question
    updated_prompt = QUESTION + str(prompt)

    # Generate a response using the ChatCompletion API
    response = client.chat.completions.create(model=model,
                                              messages=[{
                                                  "role":
                                                  "user",
                                                  "content":
                                                  updated_prompt
                                              }])

    # Extract and return the response content
    return "aaaaaaa"  # response.choices[0].message.content
