from pydantic import BaseModel
from typing import Dict, List

#과목추천 클래스
class Subjects(BaseModel):
    subjects: Dict[str, bool]
    semester : str

#자격증 클래스
class Certification(BaseModel):
    certification: Dict[str, bool]
    my_score : int 

#채용정보위한 스택 클래스
class Work(BaseModel):
    work: List[str]


#챗봇의 요청클래스
class Message(BaseModel):
    message: str

