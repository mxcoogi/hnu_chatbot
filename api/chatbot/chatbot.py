from api.chatbot.common import client, model
import math
import api.db_manager as db_manager
class Chatbot:
    
    def __init__(self, model, system_role, instruction, **kwargs):
        self.context = [{"role": "system", "content": system_role}]
        self.model = model
        self.instruction = instruction
        self.max_token_size = 16*1024
        self.available_token_rate = 0.9
        self.user = kwargs["user"]
        self.assistant = kwargs["assistant"]
        self.memoryManager = db_manager.MemoryManager()
        self.context.extend(self.memoryManager.restore_chat())
    

    def add_user_message(self, user_message):
        self.context.append({"role": "user", "content": user_message, "saved" : False})

    def _send_request(self):
        try:
            response = client.chat.completions.create(
                model=self.model, 
                messages=self.to_openai_context(),
                temperature=0.5,
                top_p= 1,
                max_tokens=256,
                frequency_penalty=0,
                presence_penalty=0
            ).model_dump()
        except Exception as e:
            print(f"Exception 오류 ({type(e)}) 발생:{e}")
        return response
    
    def to_openai_context(self):
        return [{"role" : v["role"], "content":v["content"]}  for v in self.context]

    def save_chat(self):
        self.memoryManager.save_chat(self.context)

        
    def send_request(self):
        self.context[-1]['content'] += self.instruction
        return self._send_request()

    def add_response(self, response):
        self.context.append({
                "role" : response['choices'][0]['message']["role"],
                "content" : response['choices'][0]['message']["content"],
                "saved" : False
            }
        )

    def get_response_content(self):
        return self.context[-1]['content']

    def clean_context(self):
        for idx in reversed(range(len(self.context))):
            if self.context[idx]["role"] == "user":
                self.context[idx]["content"] = self.context[idx]["content"].split("instruction:\n")[0].strip()
                break
    
    def handle_token_limit(self,response):
        try:
            current_usage_rate = response['usage']['total_tokens'] / self.max_token_size
            exceeded_token_rate = current_usage_rate - self.available_token_rate
            if exceeded_token_rate > 0:
                remove_size = math.ceil(len(self.context) / 10)
                self.context = [self.context[0] + self.context[remove_size+1:]]
        except Exception as e:
            print(f"handle_token_limit exception:{e}")

"""if __name__ == "__main__":
    # step-3: 테스트 시나리오에 따라 실행 코드 작성 및 예상 출력결과 작성
    chatbot = Chatbot(model.basic)

    chatbot.add_user_message("Who won the world series in 2020?")

    # 시나리오1-4: 현재 context를 openai api 입력값으로 설정하여 전송
    response = chatbot.send_request()

    # 시나리오1-5: 응답 메시지를 context에 추가
    chatbot.add_response(response)

    # 시나리오1-7: 응답 메시지 출력
    print(chatbot.get_response_content())

    # 시나리오2-2: 사용자가 채팅창에 "Where was it played?" 입력
    chatbot.add_user_message("Where was it played?")

    # 다시 요청 보내기
    response = chatbot.send_request()

    # 응답 메시지를 context에 추가
    chatbot.add_response(response)

    # 응답 메시지 출력
    print(chatbot.get_response_content())"""