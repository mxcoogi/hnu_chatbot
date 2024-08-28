import api.db_manager as db_manager


#과목추천서비스
def recommend_subject(semester,subject):
    all_subject = db_manager.subject #과목전부 가져와야함
    no_subject = []
    
    for i in all_subject:
        if i['개설학기'] == semester:
            no_subject.append(i)

    return no_subject

#채용정보 추천
def recommend_work(my_stack):
    response = []
    for i in my_stack:
        res = db_manager.mongo_work_collectin[i].find_one()
        if res is not None:
            res['_id'] = str(res['_id'])
            response.append(res)
        else:
            # None인 경우 처리 (예: 로그 출력 또는 빈 딕셔너리 추가)
            print(f"No document found for stack: {i}")
            response.append({})
    return response

#봉사추천
def recommend_vol():
    vols = db_manager.mongo_graduation['봉사'].aggregate([{"$sample": {"size": 1}}]).next()
    vols['_id']  =  str(vols['_id'])
    print(vols)
    return vols
#자격증 추천
def recommend_certification(my_score):
    res = 1000 - my_score
    three = res // 300
    two = (res % 300) // 200
    one = ((res % 300) % 200) // 100
    ls = [("100", one), ("200", two), ("300", three)]
    print(one, two, three)
    res = []
    for i in ls:
        score = i[0]
        unit = i[1]
        pipeline =[
            {"$match" : {"점수" : score}},
            {"$sample" :{"size" : unit} }
        ]
        res += list(db_manager.mongo_graduation['자격증'].aggregate(pipeline))
    for j in res:
        j['_id'] = str(j['_id'])
    return res

#학교활동추천
def recommend_activation():
    event = db_manager.event
    return event