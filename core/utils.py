from __future__ import annotations

import json
import uuid
import unicodedata
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from .extractor_ai import DocumentFields, document_fields_to_public_dict


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
DOCUMENTS_DB_PATH = DATA_DIR / "documentos.json"


def _ensure_data_dir_exists() -> None:
    """
    Garante que a pasta data/ existe.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_documents_db() -> List[Dict[str, Any]]:
    """
    Carrega o "banco" de documentos (lista de registros) a partir de data/documentos.json.

    Se o arquivo não existir ou estiver vazio/corrompido, retorna uma lista vazia.
    """
    _ensure_data_dir_exists()

    if not DOCUMENTS_DB_PATH.exists():
        return []
    
    try:
        raw = DOCUMENTS_DB_PATH.read_text(encoding="utf-8")
        if not raw.strip():
            return []
        
        data = json.loads(raw)
        if isinstance(data, list):
            return data
        
        return []
    except Exception:
        return []
    

def save_documents_db(records: List[Dict[str, Any]]) -> None:
    """
    Salva a lista completa de registros em data/documentos.json.

    Sobreescreve o conteudo anterior.
    """
    _ensure_data_dir_exists()

    DOCUMENTS_DB_PATH.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def reset_documents_db() -> None:
    """
    Reseta o 'banco' de documentos, sobrescrevendo data/documentos.json com uma lista vazia.

    Util para garantir que cada sessão de uso do app comece com uma base limpa.
    """
    _ensure_data_dir_exists()
    DOCUMENTS_DB_PATH.write_text("[]", encoding="utf-8")


def add_document_records(new_records: List[Dict[str, any]]) -> None:
    """
    Adiciona novos registros ao "banco" e salva de volta no arquivo JSON.
    """
    if not new_records:
        return
    
    existing = load_documents_db()
    existing.extend(new_records)
    save_documents_db(existing)


def build_document_records(
    people: List[DocumentFields],
    *,
    source_file_name: str,
    source_pdf_is_scanned: bool,
) -> List[Dict[str, Any]]:
    """
    Constroi uma lista de registros prontos para serem persistidos
    em data/documentos.json, a partir da lista de DocumentFields.

    Cada registro representa uma "pessoa" extraida do PDF.
    """
    records: List[Dict[str, Any]] = []
    now_iso = datetime.now(timezone.utc).isoformat()

    for idx, person in enumerate(people, start=1):
        public_fields = document_fields_to_public_dict(person)

        record: Dict[str, Any] = {
            "id": str(uuid.uuid4()),
            "file_name": source_file_name,
            "person_index": idx,
            "is_probably_scanned": source_pdf_is_scanned,
            "created_at": now_iso,
            "fields": public_fields,
        }
        records.append(record)

    return records


def sanitize_text_for_ai(text: str) -> str:
    """
    Limpa o texto antes de enviar para a IA, removendo caracteres que podem causar
    problemas de encoding (acentos estranhos, símbolos 'quebrados', etc).

    Estratégia:
    - Normaliza Unicode (NFKD).
    - Converte para ASCII ignorando caracteres que não podem ser representados.
      (Isso remove acentos, aspas curvas e símbolos bizarros.)
    """
    if not text:
        return text

    # Normaliza acentos e caracteres compostos
    normalized = unicodedata.normalize("NFKD", text)

    # Remove tudo que não cabe em ASCII (acentos, símbolos estranhos, etc.)
    ascii_bytes = normalized.encode("ascii", errors="ignore")
    safe_text = ascii_bytes.decode("ascii")

    return safe_text