import json
import logging

import requests

from typing import Dict, Any, Optional, List

from rasa_nlu.model import Interpreter


logger = logging.getLogger(__file__)


class RasaNluEntity():
    def __init__(self,
                 name: str = '',
                 value: str = '',
                 start: int = -1,
                 end: int = -1,
                 confidence: float = 0,
                 extractor: str = '') -> None:
        # entity name
        self.name = name
        # entity value
        self.value = value
        self.start = start
        self.end = end
        self.confidence = confidence
        self.extractor = extractor


    def from_dict(self,
                  json_obj: Dict[str, Any]) -> None:
        # NOTE: to be consistent with RasaNLU output, the key is 'entity' for
        # the entity name
        self.name = json_obj.get('entity', '')
        self.value = json_obj.get('value', '')
        self.start = json_obj.get('start', -1)
        self.end = json_obj.get('end', -1)
        self.confidence = json_obj.get('confidence', 0)


    def to_dict(self) -> Dict[str, Any]:
        json_obj: Dict[str, Any] = {
            'entity': self.name,
            'value': self.value,
            'start': self.start,
            'end': self.end,
            'confidence': self.confidence,
            'extractor': self.extractor
        }
        return json_obj


class RasaNluIntent():
    def __init__(self,
                 name: str = '',
                 confidence: float = 0) -> None:
        self.name = name
        self.confidence = confidence


    def from_dict(self,
                  json_obj: Dict[str, Any]) -> None:
        self.name = json_obj.get('name', '')
        self.confidence = json_obj.get('confidence', 0)


    def to_dict(self) -> Dict[str, Any]:
        json_obj: Dict[str, Any] = {
            'name': self.name,
            'confidence': self.confidence
        }
        return json_obj


class RasaNluResponse():
    def __init__(self) -> None:
        """Constructor."""
        self.status_code: int = -1
        self.project: str = ''
        self.model: str = ''
        self.text: str = ''
        self.intent: Optional[RasaNluIntent] = None
        self.intent_ranking: List[RasaNluIntent] = []
        self.entities: List[RasaNluEntity] = []


    def from_dict(self,
                  json_obj: Dict[str, Any]) -> None:
        self.project = json_obj.get('project', '')
        self.status_code = int(json_obj.get('status_code', '-1'))
        self.model = json_obj.get('model', '')
        self.text = json_obj.get('text', '')
        for entity_dict in json_obj.get('entities', []):
            entity_obj = RasaNluEntity()
            entity_obj.from_dict(entity_dict)
            self.entities.append(entity_obj)
        if 'intent' in json_obj:
            self.intent = RasaNluIntent()
            self.intent.from_dict(json_obj['intent'])
        for intent_ranking_dict in json_obj.get('intent_ranking', []):
            intent_ranking_obj = RasaNluIntent()
            intent_ranking_obj.from_dict(intent_ranking_dict)
            self.intent_ranking.append(intent_ranking_obj)


    def to_dict(self) -> Dict[str, Any]:
        json_obj: Dict[str, Any] = {
            'status_code': self.status_code,
            'project': self.project,
            'model': self.model,
            'text': self.text
        }
        if self.intent:
            json_obj['intent'] = self.intent.to_dict()
        if self.intent_ranking:
            json_obj['intent_ranking'] = [
                intent.to_dict()
                for intent in self.intent_ranking
            ]
        if self.entities:
            json_obj['entities'] = [
                entity.to_dict()
                for entity in self.entities
            ]
        return json_obj


def rasa_nlu_annotate(text: str,
                      rasa_nlu_url: str,
                      project: str,
                      model: str) -> RasaNluResponse:

    rasa_nlu_response = RasaNluResponse()

    request_json = dict(
        q=text,
        project=project
    )
    if model:
        request_json['model'] = model
    response: requests.Response = requests.post(rasa_nlu_url + '/parse', json=request_json)
    response.raise_for_status()
    rasa_nlu_response.from_dict(response.json())

    return rasa_nlu_response
