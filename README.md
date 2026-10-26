# 🔎 Twitter Checker

Bot de Discord que analisa de quais clientes (Web, iPhone, Android, TweetDeck, apps de terceiros…) foram publicados os últimos tweets de uma conta do X/Twitter e aponta origens incomuns que **podem** indicar que a conta foi comprometida.

```
/check usuario:wallstengine
```

O bot responde com um embed contendo:

- **Sources** — quantos tweets vieram de cada cliente (✅ comum / ⚠️ incomum)
- **Suspicious** — os tweets de origem incomum, com link
- **Verdict** — `NORMAL`, `SUSPEITO` ou `ALTO RISCO`

## Como funciona

O X removeu o rótulo de origem da interface, mas o campo `source` ainda vem nas respostas da API GraphQL interna usada pelo site. O bot usa o [twscrape](https://github.com/vladkens/twscrape) para buscar os tweets com uma conta logada (via cookies) e lê o campo `sourceLabel` de cada um.

> ⚠️ O veredito é uma **heurística**, não uma prova. Muitas contas legítimas (notícias, empresas, criadores) usam TweetDeck/X Pro ou ferramentas de agendamento. Use o resultado como um sinal para investigar, nunca como acusação.

## Requisitos

- Python 3.10+
- Um bot do Discord ([Developer Portal](https://discord.com/developers/applications))
- Uma conta **secundária** do X (pode ser suspensa — não use sua conta principal)

## Instalação

```bash
git clone https://github.com/SEU_USUARIO/twitter-checker.git
cd twitter-checker
python -m pip install -r requirements.txt
```

### 1. Token do Discord

Copie o arquivo de exemplo e cole o token do bot (Developer Portal → sua aplicação → **Bot** → **Reset Token**):

```bash
cp .env.example .env        # Linux/Mac
copy .env.example .env      # Windows
```

```
DISCORD_TOKEN=seu_token_aqui
```

Convide o bot para o servidor em **OAuth2 → URL Generator** com os escopos `bot` e `applications.commands` e as permissões *Send Messages* e *Embed Links*.

### 2. Conta do X

Logado no x.com com a conta secundária, abra o DevTools (F12) → **Application** → **Cookies** → `https://x.com` e copie os valores de `auth_token` e `ct0`. Depois:

```bash
python add_account.py NOME_DA_CONTA "auth_token=VALOR; ct0=VALOR"
```

Deve aparecer `active: True`. Não clique em "Sair" nessa conta no navegador, ou os cookies param de funcionar. Para mais estabilidade, adicione 2–3 contas: o twscrape alterna entre elas.

### 3. Rodar

```bash
python bot.py
```

No Windows, você pode usar o `iniciar.bat`, que reinicia o bot automaticamente se ele cair.

## Personalização

No topo do `bot.py`:

| Variável | O que faz |
|---|---|
| `FONTES_NORMAIS` | Clientes considerados comuns (✅). Qualquer outro é marcado com ⚠️ |
| `LIMITE_TWEETS` | Quantos tweets analisar (padrão: 20) |
| `MAX_SUSPEITOS_EXIBIDOS` | Quantos tweets suspeitos listar no embed |
| `TIMEOUT_BUSCA` | Tempo máximo de espera por consulta, em segundos |

## Limitações

- **IP e localização não estão disponíveis.** O X não expõe esses dados para terceiros.
- **Pode quebrar sem aviso.** O X pode mudar a API interna ou remover o campo `source` a qualquer momento. Nesse caso, atualize o twscrape (`pip install -U twscrape`).
- **Limites de uso.** Cada `/check` faz algumas requisições, e o X limita requisições e leitura de posts por conta. Uso intenso pode bloquear temporariamente a conta.

## Aviso legal

Este projeto acessa a API interna do X por meio de scraping, o que viola os [Termos de Serviço do X](https://x.com/tos). Ele é disponibilizado para fins educacionais e de pesquisa. Quem o utiliza assume total responsabilidade pelo uso, incluindo a possível suspensão das contas envolvidas. Os autores não têm afiliação com o X Corp.

**Nunca commite o `.env` ou o `accounts.db`** — eles contêm o token do bot e os cookies da conta do X. O `.gitignore` incluído já os exclui.

## Licença

[MIT](LICENSE)
