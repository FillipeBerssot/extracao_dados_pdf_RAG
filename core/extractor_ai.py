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
    Constroi o prompt para extracao de DADOS DE UMA OU MAIS PESSOAS.

    Importante: usamos apenas caracteres ASCII para evitar problemas
    de encoding em alguns ambientes.
    """
    return f"""
    You are an assistant specialized in extracting structured data from Brazilian identity documents
    (RG, CPF, CNH, etc.).

    The text below may contain data from ONE or MORE different people.

    Your task:

    1. Identify each distinct person mentioned in the text.
    2. For each person, extract ONLY the fields below.

    Return the answer STRICTLY as valid JSON, with the format:

    {{
    "pessoas": [
        {{
        "nome": string or null,
        "cpf": string or null,
        "rg": string or null,
        "data_nascimento": string or null,
        "genero": string or null,
        "orgao_emissor": string or null,
        "tipo_documento": string or null,
        "numero_documento": string or null
        }},
        ...
    ]
    }}

    Rules:
    - Do NOT invent information.
    - If a field is not clearly present for a person, use null.
    - The same person must not appear twice.
    - Use the date format exactly as it appears in the document (for example: "01/01/1990").
    - For CPF/RG, keep dots and dashes if they appear in the document.
    - For "genero", use the exact text that appears (for example: "MASCULINO", "FEMININO").
    - If you cannot find any person, return "pessoas": [].

    Document text:

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
                        "You are an assistant for structured data extraction, "
                        "specialized in Brazilian identity documents (RG, CPF, CNH, etc.). "
                        "Always respond with valid JSON only."
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
