from typing import List,Optional
from pydantic import BaseModel

class Move(BaseModel):
    name: str
    move: str
    position: List[List[str]]
    
class ValidMoves(BaseModel):
    name: str
    position: List[List[str]]

class Machin(BaseModel):
    position: List[List[str]]