# 🕵️ Extrator de Dados Inteligente (IDP) + Chat RAG

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?style=for-the-badge&logo=openai&logoColor=white)
![Status](https://img.shields.io/badge/Status-Projeto_de_Estudo-success?style=for-the-badge)

<details>
  <summary><strong>📸 Clique aqui para ver as Screenshots do Projeto</strong></summary>
  <br>
  <div align="center">
    <img src="CAMINHO_DA_FOTO_1.png" alt="Tela Inicial" width="700">
    <br><br>
    <img src="CAMINHO_DA_FOTO_2.png" alt="Resultado da Extração" width="700">
  </div>
</details>

## Link para utilizar no Streamlit

👉  https://extracao-dados-rag.streamlit.app/

## 📖 Sobre o Projeto

Este é um projeto de **Intelligent Document Processing (IDP)** desenvolvido como estudo de caso em Engenharia de IA.

O sistema recebe documentos digitalizados (PDFs de RG, CNH, Certidões), utiliza **Modelos de Visão Multimodal (GPT-4o)** para extrair dados com precisão humana e oferece uma interface de **RAG (Retrieval-Augmented Generation)** para que o usuário possa "conversar" com os documentos extraídos.

O diferencial deste projeto é a arquitetura robusta que valida os dados matematicamente (CPF, Datas) e separa automaticamente múltiplos documentos contidos em um único arquivo PDF.

---

## 📚 Aprendizados do Projeto de Estudo
Este projeto abordou conceitos fundamentais de Engenharia de IA Moderna:

Prompt Engineering: Como instruir a IA a agir como uma "Máquina de OCR literal".

Context Injection: Como injetar dados JSON no contexto do chat para criar um RAG eficiente.

Handling Multimodal Inputs: Manipulação de texto e imagem simultaneamente.

Stateless Web Apps: Gerenciamento de sessão em aplicações Streamlit.

---

## 🛠️ Arquitetura e Tecnologias

O projeto foi construído utilizando uma arquitetura modular moderna. Abaixo, detalho as ferramentas escolhidas e o "porquê" de cada uma:

| Tecnologia | Função no Projeto | Por que foi escolhida? |
| :--- | :--- | :--- |
| **OpenAI GPT-4o** | Cérebro / OCR Semântico | Diferente de OCRs tradicionais (Tesseract), o GPT-4o "entende" o layout visual e o contexto, corrigindo falhas de leitura em documentos amassados ou complexos. |
| **Streamlit** | Frontend / Interface | Permite criar aplicações de dados interativas rapidamente usando apenas Python, com gerenciamento eficiente de memória de sessão. |
| **Pydantic** | Modelagem de Dados | Garante que a IA devolva um JSON estrito e estruturado. Usado também para criar **Data Guardrails** (validadores que alertam se um CPF é inválido). |
| **pdf2image** | Conversão de Arquivos | Modelos de visão (Vision LLMs) trabalham melhor com imagens (JPG/PNG) do que com PDFs puros. Esta lib faz a conversão em alta resolução (300 DPI). |
| **Pillow (PIL)** | Pré-processamento | Usada para aplicar filtros de contraste, nitidez e escala de cinza nas imagens antes de enviá-las à IA, aumentando a assertividade. |

---

## 🚀 Funcionalidades Principais

* **📥 Leitura Multi-Tenant:** Identifica se o PDF contém documentos de uma ou mais pessoas e separa os dados automaticamente em abas diferentes.
* **👁️ Visão Computacional Avançada:** Pré-processamento de imagem automático para melhorar documentos escuros ou com baixa legibilidade.
* **🛡️ Validação de Dados (Guardrails):** O sistema alerta visualmente se formatos críticos (como CPF e Datas) estiverem inconsistentes.
* **💬 Chat Inteligente (RAG):** Interface de chat contextual que permite perguntas complexas (ex: *"Qual a data de expedição do documento mais antigo?"*).
* **🔒 Privacidade e Segurança:** Arquitetura *stateless*. Os dados residem apenas na memória RAM da sessão e são destruídos assim que a página é recarregada.

---

## 📂 Estrutura do Código

O projeto segue padrões de Engenharia de Software, evitando scripts únicos ("código espaguete") para facilitar a manutenção.

```text
/EXTRACAO_DADOS_PDF_RAG
├── main.py                # O Maestro: Gerencia a Interface e o fluxo de dados
├── requirements.txt       # Bibliotecas Python necessárias
├── packages.txt           # Dependências de sistema (Linux/Debian) para Deploy
├── src/
|    ├── models/
|    │   └── schemas.py     # Definição dos campos (JSON) e regras de validação
|    ├── services/
|    │   ├── ai_service.py  # Comunicação com a OpenAI e lógica do Chat RAG
|    │   └── image_utils.py # Pipeline de tratamento de imagem (DPI, Contraste)
|    └── ui/
|        └── interface.py   # Componentes visuais (Barra lateral, Chat)
├─ README.md
└─ .env                        # (opcional) OpenAI API Key
```

---

## 💻 Como Rodar no Seu Computador (Localhost)

Siga estes passos para executar o projeto na sua máquina (Windows/WSL, Linux ou Mac).

### 1. Pré-requisitos
Certifique-se de ter instalado:

* **Python 3.9+**
* **Poppler** (Ferramenta de sistema essencial para manipular PDFs).

**Instalando o Poppler:**
* **Windows (via WSL/Ubuntu):** `sudo apt-get install poppler-utils`
* **Linux (Debian/Ubuntu):** `sudo apt-get install poppler-utils`
* **MacOS:** `brew install poppler`

### 2. Instalação

Clone o repositório e entre na pasta:

```bash
git clone [https://github.com/FillipeBerssot/extracao_dados_pdf_RAG.git](https://github.com/FillipeBerssot/extracao_dados_pdf_RAG)
cd extrator-documentos
Crie e ative um ambiente virtual (Recomendado):

# Linux/Mac/WSL
python3 -m venv venv
source venv/bin/activate

# Windows (Powershell)
python -m venv venv
.\venv\Scripts\activate
Instale as dependências:

pip install -r requirements.txt
3. Execução
Rode o comando do Streamlit:

streamlit run main.py
O navegador abrirá automaticamente em: http://localhost:8501
```

---

## 🎮 Guia de Uso

API Key: Ao abrir o sistema, insira sua chave da OpenAI na barra lateral esquerda.

Upload: Arraste seu PDF para a área indicada.

Processamento: Clique em "🔍 Extrair Dados". O sistema irá:

Converter o PDF em imagens de alta resolução.

Melhorar o contraste e nitidez.

Enviar para o GPT-4o extrair os dados.

Resultados: Visualize os dados estruturados nas abas laterais.

Interação: Use o chat abaixo para tirar dúvidas sobre o documento processado.

---

## ⚠️ Notas de Estudo

Custos: O projeto utiliza a API paga da OpenAI (gpt-4o). O custo médio é de ~$0.005 USD por documento processado.

Limitações: A qualidade da extração depende da qualidade da imagem original, embora o pré-processamento ajude significativamente.

Desenvolvido como projeto de estudo em IA Generativa Aplicada.

---