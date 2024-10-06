import json
import openai
from fastapi import APIRouter, Depends, UploadFile, File
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import Response

from app.schemas import NotesCreate
from app.database import engine
from .. import schemas, models, database
import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings

from io import StringIO
import redis
from langchain.llms import OpenAI

openai.api_key = OPENAI_KEY

redis_client = redis.Redis(host='localhost', port=6379, db=0)

router = APIRouter()


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


client = chromadb.PersistentClient(
    path="app/notes_data",
    settings=Settings(),
    tenant=DEFAULT_TENANT,
    database=DEFAULT_DATABASE,
)

notes_collection = client.get_or_create_collection("notes_embeddings")


@router.post('/note-create', tags=["Notes"])
def create_note(request: NotesCreate, db: Session = Depends(database.get_db)):
    new_note = models.Todo(title=request.title, notes=request.notes)
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    notes_collection.add(
        documents=[request.notes],
        metadatas=[{"title": request.title}],
        ids=[str(new_note.id)]
    )

    return new_note


@router.get('/search-notes', tags=['Notes'])
def search_note(search_query: str, db: Session = Depends(database.get_db)):
    results = notes_collection.query(
        query_texts=[search_query],
        n_results=2
    )
    ids = [id[0][0] for id in results.get("ids", " ")]
    data = db.query(models.Todo).filter(models.Todo.id.in_(ids)).all()
    return data


@router.get('/summarize-notes', tags=["Notes"])
def summerize_notes(id: int, db: Session = Depends(database.get_db)):
    data = db.query(models.Todo).filter(models.Todo.id == id).first()
    # note_data = redis_client.get(f"note:{data.id}")
    # if note_data:
    #     return json.loads(note_data)
    summarized_text = get_response(data.notes)
    # redis_client.set(f"note:{data.id}", json.dumps(summarized_text))
    return summarized_text.replace("\n", " ")


@router.get('/get-info', tags=["Notes"])
def get_info(query: str, db: Session = Depends(database.get_db)):
    llm = OpenAI(temperature=0.6)
    prompt_template = PromptTemplate(
        input_varaible=['query'],
        template="""You are answer generator give proper answer to the question {query} .The answer for the question should be proper and the accurate and
                     pointwise."""
    )
    chain = LLMChain(llm=llm, prompt=prompt_template)
    response = chain.run(query)
    new_response = response.replace('\n', '')
    return new_response


@router.post('/question-answer/', tags=["Notes"])
async def upload_file(query: str, db: Session = Depends(database.get_db), file: UploadFile = File(...)):
    file_location = f"app/uploaded_files/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())
    with open(file_location, "r") as f:
        file_data = f.read()
    llm = OpenAI(temperature=0.6)
    prompt_template = PromptTemplate(
        input_varaible=['query', 'content'],
        template="""You are answer generator give proper answer to the question {query} that based on data {content}.The answer for the question should be proper and the accurate and
                         pointwise."""
    )
    chain = LLMChain(llm=llm, prompt=prompt_template)
    data = chain.run({"query": query, "content": file_data})

    # response=[]
    # chunk_size=50
    # chunks = [file_data[i:i + chunk_size] for i in range(0, len(file_data), chunk_size)]
    # for chunk in chunks:
    #     response.append(chain.run(chunk))
    new_data = data.replace("\n", "")
    return {"info": f"File content{new_data}"}
