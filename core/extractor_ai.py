from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from openai import OpenAI



class ExtractionAIError(Exception):
    """Erro genérico para problemas na extração via IA."""
    pass


@dataclass
class DocumentFields:
    """
    Representa os campos extraídos de um documento de identificação.

    Todos os campos são opcionais por que podem não aparecer no documento.
    """
    nome: Optional[str] = None
    cpf: Optional[str] = None
    rg: Optional[str] = None
    data_nascimento: Optional[str] = None
    genero: Optional[str] = None
    orgao_emissor: Optional[str] = None
    tipo_documento: Optional[str] = None
    numero_documento: Optional[str] = None

    raw_model_output: Optional[Dict[str, Any]] = None


def _build_client(api_key: str) -> OpenAI:
    """
    Cria o cliente da OpenAI com a API Key informada.

    Args:
        api_key (str): A chave da API da OpenAI.

    Returns:
        Instância de OpenAI.
    """
    if not api_key:
        raise ExtractionAIError("API Key da OpenAI não foi informada.")
    return OpenAI(api_key=api_key)


def _build_prompt(document_text: str) -> str:
    """
    Constrói o prompt para extração de DADOS DE UMA OU MAIS PESSOAS.
    """
    return f"""
    Você é um assistente especializado em extrair dados estruturados de documentos
    de identificação brasileiros (RG, CPF, CNH, etc.).

    O texto a seguir pode conter dados de UMA ou MAIS pessoas diferentes.

    Sua tarefa é:
    1. Identificar cada pessoa distinta presente no texto.
    2. Para cada pessoa, extrair APENAS os campos abaixo.

    Retorne a resposta EXCLUSIVAMENTE em JSON válido, no formato:

    {{
        "pessoas": [
            {{
            "nome": string | null,
            "cpf": string | null,
            "rg": string | null,
            "data_nascimento": string | null,
            "genero": string | null,
            "orgao_emissor": string | null,
            "tipo_documento": string | null,
            "numero_documento": string | null
            }},
            ...
        ]
    }}

    Regras importantes:
    - Não invente informações.
    - Se um campo não estiver claro ou não existir para uma pessoa, use null.
    - Uma mesma pessoa não deve aparecer duplicada.
    - Use o formato de data exatamente como aparece no documento (ex: "01/01/1990").
    - Para CPF/RG, mantenha pontos e traços se estiverem no documento.
    - Para "genero", use o texto exato que aparecer (ex: "MASCULINO", "FEMININO").
    - Se não encontrar nenhuma pessoa, retorne "pessoas": [].

    Texto do documento:

    \"\"\"{document_text}\"\"\"
    """.strip()


def extract_people_from_text(
    document_text: str,
    api_key: str,
    model: str = "gpt-4o-mini",
) -> List[DocumentFields]:
    """
    Usa a API da OpenAI para extrair dados de UMA OU MAIS pessoas
    a partir do texto do documento.

    Retorna uma lista de DocumentFields (uma entrada por pessoa).
    """
    if not document_text or not document_text.strip():
        raise ExtractionAIError("Texto do documento está vazio; nada para extrair.")
    
    client = _build_client(api_key)
    prompt = _build_prompt(document_text)

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um assistente de extração de dados estruturados, "
                        "especializado em documentos de identificação brasileiros."
                    ),                
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

    except Exception as exc:
        raise ExtractionAIError(f"Erro ao chamar a API da OpenAI: {exc}") from exc
    
    try:
        content = response.choices[0].message.content
        data = json.loads(content)
    except Exception as exc:
        raise ExtractionAIError(f"Não foi possível interpretar a resposta da IA como JSON: {exc}") from exc
    
    if isinstance(data, list):
        data = {"pessoas": data}

    raw_people = data.get("pessoas", [])
    if not isinstance(raw_people, list):
        raise ExtractionAIError(
            "Resposta da IA não contém o campo 'pessoas' como uma lista."
        )

    people: List[DocumentFields] = []

    for person in raw_people:
        if not isinstance(person, dict):
            continue

        fields = DocumentFields(
            nome=person.get("nome"),
            cpf=person.get("cpf"),
            rg=person.get("rg"),
            data_nascimento=person.get("data_nascimento"),
            genero=person.get("genero"),
            orgao_emissor=person.get("orgao_emissor"),
            tipo_documento=person.get("tipo_documento"),
            numero_documento=person.get("numero_documento"),
            raw_model_output=person,
        )
        people.append(fields)

    return people


def extract_fields_from_text(
    document_text: str,
    api_key: str,
    model: str = "gpt-4o-mini",
) -> DocumentFields:
    """
    Retorna apenas a primeira pessoa encontrada.

    Útil se quiser manter o comportamento de "um documento = uma pessoa".
    """
    people = extract_people_from_text(document_text=document_text, api_key=api_key, model=model)
    if not people:
        raise ExtractionAIError(
            "Nenhuma pessoa foi identificada no texto do documento."
        )
    return people[0]


def document_fields_to_public_dict(fields: DocumentFields) -> Dict[str, Any]:
    """
    Converte o dataclass para um dicionario "limpo" para exibição,
    removendo campos internos como `raw_model_output`.

    Args:
        fields (DocumentFields): A instância a ser convertida.

    Returns:
        Dicionário apenas com os campos de interesse para o usuário.
    """
    base = asdict(fields)
    base.pop("raw_model_output", None)
    return base


def people_to_public_dict_list(people: List[DocumentFields]) -> List[Dict[str, Any]]:
    """
    Converte uma lista de DocumentFields em uma lista de dicionários
    prontos para exibição (um dicionário por pessoa).
    """
    return [document_fields_to_public_dict(p) for p in people]
