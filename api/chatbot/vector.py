from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher

def vector_find_most_similar(input_word, word_list):
    # 벡터화 할 문장 리스트 (입력 단어 + 후보 단어 리스트)
    sentences = [input_word] + word_list
    
    # TF-IDF 벡터라이저 초기화 및 문장 벡터화
    vectorizer = TfidfVectorizer().fit_transform(sentences)
    
    # 입력 단어 벡터와 각 후보 단어 벡터 간의 코사인 유사도 계산
    cosine_similarities = cosine_similarity(vectorizer[0:1], vectorizer[1:]).flatten()
    
    # 가장 유사한 단어의 인덱스 찾기
    most_similar_index = cosine_similarities.argmax()
    
    # 가장 유사한 단어 반환
    return word_list[most_similar_index]


def find_most_similar(query, elements):
    """
    주어진 쿼리와 가장 관련 있는 요소를 리스트에서 찾아줍니다.
    
    Args:
        query (str): 검색할 쿼리
        elements (list): 요소들이 포함된 리스트
    
    Returns:
        str: 가장 관련 있는 요소
    """
    most_similar_element = None
    highest_similarity = 0
    
    for element in elements:
        similarity = SequenceMatcher(None, query, element).ratio()
        if similarity > highest_similarity:
            highest_similarity = similarity
            most_similar_element = element
    
    return most_similar_element

