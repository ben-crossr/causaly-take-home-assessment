from typing import Optional

from pydantic import BaseModel

class Node(BaseModel):
    id: str
    name: str
    type: str
    other_identifiers: Optional[list[str]] = None


class Relationship(BaseModel):
    start_node_id: str
    end_node_id: str
    type: str
    subtype: Optional[str] = None
    score: Optional[float] = None
    provenance: str