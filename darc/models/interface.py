from typing import Dict
from uuid import UUID

from pydantic import BaseModel
class SourceCode(BaseModel):
    # Use tree dir to get the structure
    tree: str
    # {file_name: src_str}
    content: Dict[str, str]