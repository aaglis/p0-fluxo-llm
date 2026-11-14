# Leitor de Contratos: "o que eu tô assinando?"

Aplicação de terminal em Python que lê um contrato e aponta, em português simples, as cláusulas que podem trazer custo, obrigação ou risco para quem vai assinar, usando o Claude (Anthropic) por meio da API.

> Projeto P0 (Primeiro fluxo com LLM). Status atual: **nível Intermediário**.

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
| Modelo padrão | `claude-haiku-5-5` (configurável pela variável `ANTHROPIC_MODEL`) |
| Biblioteca | SDK oficial `anthropic` para Python, que faz as chamadas HTTPS à API REST `POST /v1/messages` |
| Custo | Por conta do estudante. Uma análise de contrato típica custa poucos centavos de dólar |

**Por que não o LLM institucional:** o LLM institucional (Ollama com Qwen) só é acessível de dentro dos containers da plataforma Devel, o que obriga a gerar e enviar uma imagem Docker a cada teste. Preferi um serviço que qualquer pessoa consegue usar localmente com uma chave de API, o que facilita o desenvolvimento e a reprodução por terceiros. A instituição não presta suporte a este provedor.

## Como executar

### Pré-requisitos

- Python 3.10 ou superior (desenvolvido e testado com Python 3.15)
- Uma chave de API da Anthropic ([console.anthropic.com](https://console.anthropic.com/settings/keys))

### Instalação

```bash
git clone https://github.com/aaglis/p0-fluxo-llm.git
cd p0-fluxo-llm
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Para rodar os testes, instale também as dependências de desenvolvimento: `pip install -r requirements-dev.txt`.

### Configuração

```bash
cp .env.example .env
```

Abra o `.env` e substitua `coloque-sua-chave-aqui` pela sua chave. O `.env` está no `.gitignore` e não deve ser enviado ao repositório. A chave não aparece no código, nos relatórios nem nas mensagens de erro.

| Variável | Obrigatória | Padrão | Função |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | sim | | Chave de acesso à API da Anthropic |
| `ANTHROPIC_MODEL` | não | `claude-haiku-5-5` | Modelo usado na análise |
| `MAX_TOKENS` | não | `16000` | Limite de tamanho da resposta |
| `TIMEOUT_SEGUNDOS` | não | `120` | Tempo máximo de espera por resposta |
| `MAX_CARACTERES` | não | `100000` | Tamanho máximo do contrato aceito |

### Uso

```bash
# Analisar um arquivo
python main.py exemplos/contrato_academia.txt

# Colar o texto no terminal (finalize com Ctrl+D; no Windows, Ctrl+Z e Enter)
python main.py

# Receber pela entrada padrão
cat meu_contrato.txt | python main.py
```

## Exemplo de entrada e saída

Entrada: [`exemplos/contrato_academia.txt`](exemplos/contrato_academia.txt), um contrato fictício de academia.

```
$ python main.py exemplos/contrato_academia.txt
Analisando o contrato, aguarde...

RESUMO
Contrato de prestação de serviços de musculação e aulas coletivas entre a Academia Corpo
em Movimento Ltda. (contratada) e a pessoa física matriculada (contratante), com vigência
de 12 meses e renovação automática.

PONTOS DE ATENÇÃO (14)

[ALTO] Multa de 50% das mensalidades restantes
    Trecho: "Em caso de cancelamento antes do término da vigência, será cobrada multa
    rescisória equivalente a 50% (cinquenta por cento) do valor das mensalidades restantes
    até o fim do contrato."
    O que significa: Exemplo: se você sair no 4º mês de um plano de R$ 119,90, com 8
    mensalidades restantes, a multa seria de cerca de R$ 479,60 (50% de 8 x R$ 119,90),
    além de pagar o mês em curso.
...

PERGUNTE ANTES DE ASSINAR
  1. Como posso cancelar por escrito ou à distância, e não só presencialmente na recepção?
...

Todos os trechos citados foram conferidos no texto do contrato.
Este relatório não substitui a orientação de um advogado.
```

As respostas do modelo variam a cada execução; o formato é sempre o mesmo.

## Como funciona

1. **Entrada** ([`entrada.py`](leitor_contratos/entrada.py)): lê o arquivo ou o texto colado, remove caracteres invisíveis, bloqueia texto vazio e acima do limite.
2. **Configuração** ([`config.py`](leitor_contratos/config.py)): lê e valida as variáveis do `.env`.
3. **Solicitação** ([`prompt.py`](leitor_contratos/prompt.py)): monta o prompt, delimita o contrato entre `<contrato>` e `</contrato>` e pede a resposta em JSON seguindo um esquema.
4. **Chamada** ([`cliente_llm.py`](leitor_contratos/cliente_llm.py)): envia ao Claude e traduz os erros da API em mensagens compreensíveis.
5. **Resposta** ([`resposta.py`](leitor_contratos/resposta.py)): valida o JSON com Pydantic e confere se cada trecho citado existe literalmente no contrato.
6. **Apresentação** ([`apresentacao.py`](leitor_contratos/apresentacao.py)): monta o relatório e remove caracteres de controle antes de imprimir.

O [`main.py`](main.py) apenas encadeia essas etapas. Não há ferramentas (tools), agentes nem banco vetorial: é uma única chamada ao modelo por análise.

## Tratamento de erros

| Situação | Mensagem exibida |
|---|---|
| Entrada vazia | Nenhum texto foi recebido |
| Arquivo inexistente, pasta ou arquivo não UTF-8 | Indica o problema com o arquivo |
| Texto acima de `MAX_CARACTERES` | Informa o tamanho e o limite |
| Configuração inválida (`MAX_TOKENS=abc`, timeout negativo) | Indica a variável e o valor incorreto |
| Credencial ausente | A chave de acesso ao Claude não foi configurada |
| Credencial inválida (401) ou sem permissão (403) | A chave de acesso foi recusada pelo Claude |
| Modelo inexistente (404) | O modelo não foi encontrado |
| Limite de requisições (429), indisponibilidade ou sobrecarga (5xx, 529) | O serviço está indisponível; tente novamente |
| Timeout | O Claude não respondeu no tempo configurado |
| Falha de comunicação | Não foi possível conectar ao Claude |
| Resposta vazia, fora do formato, cortada ou recusada | Explica o que houve e sugere o que fazer |

Todas as mensagens vão para a saída de erro, com código de saída 1, sem traceback.

## Testes

### Testes simulados (sem chamar a API)

```bash
pip install -r requirements-dev.txt
pytest
```

Os 43 testes em [`tests/`](tests) usam um cliente simulado no lugar do Claude. Não precisam de chave nem de internet e não geram custo. Eles cobrem a validação da entrada, a configuração, a montagem da solicitação, a tradução de cada erro da API (401, 403, 404, 429, 500, 529, timeout e falha de conexão), respostas inválidas, a verificação de trechos, a limpeza da saída e o fluxo completo do `main.py`, incluindo credencial ausente e credencial inválida sem expor a chave.

### Testes reais (com a API)

Executados manualmente, com chamadas reais ao Claude:

| Cenário | Comando | Resultado |
|---|---|---|
| Análise de contrato | `python main.py exemplos/contrato_academia.txt` | Relatório com 14 pontos, todos os trechos conferidos |
| Prompt injection | `python main.py exemplos/contrato_com_injecao.txt` | Instrução escondida detectada e reportada como alerta |
| Credencial ausente | `ANTHROPIC_API_KEY= python main.py exemplos/contrato_academia.txt` | Mensagem de chave não configurada |
| Credencial inválida | `ANTHROPIC_API_KEY=sk-ant-chave-falsa python main.py exemplos/contrato_academia.txt` | A API devolveu 401; mensagem de chave recusada |
| Modelo inexistente | `ANTHROPIC_MODEL=claude-nao-existe python main.py ...` | Mensagem de modelo não encontrado |
| Timeout | `TIMEOUT_SEGUNDOS=0.01 python main.py ...` | Mensagem de tempo esgotado |
| Falha de comunicação | `ANTHROPIC_BASE_URL=http://127.0.0.1:9 python main.py ...` | Mensagem de falha de conexão |
| Resposta cortada | `MAX_TOKENS=50 python main.py ...` | Mensagem de resposta cortada |

## Segurança

O texto do contrato é escrito pela outra parte, que tem interesse em que riscos passem despercebidos. Por isso ele é tratado como conteúdo não confiável:

- **Prompt injection:** o contrato vai delimitado por tags, e o prompt instrui o modelo a tratá-lo como dado e a reportar qualquer texto dirigido a sistemas de IA. Tags `<contrato>` dentro do próprio texto são neutralizadas para que o documento não "feche" o delimitador. O exemplo [`contrato_com_injecao.txt`](exemplos/contrato_com_injecao.txt) demonstra a detecção.
- **Texto escondido:** caracteres invisíveis (largura zero, controle de direção) são removidos e o usuário é avisado.
- **Citações conferidas:** cada trecho citado é procurado no contrato. Os que não forem encontrados são marcados. Limitação: essa verificação detecta citações inventadas, mas não detecta cláusulas que o modelo deixou de mencionar.
- **Saída do terminal:** caracteres de controle e sequências de escape são removidos antes de imprimir.
- **Sem ferramentas:** o modelo não executa ações; no pior caso, um ataque altera apenas o texto do relatório.
- **Segredos:** a chave fica no `.env`, fora do repositório, e não aparece em mensagens de erro (há teste para isso).

## Estrutura

```
.
├── main.py                  # orquestra as etapas
├── leitor_contratos/
│   ├── entrada.py           # captura e validação da entrada
│   ├── config.py            # carregamento da configuração
│   ├── prompt.py            # preparação da solicitação
│   ├── cliente_llm.py       # chamada ao modelo e tradução de erros
│   ├── resposta.py          # validação da resposta e verificação de trechos
│   ├── apresentacao.py      # formatação do relatório
│   ├── modelos.py           # esquema da resposta (Pydantic)
│   └── erros.py             # erros da aplicação
├── tests/                   # testes simulados (pytest)
├── exemplos/                # contratos fictícios
├── requirements.txt
├── requirements-dev.txt
└── .env.example
```

## Privacidade

O texto do contrato é enviado à API da Anthropic. Os exemplos do repositório são **fictícios**. Se for analisar um contrato real, remova antes dados pessoais como nome, CPF, endereço e dados bancários.

## Aviso

Esta ferramenta ajuda a ler contratos, mas **não substitui a orientação de um advogado**.

## Uso de IA no desenvolvimento

Utilizei o Claude Code (assistente de programação da Anthropic) para discutir ideias de projeto, analisar os requisitos, estruturar o código, escrever testes e redigir esta documentação. As decisões de escopo, provedor e modelo foram minhas, e todo o código foi revisado e testado por mim.
