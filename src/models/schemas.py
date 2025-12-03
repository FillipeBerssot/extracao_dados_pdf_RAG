import re

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional



class DadosDocumento(BaseModel):
    tipo_documento: str = Field(description="O tipo do documento (RG, CNH, etc).")
    nome_completo: str = Field(description="Nome completo exatamente como consta no documento.")
    data_nascimento: Optional[str] = Field(description="Data de nascimento (ex: 10/05/1990).")
    
    numero_rg: Optional[str] = Field(description="Número do RG incluindo pontos e traços.")
    numero_cpf: Optional[str] = Field(description="Número do CPF incluindo pontos e traços.")
    
    filiacao: List[str] = Field(description="Lista com os nomes dos pais.")
    genero: Optional[str] = Field(description="Gênero/Sexo.")
    orgao_emissor: Optional[str] = Field(description="Órgão emissor.")

    @field_validator('numero_cpf')
    @classmethod
    def validar_cpf(cls, v):
        if not v:
            return None
        
        limpo = re.sub(r'[^0-9]', '', v)
        
        if len(limpo) != 11:
            return f"{v} (ALERTA: Formato Inválido - {len(limpo)} dígitos)"
        
        return v

    @field_validator('data_nascimento')
    @classmethod
    def validar_data(cls, v):
        if not v:
            return None

        if not re.match(r'\d{2}/\d{2}/\d{4}', v):
            return f"{v} (ALERTA: Formato de data suspeito)"
        return v

class AnaliseDocumentos(BaseModel):
    pessoas_identificadas: List[DadosDocumento] = Field(description="Lista de documentos identificados.")