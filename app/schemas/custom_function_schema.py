from pydantic import BaseModel

class CustomFunctionRequest(BaseModel):
    name: str
    expression: str

class CustomFunctionResponse(CustomFunctionRequest):
    id: str
    uid: str
    date: str
