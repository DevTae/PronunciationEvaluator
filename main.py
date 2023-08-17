# Developed by DevTae@2023

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 자음 기준 (중요성 있는 순서대로 나열)
# 1. 조음 위치, 유성음 여부
# 2. 조음 방법, 조음 강도

# Position (Bilabial) -0.5 --- 0.5 (Glottal)
conso_pos = { "Bilabial": -0.5, "Alveolar": -0.25, "Alveo-Palatal": 0, "Velar": 0.25, "Glottal": 0.5 }
# HowToPronunce (Plosive) 0.75 --- -0.25 (Lateral)
# 파열음(ㅂ, ㅍ, ㅃ, ㄷ, ㅌ, ㄸ, ㄱ, ㅋ, ㄲ), 마찰음(ㅅ, ㅆ, ㅎ), 파찰음(ㅈ, ㅊ, ㅉ), 비음(ㅁ, ㄴ, ㅇ), 유음(ㄹ)
conso_how = { "Plosive": 0.75, "Fricative": 0.25, "Affricate": 0.5, "Nasal": 0, "Lateral": -0.25 }
# Strength (Lenis) 0 --- 1 (Fortis)
conso_str = { "Lenis": 0, "Aspirated": 0.5, "Fortis": 1 }
# Voice or not (Yes) 0.5 --- -0.5 (No)
# 유성음인지 아닌지 구분
conso_voi = { "Yes": 0.5, "No": -0.5 }

consonants = pd.read_csv("csv/consonants.csv")
consonants["조음강도"] = consonants["조음강도"].replace("None", "Lenis") # None -> Lenis
consonants = consonants.fillna("Lenis")

# 모음 기준 (중요성 있는 순서대로 나열)
# 1. 입술 모양
# 2. 조음 좌우 위치, 조음 상하 위치

# shape (Unrounded) -0.5 --- 0.5 (Rounded)
vowel_shp = { "Unrounded": -0.5, "Rounded+Unrounded": -0.17, "Unrounded+Rounded": 0.17, "Rounded": 0.5 }
# width position (Front) -0.5 --- 0.5 (Back)
vowel_wps = { "Front": -0.5, "NearFront": -0.4, "Back+Front": -0.17, "Front+Back": 0.17, "NearBack": 0.4, "Back": 0.5 }
# height position (Low) -0.5 --- 0.5 (High)
vowel_hps = { "Low": -0.5, "NearLow": -0.4, "Mid+Low": -0.3, "High+Low": -0.1, "Mid": 0, "High+Mid": 0.2, "NearHigh" : 0.4, "High": 0.5 }

vowels = pd.read_csv("csv/vowels.csv")


# data 에서 각 IPA 문자에 대응되는 수치를 저장한다.
def mapping_ipa_with_value(data):
    values = []
    types = []
    origs = []
    idx = 0
    while idx < len(data):
        ch = data[idx]
        skip = True
        for ipa in list(consonants["IPA"]):
            if data[idx:idx+len(ipa)] == ipa:
                skip = False
                conso_pos_ = conso_pos[consonants.loc[consonants["IPA"] == ipa]["조음위치"].iloc[0]]
                conso_how_ = conso_how[consonants.loc[consonants["IPA"] == ipa]["조음방법"].iloc[0]]
                conso_str_ = conso_str[consonants.loc[consonants["IPA"] == ipa]["조음강도"].iloc[0]]
                conso_voi_ = conso_voi[consonants.loc[consonants["IPA"] == ipa]["유성음여부"].iloc[0]]
                value = [conso_pos_, conso_how_, conso_str_, conso_voi_]
                values.append(value)
                if ipa == "ŋ": # 받침이 있는 경우, 'C' 가 아닌 'c' 로 등록하여 이후 처리에 반영한다.
                    types.append("c") # Consonants (받침)
                else:
                    types.append("C") # Consonants
                origs.append(ipa)
                idx += len(ipa)
        for ipa in list(vowels["IPA"]):
            if data[idx:idx+len(ipa)] == ipa:
                skip = False
                vowel_shp_ = vowel_shp[vowels.loc[vowels["IPA"] == ipa]["입술모양"].iloc[0]]
                vowel_wps_ = vowel_wps[vowels.loc[vowels["IPA"] == ipa]["조음좌우위치"].iloc[0]]
                vowel_hps_ = vowel_hps[vowels.loc[vowels["IPA"] == ipa]["조음상하위치"].iloc[0]]
                value = [vowel_shp_, vowel_wps_, vowel_hps_]
                values.append(value)
                types.append("V") # Vowels
                origs.append(ipa)
                idx += len(ipa)
        if skip == True:
            idx += 1
    return values, types, origs

