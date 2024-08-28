from api.chatbot.common import client, model
import json
import requests
from pprint import pprint 
from tavily import TavilyClient
import api.key as key
from api.db_manager import mongo_hnu_collection, mongo_hnu_collection2, mongo_introduce
from api.chatbot.vector import find_most_similar
tavily = TavilyClient(api_key=key.tavil_key)
from pinecone import Pinecone

pc = Pinecone(api_key=key.pinecone_key)
index = pc.Index("vectordb")

#위도 경도
global_lat_lon = { 
           '서울':[37.57,126.98],'강원도':[37.86,128.31],'경기도':[37.44,127.55],
           '경상남도':[35.44,128.24],'경상북도':[36.63,128.96],'광주':[35.16,126.85],
           '대구':[35.87,128.60],'대전':[36.35,127.38],'부산':[35.18,129.08],
           '세종시':[36.48,127.29],'울산':[35.54,129.31],'전라남도':[34.90,126.96],
           '전라북도':[35.69,127.24],'제주도':[33.43,126.58],'충청남도':[36.62,126.85],
           '충청북도':[36.79,127.66],'인천':[37.46,126.71],
           'Boston':[42.36, -71.05],
           '도쿄':[35.68, 139.69]
          }

def get_celsius_temperature(**kwargs):
    location = kwargs['location']
    lat_lon = global_lat_lon.get(location, None)
    if lat_lon is None:
        return None
    lat = lat_lon[0]
    lon = lat_lon[1]

    # API endpoint
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"

    # API를 호출하여 데이터 가져오기
    response = requests.get(url)
    # 응답을 JSON 형태로 변환
    data = response.json()
    # 현재 온도 가져오기 (섭씨)
    temperature = data['current_weather']['temperature']

    print("temperature:",temperature) 
    return temperature


def search_internet(**kwargs):
    print("search_internet",kwargs)
    answer = tavily.search(query=kwargs['search_query'], include_answer=True)['answer']
    return answer

def search_hnu(**kwargs):
    print("search_hnu", kwargs)
    input_word = kwargs['search_query']
    print(input_word)
    db = mongo_hnu_collection.find()
    ls = []
    for i in db:
        ls.append(i['제목'])

    res = find_most_similar(input_word, ls)
    res2 = mongo_hnu_collection.find_one({'제목' : res})
    return res2

def search_date(**kwargs):
    print("search_date", kwargs)
    input_word = kwargs['search_query']    
    month=["3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월", "1월", "2월", "전체일정","1학기 학사일정", "2학기 학사일정"]
    input_word = find_most_similar(input_word, month)
    print(input_word)

    res2 = mongo_hnu_collection2.find_one({"제목" : input_word})
    return res2
    
def introduce_department(**kwargs):
    print("search_date", kwargs)
    input_word = kwargs['search_query']
    input_word = find_most_similar(input_word, ["학과소개", "교수소개"])
    res = mongo_introduce.find_one({"제목" : input_word})
    return res



tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_celsius_temperature",
                    "description": "지정된 위치의 현재 섭씨 날씨 확인",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "광역시도, e.g. 서울, 경기",
                            }
                        },
                        "required": ["location"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "search_internet",
                    "description": "답변 시 인터넷 검색이 필요하다고 판단되는 경우 수행",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "search_query": {
                                "type": "string",
                                "description": "인터넷 검색을 위한 검색어",
                            }
                        },
                        "required": ["search_query"],
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_hnu",
                    "description": "공지사항이 필요하다 판단될 시 수행",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "search_query": {
                                "type": "string",
                                "description": "학교공지 , 학사공지, 장학공지",
                            }
                        },
                        "required": ["search_query"],
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_date",
                    "description": "답변 시 일정 관련이 필요하다 판단될 시 수행",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "search_query": {
                                "type": "string",
                                "description": "월, e.g. 1월 ~ 12월, 전체일정",
                            }
                        },
                        "required": ["search_query"],
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "introduce_department",
                    "description": "답변 시 컴퓨터공학과(학과) 소개해야 될 경우 수행",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "search_query": {
                                "type": "string",
                                "description": "학과소개, 교수소개, 교수소개시 교수들 앞에 좋은 수식언 붙이기",
                            }
                        },
                        "required": ["search_query"],
                    }
                }
            },
            
        ]


class FunctionCalling:
    
    def __init__(self, model):
        self.available_functions = {
            "get_celsius_temperature": get_celsius_temperature,
            "search_internet": search_internet,
            "search_hnu" : search_hnu,
            "search_date" : search_date,
            "introduce_department" : introduce_department,
        }
        self.model = model


    def analyze(self, user_message, tools):
        try:
            response = client.chat.completions.create(
                    model=model.basic,
                    messages=[{"role": "user", "content": user_message}],
                    tools=tools,
                    tool_choice="auto", 
                )
            message = response.choices[0].message
            message_dict = message.model_dump() 
            pprint(("message_dict=>", message_dict))
            return message, message_dict
        except Exception as e:
            print("Error occurred(analyze):",e)
        

    def run(self, analyzed, analyzed_dict, context):
        context.append(analyzed)
        tool_calls = analyzed_dict['tool_calls']
        for tool_call in tool_calls:
            function = tool_call["function"]
            func_name = function["name"] 
            func_to_call = self.available_functions[func_name]        
            try:
                func_args = json.loads(function["arguments"])
                # 챗GPT가 알려주는 매개변수명과 값을 입력값으로하여 실제 함수를 호출한다.
                func_response = func_to_call(**func_args)
                context.append({
                    "tool_call_id": tool_call["id"],
                    "role": "tool",
                    "name": func_name, 
                    "content": str(func_response)
                })
            except Exception as e:
                print("Error occurred(run):",e)
    
        return client.chat.completions.create(model=self.model,messages=context).model_dump()    