## pronunciation-evaluator

### What is this?
- **IPA 문자열에 대하여 발음 속성을 바탕으로 유사도를 반환하는 함수**이다.
- 현재, 문자열을 비교하는 평가 지표는 CER, WER 등 다양하다.
- 해당 평가 지표들은 각각의 Character 또는 Word 단위에서 한 글자만 틀리게 되어도 아예 다른 문자로 인식한다.
- 이러한 상황에서 발음에 대한 유사도가 필요하여 주어진 문자에 대하여 11 개의 속성으로 벡터화하여 유사도를 계산하도록 하였다.
  - ex) `조음 위치`, `조음 방법`, `조음 강도`, `유성음 여부`, `입술 모양` 등

### Examples
- 발음 단위로 `11 개에 대한 속성`으로 벡터화 진행
  - `자음 조음위치`, `자음 조음방법`, `자음 조음강도`, `자음 유성음여부`, `모음 조음상하위치`, `모음 조음좌우위치`, `모음 입술모양`, `받침자음 조음위치`, `받침자음 조음방법`, `받침자음 조음강도`, `받침자음 유성음여부`
  
  - 다음 그래프와 같이 표현할 수 있음.
    ```python
    values, types, origs = mapping_ipa_with_value("ɑnnjʌŋɑsɛjo")
    vector_values, vector_types, vector_origs = vectorize_ipa(values, types, origs)
    plt.plot(vector_values)
    ```
    ![1](https://github.com/DevTae/pronunciation-evaluator/assets/55177359/0fee58b3-8ee0-4922-b7e9-439f6f25d8f5)

    
- 각 벡터에 대한 수치를 활용하여 가장 유사한 부분집합을 바탕으로 채점 진행
  - `동적계획법 (Dynamic Programming)` 활용
  ```python
  { 'answer_ipa': '정답 IPA', 'user_ipa': '유저 IPA', 'score': "전체 점수",
    'summary': "각 매핑된 부분에 대한 피드백 제공" }
  ```
  ![3](https://github.com/DevTae/pronunciation-evaluator/assets/55177359/7457ff1d-974b-4ecf-bba4-e032ba72e6c1)


- 채점 기준
  - 발음 단위를 기준으로 `11개에 대한 속성` 에 대한 유사도 계산
  - 동적계획법 바탕으로 최대 평균값 구할 때, `매핑되는 입력 문자열과 정답 문자열에 대한 길이` 비교


- pronunciation-evaluator 적용 예시
  - 다음과 같이 적용할 수 있음.
    
  ![4](https://github.com/DevTae/pronunciation-evaluator/assets/55177359/478e2f74-a5bc-4ad4-9816-3e4ddb1d1a0b)


### Reference
- https://github.com/stannam/hangul_to_ipa
- https://github.com/mphilli/English-to-IPA
- http://pronunciation.cs.pusan.ac.kr/
- https://ko.wikipedia.org/wiki/%EA%B5%AD%EC%A0%9C_%EC%9D%8C%EC%84%B1_%EA%B8%B0%ED%98%B8
