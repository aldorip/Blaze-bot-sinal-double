<h1 align="center">🤖 Bot de Sinais Automatizado para Blaze - Double</h1>
<p align="center"><strong>Identifique padrões, envie sinais, aplique Martingale e receba estatísticas em tempo real via Telegram.</strong></p>

---

## 🧠 Sobre o Projeto

Este é um bot inteligente desenvolvido em Python que se conecta à API da Blaze para coletar dados em tempo real do jogo **Double**.  
Ele analisa sequências com base em padrões salvos, envia **sinais automatizados** para um grupo do **Telegram**, acompanha os resultados e aplica **Martingale** até um limite de tentativas.

> ⚠️ **Aviso Importante**  
> Este projeto é de caráter **educacional** e **analítico**, não representando incentivo à prática de jogos de azar. Use com responsabilidade.

---

## ⚙️ Funcionalidades

✅ Monitoramento em tempo real do jogo Double  
✅ Verificação de padrões configuráveis via JSON  
✅ Envio de sinais com link de aposta e sticker de marca  
✅ Sistema de Martingale com contagem de tentativas (Gales)  
✅ Estatísticas detalhadas: win, loss, win com gale e vitórias seguidas  
✅ Feedback visual via stickers (WIN/LOSS)  
✅ Totalmente assíncrono com `aiohttp` e `asyncio`

---

## 🛠️ Tecnologias Utilizadas

| Biblioteca     | Descrição                                |
|----------------|--------------------------------------------|
| `telebot`      | Envia mensagens e stickers para o Telegram |
| `aiohttp`      | Requisições HTTP assíncronas               |
| `asyncio`      | Loop de eventos e tarefas assíncronas      |
| `datetime`     | Manipulação de datas e formatação          |
| `configparser` | Gerencia arquivos de configuração `.ini`   |

---

## 🗂️ Estrutura esperada

```
📁 seu_repositorio/
│
├── config.ini                # Configurações de tokens, URLs e stickers
├── sequencias.json          # Lista de padrões e previsões (Ex: [["V,P,B","P"]])
├── bot.py                   # Código principal do bot
├── pix_qrcode.png           # Imagem opcional do QR code para apoio
└── README.md                # Este arquivo de documentação
```

### Exemplo de `config.ini`

```ini
[url_cassino]
url = https://api.blaze.bet

[bot_config]
api_key = SEU_TOKEN_DO_BOT
chat_id = SEU_CHAT_ID
sticker_win = CAACAgEAAxkBA...
sticker_loss = CAACAgEAAxkBB...
sticker_pybots = CAACAgEAAxkBC...
```

---

## ▶️ Como Usar

1. Clone o repositório:
```bash
git clone https://github.com/SEU_USUARIO/nome-do-repositorio.git
cd nome-do-repositorio
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Edite o arquivo `config.ini` com seus dados da Blaze e Telegram.

4. Adicione seus padrões no arquivo `sequencias.json`:
```json
[
  [["V", "P", "B"], "P"],
  [["B", "V", "B"], "V"]
]
```

5. Execute o bot:
```bash
python bot.py
```

---

## 💡 Exemplo de Funcionamento

- O bot verifica os últimos giros.
- Identifica se algum padrão salvo ocorreu.
- Se identificar, envia mensagem para o grupo com:
  - Cor da entrada (🔴 ou ⚫️)
  - Sticker temático
  - Link de aposta
  - Informações de Gale (até quantas tentativas)
- Após o resultado, envia sticker WIN ou LOSS e estatísticas atualizadas.

---

## 💸 Apoie este Projeto

Se este projeto te ajudou ou você curtiu a ideia, considere apoiar com uma doação via PIX:

<p align="lefth">
  <img src="https://raw.githubusercontent.com/aldorip/api_resultados_blaze/refs/heads/main/pix_qrcode.png" alt="QR Code PIX" width="220"/>
</p>

📌 Chave PIX (aleatória):  
`f2f781b0-a4af-43f2-a2b3-f2c5d3a2e9bc`

---

## 📬 Contato

[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=flat&logo=telegram&logoColor=white)](https://t.me/aldorip)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/in/aldo-ribeiro-7b61a646)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/aldorip)

---

> 💡 *"Bots inteligentes não apenas automatizam. Eles tomam decisões baseadas em dados."*  
> — Aldo Ribeiro
