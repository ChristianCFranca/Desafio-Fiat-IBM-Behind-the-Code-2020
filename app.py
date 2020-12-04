from flask import Flask, request, jsonify

import json

from ibm_watson import NaturalLanguageUnderstandingV1, SpeechToTextV1
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

import os

# Inicialização do app, das API Keys e todas as strings necessárias à conexão ao serviço ----------------------------------------------------

app = Flask(__name__)

# Pegamos a porta da variavel de ambiente PORT
port = int(os.getenv('PORT', 8000))

# Natural Language Understanding
nlu_apikey = "NyDMAj43hZvu1T-vWbz-evJgiYhZZZwR3_bLO1-y0P7f"
nlu_service_url = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/7e56160b-4784-41fb-8d56-193a3b3c7fec"  
nlu_entity_model = "4f0c3f0d-d6ec-4723-a3ae-1868a6435c69"

# Speech-to-Text
stt_apikey = "HfKqTA4ixXjPkNfKNSFcK6P-ATgmGuhXIqOTOxhO0RYM"
stt_service_url = "https://api.us-south.speech-to-text.watson.cloud.ibm.com/instances/c787c51d-d355-48a4-898e-96e61da2d7ad"
stt_entity_model = 'pt-BR_BroadbandModel'

# ---------------------------------------------------------------------------------------------------------------------------------------------------

def restructure_nlu_json_result(json_response):
    entities = []
    for entity_object in json_response['entities']:
        sentiment_score = entity_object['sentiment']['score']
        entity = entity_object['type']
        mention = entity_object['text']

        entities.append({"entity": entity, "sentiment": sentiment_score, "mention": mention})

    if len(entities) == 0:
        return None

    return entities

def get_worst_entity_data(json_response):
    priority_dict = {"SEGURANCA": 0, "CONSUMO": 1, "DESEMPENHO": 2, "MANUTENCAO": 3, "CONFORTO": 4, "DESIGN": 5, "ACESSORIOS": 6}
    types_score_dict = {}
    conflicted_types = []

    worst_entity_text = None
    worst_entity_type = None
    worst_score = None

    for entity_object in json_response['entities']:
        # Ignoramos o modelo
        if entity_object['type'] == "MODELO":
            continue

        score = entity_object['sentiment']['score']
        label = entity_object['sentiment']['label']
        entity = entity_object['type']
        text = entity_object['text']

        if label == "negative":
            if worst_score is None:
                worst_score = score
                worst_entity_type = entity
                worst_entity_text = text

            if entity in types_score_dict:
                if score < types_score_dict[entity]:
                    types_score_dict[entity] = score
            else:
                types_score_dict[entity] = score

            if score <= worst_score:
                worst_entity_type = entity
                worst_entity_text = text
                worst_score = score
    
    #print("Pior Encontrado Final: ", worst_entity_type)
    #print(types_score_dict)
    types_score_dict = {key: abs(types_score_dict[key] - worst_score) < 0.1 if key != worst_entity_type else types_score_dict[key] for key in types_score_dict.keys()}
    #print(types_score_dict)
    conflicted_types.append(worst_entity_type)
    for key in types_score_dict.keys():
        if types_score_dict[key] and key != worst_entity_type:
            conflicted_types.append(key)

    if len(conflicted_types) == 1:
        return worst_entity_type, worst_entity_text, worst_score
    else:
        #print(conflicted_types)
        priority_list = [priority_dict[conflicted_type] for conflicted_type in conflicted_types]
        worst_entity_type = conflicted_types[priority_list.index(min(priority_list))]
        return worst_entity_type, worst_entity_text, worst_score

def get_recommendation(carro, worst_entity, list_of_jsons):
    base_recommendation_dict = {"SEGURANCA": "TORO", 
                                "CONSUMO": "ARGO", 
                                "DESEMPENHO": "TORO", 
                                "MANUTENCAO": "FIORINO", 
                                "CONFORTO": "TORO", 
                                "DESIGN": "ARGO", 
                                "ACESSORIOS": "RENEGADE"}

    same_recommendation_dict = {"SEGURANCA": "CRONOS", 
                                "CONSUMO": "TORO", 
                                "DESEMPENHO": "ARGO", 
                                "MANUTENCAO": "TORO", 
                                "CONFORTO": "MAREA", 
                                "DESIGN": "CRONOS", 
                                "ACESSORIOS": "DUCATO"}

    sentimento_geral = 0
    for objeto in list_of_jsons:
        sentimento_geral += objeto['sentiment']

    if sentimento_geral > 0:
        return ""

    try: return base_recommendation_dict[worst_entity] if base_recommendation_dict[worst_entity] != carro else same_recommendation_dict[worst_entity]
    except: return ""

@app.route('/')
def hello_desafio8():
    return "Olá Desafio 8, vim pra te conquistar!"

@app.route('/recommendation', methods=['POST'])
def recommendation():
    json_final = {"recommendation": "", "entities": []}
    carro = None
    text = None
    audio_file = None
    restructured_json_entities_list = None
    worst_entity_type = None
    worst_entity_text = None
    worst_score = None

    if "car" in request.form.keys():
        carro = request.form.get("car").upper()
        if not isinstance(carro, str):
            return jsonify(json_final), 200

    if "text" in request.form.keys():
        text = request.form.get("text")

    elif "audio" in request.files.keys():
        audio_file = request.files.get("audio").read() # Bytes
        stt_response = stt_service.recognize(
                            audio=audio_file,
                            content_type='audio/flac',
                            model=stt_entity_model,
                            timestamps=False,
                            word_confidence=False
                            )
        stt_response = stt_response.get_result()
        text = stt_response['results'][0]['alternatives'][0]['transcript']

    if text:
        nlu_response = nlu_service.analyze(
                            text=text,
                            features=Features(entities=EntitiesOptions(model=nlu_entity_model, sentiment=True)),
                            language='pt'
                        )
        nlu_response = nlu_response.get_result()

        restructured_json_entities_list = restructure_nlu_json_result(nlu_response)
        worst_entity_type, worst_entity_text, worst_score = get_worst_entity_data(nlu_response)

    if restructured_json_entities_list:
        recommendation = get_recommendation(carro, worst_entity_type, restructured_json_entities_list)
        json_final['recommendation'] = recommendation
        json_final['entities'] = restructured_json_entities_list

    #if worst_entity_type:
        #json_final['piorEntity'] = worst_entity_text
        #json_final['piorScore'] = worst_score
        #json_final['prioridadeDeMelhora'] = worst_entity_type

    return jsonify(json_final), 200


nlu_authenticator = IAMAuthenticator(apikey=nlu_apikey)
nlu_service = NaturalLanguageUnderstandingV1(version='2018-03-16', authenticator=nlu_authenticator)
nlu_service.set_service_url(nlu_service_url)

stt_authenticator = IAMAuthenticator(apikey=stt_apikey)
stt_service = SpeechToTextV1(authenticator=stt_authenticator)
stt_service.set_service_url(stt_service_url)


#if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=port)