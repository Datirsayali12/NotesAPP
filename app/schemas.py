from pydantic import BaseModel


class NotesCreate(BaseModel):
    title: str
    notes: str
   