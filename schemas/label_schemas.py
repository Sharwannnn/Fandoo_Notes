from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LabelValidator(BaseModel):
    name:Optional[str]=None
    user_id:int