# 자음과 모음이 한 발음 단위로 나뉘도록 분할
def split_types(types):
    result = []
    
    while len(types) > 0:
        if types.startswith("CVCC") or types.startswith("CVc") or types.startswith("CVCc"):
            result.append(types[:3])
            types = types[3:]
        elif types.startswith("CVCV") or types.startswith("CVV") or types.startswith("VCC") or types.startswith("Vc"):
            result.append(types[:2])
            types = types[2:]
        elif types.startswith("VCV") or types.startswith("VV") or types.startswith("cV") or types.upper().startswith("CC"):
            result.append(types[:1])
            types = types[1:]
        else:
            result.append(types[:])
            types = ""
    
    return result

# C+V 단위 Vectorization 진행
# [0] conso_pos
# [1] conso_how
# [2] conso_str
# [3] conso_voi
# [4] vowel_shp
# [5] vowel_wps
# [6] vowel_hps
# [7] support_conso_pos
# [8] support_how
# [9] support_str
# [10] support_voi
def vectorize_ipa(values, types, origs):
    vector_values = []
    vector_types = []
    vector_origs = []
    prev_type = None
    
    # C+V 단위 Vectorization
    types_after = split_types(''.join(types))
    
    idx = 0
    for types_ in types_after:
        vector_value = []
        vector_orig = []
        
        if types_ == "CVC" or types_ == "CVc":
            vector_value += values[idx]
            vector_value += values[idx+1]
            vector_value += values[idx+2]
            vector_orig.append(origs[idx])
            vector_orig.append(origs[idx+1])
            vector_orig.append(origs[idx+2])
        elif types_ == "CV":
            vector_value += values[idx]
            vector_value += values[idx+1]
            vector_value += [0, 0, 0, 0]
            vector_orig.append(origs[idx])
            vector_orig.append(origs[idx+1])
        elif types_ == "VC" or types_ == "Vc":
            vector_value += [0, 0, 0, 0]
            vector_value += values[idx]
            vector_value += values[idx+1]
            vector_orig.append(origs[idx])
            vector_orig.append(origs[idx+1])
        elif types_ == "V":
            vector_value += [0, 0, 0, 0]
            vector_value += values[idx]
            vector_value += [0, 0, 0, 0]
            vector_orig.append(origs[idx])
        elif types_ == "C":
            vector_value += values[idx]
            vector_value += [0, 0, 0]
            vector_value += [0, 0, 0, 0]
            vector_orig.append(origs[idx])
        elif types_ == "c":
            vector_value += [0, 0, 0, 0]
            vector_value += [0, 0, 0]
            vector_value += values[idx]
            vector_orig.append(origs[idx])
        else:
            print(types_after)
            print(types_)
            raise Exception("types_ 에 대하여 예기치 못한 입력값이 들어왔습니다.")
        
        vector_type = types_
        vector_values.append(vector_value)
        vector_types.append(vector_type)
        vector_origs.append(vector_orig)
        idx += len(types_)

    return vector_values, vector_types, vector_origs

# 두 value 사이에서의 score 를 구하는 함수 (1차원) (default)
def get_score_1d(values_ans, values_usr):
    assert isinstance(values_ans, list), "1차원 리스트에 대한 입력값만 지원합니다"
    assert not isinstance(values_ans[0], list), "1차원 리스트에 대한 입력값만 지원합니다"
    assert isinstance(values_usr, list), "1차원 리스트에 대한 입력값만 지원합니다"
    assert not isinstance(values_usr[0], list), "1차원 리스트에 대한 입력값만 지원합니다"
    
    # value_1 과 value_2 의 원소 배열 크기가 다른 경우, max distance (=1) 반환함.
    if len(values_ans) != len(values_usr):
        return 0 # min score 반환
    
    sum_score = 0
    cnt_score = 0
    
    for idx in range(len(values_ans)):
        distance = abs(values_usr[idx] - values_ans[idx])
        sum_score += (1 - distance) ** 2 # 거듭제곱 형식으로 정답보다 멀수록 점수를 더 차감하는 방식
        cnt_score += 1
    
    return (sum_score / cnt_score) ** 2 # 거듭제곱 형식으로 정답보다 멀수록 점수를 더 차감하는 방식

# values_1 과 values_2 에 대한 서로 대응하는 distance 를 계산한다.
# types_1 : answer, types_2 : user_input
def get_scores(values_ans, types_ans, values_usr, types_usr):
    scores = np.zeros((len(types_ans), len(types_usr)), dtype=float)
    
    for i in range(len(types_ans)):
        for j in range(len(types_usr)):
            scores[i][j] = get_score_1d(values_ans[i], values_usr[j])
            
    return scores

