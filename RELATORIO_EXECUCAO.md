# Relatório de execução — P0

Projeto: **Leitor de Contratos: "o que eu tô assinando?"**, uma aplicação de terminal que lê um contrato e aponta, em português simples, as cláusulas que trazem custo, obrigação ou risco para quem vai assinar, usando o Claude por meio da API.

Repositório: https://github.com/aaglis/p0-fluxo-llm · Vídeo: ver o [README](README.md#vídeo-de-demonstração)

## Evolução por nível

| Nível | Tag | O que foi feito |
|---|---|---|
| Básico | [`p0-basico`](https://github.com/aaglis/p0-fluxo-llm/releases/tag/p0-basico) | Primeiro fluxo funcional em dois arquivos (`main.py` e `analisador.py`): lê o contrato de um arquivo ou do terminal, carrega a chave do `.env`, faz uma chamada ao Claude e imprime o relatório. Bloqueio de entrada vazia e de credencial ausente, `.env.example`, `.gitignore`, contrato fictício de exemplo e README inicial. |
| Intermediário | [`p0-intermediario`](https://github.com/aaglis/p0-fluxo-llm/releases/tag/p0-intermediario) | Código reorganizado em um pacote com um módulo por responsabilidade (entrada, configuração, solicitação, chamada, resposta, apresentação, erros). Resposta em JSON com esquema validado pelo Pydantic e conferência de cada trecho citado. Tradução de todos os erros da API em mensagens compreensíveis. Defesas contra prompt injection e texto escondido. Testes com cliente simulado. Desenvolvido na branch `feat/intermediario` e integrado pelo [PR #1](https://github.com/aaglis/p0-fluxo-llm/pull/1). |
| Avançado | [`p0-avancado`](https://github.com/aaglis/p0-fluxo-llm/releases/tag/p0-avancado) | Parâmetros configuráveis pelo `.env` (modelo, tokens, timeout, esforço, tentativas, registros), registros de execução apenas com metadados, `--verbose` e `--help`, versões documentadas, testes automáticos no GitHub Actions em Python 3.10 a 3.14 e validação em ambiente limpo. Integrado pelo [PR #2](https://github.com/aaglis/p0-fluxo-llm/pull/2). |

## Decisões principais

| Decisão tomada | Alternativa considerada | Justificativa |
|---|---|---|
| Usar a API do Claude com chave própria | LLM institucional (Ollama com Qwen) | O LLM institucional só responde de dentro dos containers da plataforma Devel, o que obrigaria a gerar uma imagem Docker a cada teste. Com a API, qualquer pessoa reproduz o projeto localmente com uma chave. Cheguei a tentar baixar o Qwen para rodar localmente, mas desisti: o download era grande e o resultado não seria o mesmo modelo da plataforma. |
| Modelo `claude-haiku-5-5` | `claude-opus-5-5`, mais capaz | A tarefa é ler um texto curto e explicar cláusulas. Nos testes, o Haiku encontrou as cláusulas esperadas e citou trechos literais, com custo e tempo menores. O modelo pode ser trocado pelo `.env`. |
| Resposta em JSON com esquema, validada com Pydantic | Pedir texto livre e imprimir direto | Com campos estruturados, o código consegue conferir se cada trecho citado existe no contrato, ordenar por risco e detectar respostas fora do formato. Texto livre não permite nenhuma dessas verificações. |
| Uma única chamada, sem tools, agentes ou banco vetorial | Agente com ferramentas ou RAG | O contrato cabe inteiro no prompt e a tarefa tem um só passo. Sem ferramentas, um texto malicioso no contrato não consegue disparar nenhuma ação: no pior caso, altera o relatório, e isso é sinalizado. |
| Testes com um cliente simulado no lugar do Claude | Testar apenas com chamadas reais | Os testes simulados rodam sem chave, sem internet e sem custo, inclusive no GitHub Actions, e reproduzem erros difíceis de provocar de verdade (429, 529). Os cenários reais foram executados à parte e documentados. |

## Testes e resultados

Testes reais, executados com chamadas ao Claude ou com a aplicação real:

| Teste | Entrada ou situação | Resultado esperado | Resultado obtido |
|---|---|---|---|
| Entrada válida | `exemplos/contrato_academia.txt` | Relatório com resumo, pontos por risco, trechos e perguntas | 14 pontos de atenção, todos os trechos conferidos no contrato |
| Prompt injection | `exemplos/contrato_com_injecao.txt`, com instrução escondida para a IA e caracteres invisíveis | Instrução ignorada e reportada; usuário avisado sobre os caracteres | Alerta de manipulação exibido, ponto de risco alto registrado, 3 caracteres ocultos removidos |
| Entrada vazia | Arquivo vazio ou Ctrl+D sem texto | Envio bloqueado com orientação | "Nenhum texto foi recebido", sem chamada à API |
| Arquivo inexistente | `python main.py nao_existe.txt` | Mensagem indicando o arquivo | Mensagem com o caminho informado |
| Credencial ausente | `ANTHROPIC_API_KEY=` vazio | Aviso sem dados sensíveis | "A chave de acesso ao Claude não foi configurada" e como configurar |
| Credencial inválida | `ANTHROPIC_API_KEY=sk-ant-chave-falsa` | Encerramento controlado, sem expor a chave | A API devolveu 401; "A chave de acesso foi recusada pelo Claude", código de saída 1 |
| Modelo inexistente | `ANTHROPIC_MODEL=claude-nao-existe` | Mensagem sobre o modelo | "O modelo 'claude-nao-existe' não foi encontrado" |
| Tempo esgotado | `TIMEOUT_SEGUNDOS=0.01` | Mensagem compreensível | "O Claude não respondeu em 0.01 segundos" |
| Falha de comunicação | `ANTHROPIC_BASE_URL=http://127.0.0.1:9` | Mensagem compreensível | "Não foi possível conectar ao Claude" |
| Resposta cortada | `MAX_TOKENS=50` | Aviso de resposta incompleta | Mensagem de resposta cortada, sugerindo aumentar `MAX_TOKENS` |
| Ambiente limpo | Clone novo seguindo só o README (macOS com Python 3.12, Docker Alpine) | Instalação e execução sem ajuda | Funcionou nos dois; falhou com o Python 3.9 do macOS (ver abaixo) |

Testes sem chamada real: 53 testes no `pytest`, com o cliente simulado, executados a cada push no GitHub Actions (Python 3.10 a 3.14). Cobrem cada etapa separadamente (entrada, configuração, solicitação, tradução de cada erro da API, interpretação da resposta, verificação de trechos, apresentação) e o fluxo completo do `main.py`. Também verificam que a chave e o texto do contrato nunca aparecem nos registros nem nas mensagens de erro.

## Falhas e limitações

**1. Registro vazando no terminal (corrigida).**
- *O que aconteceu:* sem a chave configurada, aparecia a linha `Execução encerrada com erro: CredencialAusente` antes da mensagem de erro, mesmo sem `--verbose`.
- *Como foi identificado:* na validação em ambiente limpo. Nos testes isso não aparecia, porque o pytest captura os registros.
- *Como foi tratado:* o erro acontecia antes de os registros serem configurados, e o Python usava o manipulador padrão, que imprime no terminal. O pacote passou a registrar um `NullHandler`, e foi criado um teste que executa o programa em um subprocesso, como o usuário faria. Esse teste falha sem a correção.

**2. Python antigo do macOS (contornada na documentação).**
- *O que aconteceu:* com o `python3` que vem no macOS (3.9.6), o `pip install` falhou com `No matching distribution found for anthropic==2.8.0`.
- *Como foi identificado:* na validação em ambiente limpo.
- *Como foi tratado:* as bibliotecas exigem Python 3.10 ou superior, e a mensagem do `pip` não diz isso. O README passou a pedir a conferência com `python3 --version` e explica o erro em "Problemas comuns".

**3. Pontos fora de ordem (corrigida).**
- *O que aconteceu:* em um teste real, o ponto sobre a tentativa de manipulação apareceu depois de pontos de risco baixo, apesar de o prompt pedir ordenação por risco.
- *Como foi tratado:* o código passou a ordenar os pontos por risco antes de imprimir, sem depender do modelo.

**4. Omissões do modelo (permanece).**
- *O que é:* a verificação de trechos detecta citações inventadas, mas não detecta uma cláusula de risco que o modelo deixou de mencionar.
- *Por que permanece:* conferir omissões exigiria uma segunda análise independente ou uma lista fixa de cláusulas, o que foge do escopo do P0. Por isso o relatório sempre termina avisando que não substitui um advogado.

**5. Resultados variam (permanece).** Duas execuções com o mesmo contrato podem trazer quantidades diferentes de pontos e redações diferentes. O `claude-haiku-5-5` não aceita ajustar `temperature`, então não é possível fixar a variação. O formato da saída e a conferência dos trechos são sempre os mesmos.

## Uso de IA no desenvolvimento

| Ferramenta | Tarefa delegada | Resultado aproveitado | Correções ou alterações | Verificação |
|---|---|---|---|---|
| Claude Code | Discutir ideias de projeto a partir do enunciado | A ideia do leitor de contratos, entre as opções sugeridas | Rejeitei a primeira sugestão (um classificador simples) e pedi algo de maior impacto | Conferi a ideia contra os critérios do enunciado (problema real, uso de LLM justificado) |
| Claude Code | Investigar o acesso ao LLM institucional | Diagnóstico de que o Ollama só é acessível dentro da plataforma Devel | Interrompi o download local do modelo e decidi usar minha chave da API do Claude | Teste de acesso à URL institucional fora da plataforma |
| Claude Code | Escrever o código de cada etapa e reorganizá-lo em módulos | Estrutura do pacote, chamada à API, tradução de erros, verificação de trechos | Troquei o modelo padrão de Opus para Haiku; pedi a remoção de comentários desnecessários; exigi o reforço contra prompt injection | Execuções reais com contratos de exemplo e com cenários de erro |
| Claude Code | Escrever os testes simulados | 53 testes com cliente simulado | Acrescentados os testes de segredos nos registros e o teste em subprocesso depois da falha encontrada | `pytest` local e no GitHub Actions |
| Claude Code | Redigir o README e este relatório | Estrutura e redação | Revisei o conteúdo e conferi os comandos e resultados | Instalação em ambiente limpo seguindo apenas o README |

Também pedi que a IA não aparecesse como coautora dos commits, e o histórico foi reescrito para refletir isso antes da primeira release.

## Reflexão final

- **Principal aprendizado:** a resposta de um LLM precisa ser tratada como dado não confiável, assim como a entrada. Pedir saída estruturada e conferi-la no código (validar o JSON, procurar cada trecho citado no contrato, ordenar por risco) é o que transforma uma resposta plausível em uma resposta verificável.
- **Competência mais desenvolvida:** testar e tratar falhas. Simular a API permitiu cobrir erros que seriam difíceis de reproduzir de verdade, e a validação em ambiente limpo mostrou problemas que os testes automáticos não pegavam.
- **O que ainda precisa ser aprimorado:** avaliar a qualidade da análise de forma sistemática. Hoje sei que os trechos citados existem, mas não meço quantas cláusulas importantes o modelo deixa de apontar. Um próximo passo seria montar um conjunto de contratos com as cláusulas de risco já marcadas e comparar com o que o modelo encontra.
