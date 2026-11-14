# Leitor de Contratos: "o que eu tô assinando?"

Aplicação de terminal em Python que lê um contrato e aponta, em português simples, as cláusulas que podem trazer custo, obrigação ou risco para quem vai assinar, usando o Claude (Anthropic) por meio da API.

> Projeto P0 (Primeiro fluxo com LLM). Status atual: **nível Básico**.

## O problema

**Em uma frase:** pessoas assinam contratos de aluguel, academia, telefonia, internet e cursos sem entender cláusulas como multa rescisória, fidelidade, renovação automática e reajuste, e só descobrem o problema quando já estão presas a elas.

- **Quem tem essa necessidade:** qualquer pessoa sem formação jurídica que precise assinar um contrato de consumo ou de locação. Eu mesmo, e pessoas próximas, já passamos por isso (por exemplo, com academia e plano de internet).
- **Entrada:** o texto do contrato (arquivo `.txt` ou texto colado no terminal).
- **Saída:** um relatório com resumo, pontos de atenção classificados por risco (alto, médio e baixo), cada um com o trecho do contrato e uma explicação simples, e perguntas para fazer antes de assinar.
- **Por que um LLM:** contratos usam linguagem jurídica, têm estrutura variável e escondem riscos no meio do texto. Regras fixas (palavras-chave, regex) não conseguem interpretar o sentido de uma cláusula nem explicá-la em linguagem simples. Um modelo de linguagem consegue.

## LLM utilizado

| Item | Escolha |
|---|---|
| Provedor | Anthropic (Claude), via API oficial |
| Modelo padrão | `claude-opus-5-5` (configurável pela variável `ANTHROPIC_MODEL`) |
| Biblioteca | SDK oficial `anthropic` para Python, que faz as chamadas HTTPS à API REST `POST /v1/messages` |
| Custo | Por conta do estudante. Uma análise de contrato típica custa poucos centavos de dólar |

**Por que não o LLM institucional:** o LLM institucional (Ollama com Qwen) só é acessível de dentro dos containers da plataforma Devel, o que obriga a gerar e enviar uma imagem Docker a cada teste. Analisar contratos longos exige boa precisão para citar trechos literais, e preferi um modelo maior que pode ser executado localmente por qualquer pessoa com uma chave de API. A instituição não presta suporte a este provedor.

## Como executar

### Pré-requisitos

- Python 3.10 ou superior
- Uma chave de API da Anthropic ([console.anthropic.com](https://console.anthropic.com/settings/keys))

### Instalação

```bash
git clone https://github.com/aaglis/p0-fluxo-llm.git
cd p0-fluxo-llm
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Configuração da chave

```bash
cp .env.example .env
```

Abra o `.env` e substitua `coloque-sua-chave-aqui` pela sua chave. O arquivo `.env` está no `.gitignore` e nunca deve ser enviado ao repositório. A chave não aparece em nenhum lugar do código.

### Uso

```bash
# Analisar um arquivo
python main.py exemplos/contrato_academia.txt

# Colar o texto no terminal (finalize com Ctrl+D; no Windows, Ctrl+Z e Enter)
python main.py

# Receber pela entrada padrão
cat meu_contrato.txt | python main.py
```

## Estrutura

```
.
├── main.py              # interface de terminal: lê a entrada e mostra o relatório
├── analisador.py        # prompt, chamada ao Claude e processamento da resposta
├── exemplos/            # contratos fictícios para teste
├── requirements.txt     # dependências com versões fixadas
└── .env.example         # modelo de configuração (sem segredos)
```

## Privacidade

O texto do contrato é enviado à API da Anthropic. Os exemplos do repositório são **fictícios**. Se for analisar um contrato real, remova antes dados pessoais como nome, CPF, endereço e dados bancários.

## Aviso

Esta ferramenta ajuda a ler contratos, mas **não substitui a orientação de um advogado**.

## Uso de IA no desenvolvimento

Utilizei o Claude Code (assistente de programação da Anthropic) para discutir ideias de projeto, estruturar o código inicial e redigir esta documentação. Todo o código foi revisado e testado por mim.