# 두 values 사이에서 score 채점 진행 (동적계획법 활용)
def get_score(answer_ipa, user_ipa, option="default"):
    values_ans, types_ans, origs_ans = mapping_ipa_with_value(answer_ipa)
    values_ans, types_ans, origs_ans = vectorize_ipa(values_ans, types_ans, origs_ans)
    values_usr, types_usr, origs_usr = mapping_ipa_with_value(user_ipa)
    values_usr, types_usr, origs_usr = vectorize_ipa(values_usr, types_usr, origs_usr)
    
    scores = get_scores(values_ans, types_ans, values_usr, types_usr)
    avg_of_scores = np.zeros((len(types_ans) + 1, len(types_usr) + 1), dtype=float)
    cnt_of_directions = np.zeros((len(types_ans) + 1, len(types_usr) + 1), dtype=float) # direction counting
    directions = np.empty((len(types_ans) + 1, len(types_usr) + 1), dtype='U') # best path 의 방향 저장

    # 기본 설정
    avg_of_scores[:,0] = 0
    avg_of_scores[0,:] = 0
    for i in range(1, len(types_ans) + 1):
        cnt_of_directions[i][0] = i - 1
    
    # 평균이 최대가 되는 경우를 찾게 됨
    for i in range(1, len(types_ans) + 1):
        for j in range(1, len(types_usr) + 1):
            # right 두 개로 하나를 채우는 것이기 때문에 cnt 2 증가
            expected_right = (avg_of_scores[i][j-1] * cnt_of_directions[i][j-1] + scores[i-1][j-1]) / (cnt_of_directions[i][j-1] + 2)
            if avg_of_scores[i][j] < expected_right:
                avg_of_scores[i][j] = expected_right
                cnt_of_directions[i][j] = cnt_of_directions[i][j-1] + 2
                directions[i][j] = "r"
            
            # bottom 하나로 두 개를 떼우려는 것이기에 cnt 3 증가
            expected_bottom = (avg_of_scores[i-1][j] * cnt_of_directions[i-1][j] + scores[i-1][j-1]) / (cnt_of_directions[i-1][j] + 3)
            if avg_of_scores[i][j] < expected_bottom:
                avg_of_scores[i][j] = expected_bottom
                cnt_of_directions[i][j] = cnt_of_directions[i-1][j] + 3
                directions[i][j] = "b"
            
            # diagonal
            expected_diagonal = (avg_of_scores[i-1][j-1] * cnt_of_directions[i-1][j-1] + scores[i-1][j-1]) / (cnt_of_directions[i-1][j-1] + 1)
            if avg_of_scores[i][j] < expected_diagonal:
                avg_of_scores[i][j] = expected_diagonal
                directions[i][j] = "d"
                cnt_of_directions[i][j] = cnt_of_directions[i-1][j-1] + 1
     
    # score 계산 및 score 가 최대가 되는 i(=answer), j(=user) 계산
    i = len(types_ans)
    j = min(i, len(types_usr))
    max_score = 0
    for j_ in range(i, len(types_usr) + 1):
        score = avg_of_scores[i][j_]
        if score > max_score:
            max_score = score
            j = j_
    
    # score 최댓값
    score = avg_of_scores[i][j]
    
    if option == "score":
        return score
    elif option == "default":
        # score 최댓값이 나오게 하는 path 파악
        result_dict = dict()
        result_dict["answer_ipa"] = answer_ipa
        result_dict["user_ipa"] = user_ipa
        result_dict["score"] = score
        result_dict["summary"] = []
        
        answer_ipa_splited = []
        user_ipa_splited = []
        per_scores = []
        
        while True:
            direction = directions[i][j]
            
            if direction == '':
                break
            
            answer_ipa_splited.append(origs_ans[i-1])
            user_ipa_splited.append(origs_usr[j-1])
            per_scores.append(scores[i-1][j-1])
            
            if direction == 'r':
                j -= 1
            elif direction == 'b':
                i -= 1
            elif direction == 'd':
                i -= 1
                j -= 1

        # 전체 정답 중에서 중간부터 채점한 게 높을 땐, 이전 문제 채점도 추가.
        while i > 0:
            answer_ipa_splited.append(origs_ans[i-1])
            user_ipa_splited.append([])
            per_scores.append(0)
            i -= 1  
        
        for answer_ipa_char, user_ipa_char, per_score in zip(answer_ipa_splited, user_ipa_splited, per_scores):
            result_dict["summary"].append([answer_ipa_char, user_ipa_char, per_score])
            
        result_dict["summary"].reverse() 

        return result_dict

if __name__ == "__main__":
    print(get_score("ɑnnjʌŋɑsɛjo", "ɑnnjjmassɛjjo"))
