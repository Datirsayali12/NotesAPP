import spacy
import re
import openai

nlp = spacy.load("en_core_web_sm")


def extract_entities(text):
    doc = nlp(text)
    entities = {
        "emails": [],
        "phone_numbers": [],
        "names": [],
        "locations": []
    }

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            entities["names"].append(ent.text)
        elif ent.label_ == "GPE":
            entities["locations"].append(ent.text)
        elif ent.label_ == "ORG":
            entities["locations"].append(ent.text)

    numbers = re.findall('[6-9]\d{9}', text)
    emails = re.findall('^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-zA-Z]{2,}$', text)

    entities["numbers"] = numbers
    entities["email"] = emails
    return entities


def send_message(message_log, temp=0.4):
    print("openai started")
    # Use OpenAI's ChatCompletion API to get the chatbot's response
    openai.api_key = OPENAI_KEY
    openai.api_base = "https://api.openai.com/v1"
    openai.api_type = "open_ai"
    openai.api_version = None
    # MODELS = ["gpt-4", "gpt-4-0125-preview", "gpt-3.5-turbo", "gpt-3.5-turbo-0301","gpt-3.5-turbo-0613"]
    MODELS = ["gpt-3.5-turbo", "gpt-3.5-turbo-0301", "gpt-3.5-turbo-0613"]

    for model_name in MODELS:
        try:
            response = openai.ChatCompletion.create(
                model=model_name,  # The name of the OpenAI chatbot model to use
                messages=message_log,  # The conversation history up to this point, as a list of dictionaries
                max_tokens=1500,  # The maximum number of tokens (words or subwords) in the generated response
                # stop=None,  # The stopping sequence for the generated response, if any (not used here)
                temperature=temp,  # The "creativity" of the generated response (higher temperature = more creative)
                top_p=0,
                frequency_penalty=0,
                presence_penalty=0,
                timeout=100
            )
            # print(response)
            # Find the first response from the chatbot that has text in it (some responses may not have text)
            for choice in response.choices:
                if "text" in choice:
                    return choice.text

                # If no response with text is found, return the first response's content (which may be empty)
            print(response.usage)
            return response.choices[0].message.content
        except Exception as e:
            print("Error: OPENAI ", e)
            return {"message": str(e)}  # Return the error message instead of raising an exception
        return {"message": "Unknown error"}


def get_response(search_context):
    message_log = [
        {
            "role": "system",
            "content": """You are an expert in providing clean and structured responses based on text. 
            Your job is to analyze the provided text, clean the data, and generate a concise and accurate 
            response. your work is to summarize the text.
            """
        },
        {
            "role": "user",
            "content": search_context
        }
    ]

    response = send_message(message_log)
    return response


def get_response_for_file(search_context, content):
    message_log = [
        {
            "role": "system",
            "content": f"""You are an expert in providing clean and structured responses based on text. 
            Your job is to analyze the provided text, clean the data, and generate a concise and accurate 
            response. your work is answer the question based on {content} that provided.
            """
        },
        {
            "role": "user",
            "content": search_context
        }
    ]

    response = send_message(message_log)
    return response
