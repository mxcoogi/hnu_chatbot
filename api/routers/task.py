from fastapi import APIRouter
import api.schemas.task as task_schema
import api.recommend.recommend as recommend
from fastapi.responses import JSONResponse
from api.chatbot import parallel_function_calling, common, chatbot
from api.chatbot import characters 


router = APIRouter()

func_calling = parallel_function_calling.FunctionCalling(model=common.model.basic)
Hannam = chatbot.Chatbot(
    model = common.model.basic,
    system_role=characters.system_role,
    instruction=characters.instruction,
    user = "학생",
    assistant = "한남이"
    )

@router.post("/echo")
async def chat_message(msg: task_schema.Message):
    request_message = msg.message
    print("request_message:", request_message)
    Hannam.add_user_message(request_message)
    #함수사용 판단
    analyzed, analyzed_dict = func_calling.analyze(request_message, parallel_function_calling.tools)
    if analyzed_dict.get("tool_calls"):
        response = func_calling.run(analyzed,analyzed_dict, Hannam.context[:])
        Hannam.add_response(response)
    else:
        response = Hannam.send_request()
        Hannam.add_response(response)
    response_message = Hannam.get_response_content()
    Hannam.handle_token_limit(response)
    Hannam.clean_context()
    print("response_message:", response_message)
    return JSONResponse(content=response_message, media_type="application/json; charset=utf-8")




#수강신청, 추천과목 서비스
@router.post('/submit-subjects')
async def submit_subjects(subjects : task_schema.Subjects):
    request = subjects.model_dump()['subjects']
    semester = subjects.model_dump()['semester']
    ls = [] #수강한 과목을 담아주는 리스트
    for i in request:
        ls.append(i)
    recommend_subject = recommend.recommend_subject(semester, ls)
    return recommend_subject

#봉사추천서비스
@router.get('/submit-volunteer')
async def submit_volunteer():
    ls = []
    for _ in range(3):
        recommend_volunteer = recommend.recommend_vol()
        ls.append(recommend_volunteer)
    return ls

#자격증 추천
@router.post("/submit-certification")
async def submit_certification(certification : task_schema.Certification):
    request = certification.model_dump()['certification']
    my_score = certification.model_dump()['my_score']
    response = recommend.recommend_certification(my_score)
    print(response)
    return response

#채용정보, 추천서비스
@router.post('/submit-work')
async def submit_work(work : task_schema.Work):
    request = work.model_dump()['work']
    print(request)
    recommend_work = recommend.recommend_work(request)
    return recommend_work
    
#학교활동 추천서비스
@router.get('/submit-activation')
async def submit_activation():
    recommend_activation = recommend.recommend_activation()
    return recommend_activation