import json
from fastapi import APIRouter, Depends, UploadFile, File
# from langchain.chains.llm import LLMChain
# from langchain_core.prompts import PromptTemplate
from sqlalchemy.orm import Session
from app.schemas import NotesCreate
from .. import schemas, models, database
# from langchain.llms import OpenAI
from app.config import client, redis_client
from app.helpers import extract_entities, get_response, get_response_for_file

router = APIRouter()

notes_collection = client.get_or_create_collection("notes_embeddings")


@router.post('/note-create', tags=["Notes"])
def create_note(request: NotesCreate, db: Session = Depends(database.get_db)):
    entities = extract_entities(request.notes)
    new_note = models.Todo(title=request.title, notes=request.notes, entities=entities)
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
        n_results=5
    )
    ids = [id[0][0] for id in results.get("ids", " ")]
    data = db.query(models.Todo).filter(models.Todo.id.in_(ids)).all()
    return data


@router.get('/summarize-notes', tags=["Notes"])
def summerize_notes(id: int, db: Session = Depends(database.get_db)):
    data = db.query(models.Todo).filter(models.Todo.id == id).first()
    note_data = redis_client.get(f"note:{data.id}")
    if note_data:
        return json.loads(note_data)
    summarized_text = get_response(data.notes)
    redis_client.set(f"note:{data.id}", json.dumps(summarized_text))
    return summarized_text.replace("\n", " ")


@router.get('/get-info', tags=["Notes"])
def get_info(query: str, db: Session = Depends(database.get_db)):
    # llm = OpenAI(temperature=0.6)
    # prompt_template = PromptTemplate(
    #     input_varaible=['query'],
    #     template="""You are answer generator give proper answer to the question {query} .The answer for the question should be proper and the accurate and
    #                  pointwise."""
    # )
    # chain = LLMChain(llm=llm, prompt=prompt_template)
    # response = chain.run(query)
    data = get_response(query)
    return data


@router.post('/question-answer/', tags=["Notes"])
async def upload_file(query: str, db: Session = Depends(database.get_db), file: UploadFile = File(...)):
    file_location = f"app/uploaded_files/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())
    with open(file_location, "r") as f:
        file_data = f.read()
    data = get_response_for_file(query, file_data)
    new_data = data.replace("\n", "")
    return {"info": f"File content{new_data}"}


@router.get('/all-notes', tags=["Notes"])
def get_all_notes(db: Session = Depends(database.get_db)):
    notes = db.query(models.Todo).all()
    print(notes)
    return notes