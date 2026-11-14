# Leitor de Contratos: "o que eu tô assinando?"

[![Testes](https://github.com/aaglis/p0-fluxo-llm/actions/workflows/testes.yml/badge.svg)](https://github.com/aaglis/p0-fluxo-llm/actions/workflows/testes.yml)

Aplicação de terminal em Python que lê um contrato e aponta, em português simples, as cláusulas que podem trazer custo, obrigação ou risco para quem vai assinar, usando o Claude (Anthropic) por meio da API.

> Projeto P0 (Primeiro fluxo com LLM). Status atual: **nível Avançado**.

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

- Python 3.10 ou superior. Confira com `python3 --version`.
- Uma chave de API da Anthropic ([console.anthropic.com](https://console.anthropic.com/settings/keys))

| Componente | Versão |
|---|---|
| Python | 3.10 a 3.15 (testes automáticos de 3.10 a 3.14; desenvolvido em 3.15) |
| `anthropic` | 2.8.0 (SDK oficial da API do Claude) |
| `pydantic` | 2.14.3 (validação da resposta em JSON) |
| `python-dotenv` | 1.2.4 (leitura do `.env`) |
| `pytest` | 9.2.0 (testes, apenas desenvolvimento) |

As versões estão fixadas em [`requirements.txt`](requirements.txt) e [`requirements-dev.txt`](requirements-dev.txt).

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
| `ESFORCO` | não | `medium` | Profundidade do raciocínio do modelo: `low`, `medium`, `high`, `xhigh` ou `max` |
| `MAX_TENTATIVAS` | não | `2` | Novas tentativas automáticas em falhas temporárias (429, 5xx, rede) |
| `LOG_NIVEL` | não | `INFO` | Nível dos registros: `DEBUG`, `INFO`, `WARNING` ou `ERROR` |
| `LOG_ARQUIVO` | não | `logs/leitor_contratos.log` | Arquivo de registros; vazio desativa o arquivo |

Todos os parâmetros são lidos em [`config.py`](leitor_contratos/config.py) e validados antes de qualquer chamada. Para alterá-los, basta editar o `.env`, sem mexer no código.

**Sobre `temperature` e `top_p`:** no `claude-haiku-5-5`, a API recusa valores diferentes do padrão para esses parâmetros. Por isso os parâmetros de geração configuráveis são `MAX_TOKENS` e `ESFORCO`, que a API aceita neste modelo.

### Uso

```bash
# Analisar um arquivo
python main.py exemplos/contrato_academia.txt

# Colar o texto no terminal (finalize com Ctrl+D; no Windows, Ctrl+Z e Enter)
python main.py

# Receber pela entrada padrão
cat meu_contrato.txt | python main.py

# Mostrar os registros da execução no terminal
python main.py --verbose exemplos/contrato_academia.txt

# Ajuda
python main.py --help
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

Os registros ficam em [`registro.py`](leitor_contratos/registro.py). O [`main.py`](main.py) apenas encadeia essas etapas. Não há ferramentas (tools), agentes nem banco vetorial: é uma única chamada ao modelo por análise.

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

## Registros de execução

Cada execução grava em `logs/leitor_contratos.log` (pasta ignorada pelo Git). Com `--verbose`, os registros também aparecem no terminal.

```
INFO leitor_contratos.entrada: Entrada preparada: 1164 caracteres, 3 caracteres ocultos removidos
INFO leitor_contratos.cliente_llm: Enviando solicitação: modelo=claude-haiku-5-5 max_tokens=16000 esforco=medium timeout=120s tentativas=2
INFO leitor_contratos.cliente_llm: Resposta recebida em 9.8s: stop_reason=end_turn tokens_entrada=2194 tokens_saida=1986 request_id=req_011Ch3H8JNuWBx2duxNheL5j
INFO leitor_contratos.resposta: Análise verificada: eh_contrato=True pontos=4 trechos_nao_encontrados=0 manipulacoes=1
```

**É registrado:** tamanho da entrada, parâmetros usados, tempo de resposta, tokens consumidos, `request_id` da API (útil para suporte), contagens da análise e o tipo de erro, quando houver.

**Nunca é registrado:** a chave de API, o texto do contrato, o relatório ou trechos citados. Há testes que verificam isso. Apenas o logger da aplicação grava no arquivo; os registros internos do SDK e da biblioteca HTTP não são gravados.

## Testes

### Testes simulados (sem chamar a API)

```bash
pip install -r requirements-dev.txt
pytest
```

Os 52 testes em [`tests/`](tests) usam um cliente simulado no lugar do Claude. Não precisam de chave nem de internet e não geram custo. Eles cobrem a validação da entrada, a configuração, a montagem da solicitação, a tradução de cada erro da API (401, 403, 404, 429, 500, 529, timeout e falha de conexão), respostas inválidas, a verificação de trechos, a limpeza da saída o fluxo completo do `main.py`, incluindo credencial ausente e credencial inválida sem expor a chave, e a ausência de segredos e conteúdo nos registros.

O [GitHub Actions](.github/workflows/testes.yml) executa esses testes a cada push, em Python 3.10, 3.11, 3.12, 3.13 e 3.14.

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

## Decisões

| Decisão | Escolha | Motivo |
|---|---|---|
| Problema | Cláusulas de risco em contratos | Necessidade real, explicável em uma frase, com saída verificável |
| Provedor | Claude (API da Anthropic) | Executável localmente por qualquer pessoa com chave; o LLM institucional só funciona dentro da plataforma Devel |
| Modelo | `claude-haiku-5-5` | O mais leve e barato da linha; nos testes, encontrou as cláusulas esperadas e citou trechos literais |
| Formato da resposta | JSON com esquema, validado com Pydantic | Permite conferir cada trecho e formatar o relatório no código |
| Tools, agentes, RAG | Não utilizados | O contrato cabe inteiro no prompt e a tarefa é de um passo; sem tools, um ataque não consegue disparar ações |
| Interface | Terminal | Suficiente para o escopo do P0 |
| Erros tratados | Entrada, configuração, credencial, disponibilidade, rede, timeout e formato da resposta | Situações previstas no enunciado, cada uma com mensagem própria |
| Testes | Cliente simulado no pytest + cenários reais documentados | Testes repetíveis, sem custo, mais a evidência do funcionamento real |

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
│   ├── registro.py          # configuração dos registros de execução
│   ├── modelos.py           # esquema da resposta (Pydantic)
│   └── erros.py             # erros da aplicação
├── tests/                   # testes simulados (pytest)
├── .github/workflows/       # testes automáticos no GitHub Actions
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
