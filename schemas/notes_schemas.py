from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotesValidator(BaseModel):
    title:Optional[str]=None
    description:Optional[str]=None
    color:Optional[str]=None
    reminder:Optional[datetime]=None
    user_id:int