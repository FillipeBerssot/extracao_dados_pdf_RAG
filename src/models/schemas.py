# src/models/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional

class DadosDocumento(BaseModel):
    nome_completo: str = Field(description="O nome completo da pessoa portadora do documento.")
    data_nascimento: str = Field(description="Data de nascimento no formato DD/MM/AAAA.")
    numero_rg: Optional[str] = Field(description="Número do RG (Registro Geral) sem pontos ou traços, se houver.")
    numero_cpf: Optional[str] = Field(description="Número do CPF (Cadastro de Pessoas Físicas) sem pontos ou traços, se houver.")
    filiacao: List[str] = Field(description="Lista com os nomes dos pais (filiação).")
    genero: Optional[str] = Field(description="Gênero ou sexo listado no documento (Masculino, Feminino, Outro), se disponível.")
    orgao_emissor: Optional[str] = Field(description="Órgão emissor do documento (ex: SSP/SP, DETRAN), se disponível.")