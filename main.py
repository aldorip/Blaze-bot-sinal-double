import json
import telebot
import aiohttp
import asyncio
import configparser
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

class BlazeBot:
    def __init__(self, config_file='config.ini'): 
        # Ativa ou desativa depuração do código
        self.depuracao = True
        
        # Lê as configurações
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.url = self.config.get("url_cassino", "url")
        self.token = self.config.get("bot_config", "api_key")
        self.chat_id = int(self.config.get("bot_config", "chat_id"))
        self.sticker_win = self.config.get("bot_config", "sticker_win")
        self.sticker_loss = self.config.get("bot_config", "sticker_loss")
        self.sticker_pybots = self.config.get("bot_config", "sticker_pybots")
        
        # Variáveis de controle para martingales e análise
        self.sinal_entrada = None
        self.padrao = None
        self.martingale = 0
        self.entrada_atual = 0
        self.color_entrada = None
        self.analise_open = False
        self.last_status = None
        
        # Variáveis de estatísticas
        self.total_signals = 0
        self.win_count = 0
        self.loss_count = 0
        self.win_gale_count = 0
        self.win_normal_count = 0   # Novo contador para vitórias sem gale
        self.consecutive_win_count = 0
        self.max_consecutive_win_count = 0

        # Inicializa a sessão de API e o bot do Telegram
        self.api_session = None
        self.bot = telebot.TeleBot(self.token)

    # Métodos de conexão
    async def start_session(self):
        if self.api_session is None or self.api_session.closed:
            connector = aiohttp.TCPConnector(ssl=False)
            self.api_session = aiohttp.ClientSession(connector=connector)

    async def fetch(self, endpoint):
        await self.start_session()
        url = f"{self.url}/{endpoint}"
        async with self.api_session.get(url) as response:
            if response.status == 200:
                return await response.json()
            return None

    async def close(self):
        if self.api_session:
            await self.api_session.close()

    # Métodos de manipulação de dados via endpoints
    async def get_current(self):
        endpoint = "api/singleplayer-originals/originals/roulette_games/current/1"
        await self.start_session()
        async with self.api_session.get(f"{self.url}/{endpoint}") as response:
            if response.status == 200:
                return await response.json()
            return None

    async def get_last_doubles(self):
        endpoint = "api/singleplayer-originals/originals/roulette_games/recent/1"
        data = await self.fetch(endpoint)
        if data:
            result = {
                "items": [
                    {
                        "color": "B" if i["color"] == 0 else "V" if i["color"] == 1 else "P",
                        "value": i["roll"],
                        "created_date": datetime.strptime(i["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M:%S")
                    }
                    for i in data
                ]
            }
            return result
        return False

    async def result_recent(self):
        current = await self.get_current()
        status = current.get("status")
        recent_roll = current.get('roll')
        recent_color = current.get('color')
        # Mapeia para as iniciais: B, V, P
        color_map = {0: "B", 2: "P", 1: "V"}
        color_recente = color_map.get(recent_color, 'desconhecido')
        return status, recent_roll, color_recente

    async def historico_view(self, results):
        def map_color(number):
            if number == 0:
                return '⚪️'
            elif 1 <= number <= 7:
                return '🔴'
            elif 8 <= number <= 14:
                return '⚫️'
            else:
                return '?'
        numeros_ = results[0:10][::-1]
        emoji_colors = [map_color(num) for num in numeros_]
        numeros = [str(num).rjust(2) for num in numeros_]
        return f"Giro completo...\n{' '.join(numeros)}\n{''.join(emoji_colors)}"

    async def get_recentes(self):
        recentes = await self.get_last_doubles()
        numbers = [item["value"] for item in recentes["items"]]
        colors = [item["color"] for item in recentes["items"]]
        return numbers, colors

    # Métodos de verificação e correção de sinal
    async def martingales(self):
        if self.entrada_atual < self.martingale:
            self.entrada_atual += 1
            return "GALE"
        else:
            self.entrada_atual = 0
            return "LOSS"

    async def win_loss(self, resultado):
        if self.depuracao:
            print(f"Depuração: win_loss: |{resultado}| x |{self.color_entrada}|")
        # Armazena quantas tentativas de gale ocorreram antes do resultado final
        gale_attempts = self.entrada_atual
        if resultado == self.color_entrada:
            self.entrada_atual = 0
            return "WIN", gale_attempts
        else:
            res = await self.martingales()
            return res, gale_attempts

    async def verificar_padrao(self, sequenciaPadrao, previsaoPadrao):
        """
        Verifica se o padrão (sequenciaPadrao) está presente nos últimos resultados.
        Regras de comparação:
          - Se o elemento do padrão for numérico, compara com o campo "value".
          - Se for uma letra:
              * "X": coringa (ignora a comparação)
              * "N": deve corresponder somente a "V" ou "P"
              * Caso contrário, compara diretamente com o campo "color".
        Retorna um dicionário com o padrão e a previsão se houver match, ou False.
        """
        result = await self.get_last_doubles()
        
        if not result or "items" not in result:
            if self.depuracao:
                print("Depuração: Erro: Não foi possível obter os últimos resultados.")
            return False

        lastDoubles = result["items"]
        last_results = lastDoubles[::-1]
        
        if len(sequenciaPadrao) > len(last_results):
            if self.depuracao:
                print("Depuração: Dados insuficientes para comparação.")
            return False

        last_segment = last_results[-len(sequenciaPadrao):]
        match = True
        for i, pat in enumerate(sequenciaPadrao):
            if str(pat).isdigit():
                if str(last_segment[i]["value"]) != str(pat):
                    match = False
                    break
            else:
                pattern_letter = str(pat).upper()
                outcome_color = str(last_segment[i]["color"]).upper()
                if pattern_letter == "X":
                    continue
                elif pattern_letter == "N":
                    if outcome_color not in ["V", "P"]:
                        match = False
                        break
                else:
                    if outcome_color != pattern_letter:
                        match = False
                        break
        if match:
            return {"padrao": sequenciaPadrao, "previsao": previsaoPadrao}
        else:
            return False

    async def verificar_padroes_salvos(self, caminho_json):
        with open(caminho_json, 'r', encoding='utf-8') as file:
            padroes_salvos = json.load(file)
        if not isinstance(padroes_salvos, list):
            if self.depuracao:
                print("Depuração: Erro: O arquivo JSON deve conter uma lista de padrões.")
            return None

        for item in padroes_salvos:
            if not isinstance(item, list) or len(item) != 2:
                if self.depuracao:
                    print(f"Depuração: Erro: Formato inválido encontrado: {item}")
                continue

            padrao, previsao = item  
            resultado = await self.verificar_padrao(padrao, previsao)
            if resultado:
                # Retorna uma tupla contendo o padrão identificado e a previsão
                return resultado["padrao"], resultado["previsao"]
        return None
    
    # Métodos para interagir com o Telegram
    def send_message(self, text, reply_markup=None, parse_mode="HTML"):
        try:
            message = self.bot.send_message(
                self.chat_id, text, reply_markup=reply_markup, parse_mode=parse_mode
            )
            return message.message_id
        except Exception as e:
            if self.depuracao:
                print("Depuração: Erro ao enviar mensagem:", e)
            return None

    def send_sticker(self, sticker_file_id):
        try:
            message = self.bot.send_sticker(self.chat_id, sticker_file_id)
            return message.message_id
        except Exception as e:
            if self.depuracao:
                print("Depuração: Erro ao enviar sticker:", e)
            return None

    def delete_message(self, message_id):
        try:
            self.bot.delete_message(self.chat_id, message_id)
        except Exception as e:
            if self.depuracao:
                print("Depuração: Erro ao apagar mensagem:", e)

    # Função que retorna uma mensagem formatada com as estatísticas
    def get_statistics_message(self):
        if self.total_signals > 0:
            accuracy = self.win_count / self.total_signals * 100
        else:
            accuracy = 0.0
        message = (
            f"<b> Placar: ✅ {self.win_count} X {self.loss_count} ❌\n\n"
            f"  - 🥇 Sem Gale: {self.win_normal_count}\n"
            f"  - 🐔 Com Gale: {self.win_gale_count}\n\n"
            f"✅ Wins sequidos: {self.consecutive_win_count}\n"
            f"🎯 Assertividade: {accuracy:.2f}% </b>"
        )
        return message

    # Função para enviar as estatísticas via Telegram
    def enviar_estatisticas(self):
        stats_message = self.get_statistics_message()
        self.send_message(stats_message)

    # Função de análise e identificação de oportunidades de sinal
    async def run(self):
        self.send_sticker(self.sticker_pybots)
        if self.depuracao:
            print("Depuração: BOT ONLINE!")
        msg_id = None

        while True:
            status, recent_roll, color_recente = await self.result_recent()
            if status != self.last_status:
                self.last_status = status

                if status == "waiting":
                    if msg_id is not None:
                        await asyncio.sleep(13)
                        self.delete_message(msg_id)

                    
                elif status == "rolling" and self.analise_open:
                    # Captura quantas tentativas de gale ocorreram antes do resultado final
                    resultado_aposta, gale_attempts = await self.win_loss(color_recente)
                    
                    if resultado_aposta == "WIN":
                        self.win_count += 1
                        if gale_attempts > 0:
                            self.win_gale_count += 1
                        else:
                            self.win_normal_count += 1  # Conta vitórias sem gale
                        self.consecutive_win_count += 1
                        if self.consecutive_win_count > self.max_consecutive_win_count:
                            self.max_consecutive_win_count = self.consecutive_win_count
                        self.analise_open = False
                        self.send_sticker(self.sticker_win)
                        self.enviar_estatisticas()
                    
                    elif resultado_aposta == "LOSS":
                        self.loss_count += 1
                        self.consecutive_win_count = 0
                        self.analise_open = False
                        self.send_sticker(self.sticker_loss)
                        self.enviar_estatisticas()
                    
                    elif resultado_aposta == "GALE":
                        color_map = {"B": "⚪️", "P": "⚫️", "V": "🔴"}
                        cor_saiu = color_map.get(color_recente, 'desconhecido')
                        mensagem_gale = (
                            "🎲 <b>Blaze Girou...</b>\n\n"
                            f"⏱️ Saiu >> <b>| {recent_roll} | : {cor_saiu} |</b>\n\n"
                            f"➡️ <b>Vamos para Gale {self.entrada_atual}</b>"
                        )
                        msg_id_gale = self.send_message(mensagem_gale)
                        await asyncio.sleep(7)
                        self.delete_message(msg_id_gale)

                elif status == "complete":
                    numbers, _ = await self.get_recentes()
                    recentes = await self.historico_view(numbers)
                    mensage_giro = f"<b>{recentes}</b>"
                    msg_id = self.send_message(mensage_giro)
                    
                    if not self.analise_open:
                        resultado = await self.verificar_padroes_salvos('sequencias.json')
                        if resultado is not None:
                            self.padrao, self.sinal_entrada = resultado
                            if self.depuracao:
                                print(f"Depuração: Padrão identificado: {self.padrao} {self.sinal_entrada}")
                            self.total_signals += 1  # Incrementa total de sinais
                            
                            if self.sinal_entrada == "P":
                                self.martingale = 2  # Atualiza antes de montar a mensagem
                                self.color_entrada = self.sinal_entrada
                                mensagem_sinal = (
                                    "🚧 <b>SINAL ENCONTRADO</b> 🚧\n\n"
                                    "<b>ENTRAR NA COR</b> ⚫️\n"
                                    f"♻️ <b>Até Gale {self.martingale}</b>"
                                )
                                markup = InlineKeyboardMarkup()
                                botao = InlineKeyboardButton("🎰 Aposte Aqui", url="https://blaze.bet.br/pt/games/double")
                                markup.add(botao)
                                self.send_message(mensagem_sinal, reply_markup=markup)
                                self.analise_open = True

                            elif self.sinal_entrada == "V":
                                self.martingale = 2  # Atualiza antes de montar a mensagem
                                self.color_entrada = self.sinal_entrada
                                mensagem_sinal = (
                                    "🚧 <b>SINAL ENCONTRADO</b> 🚧\n\n"
                                    "<b>ENTRAR NA COR</b> 🔴\n"
                                    f"♻️ <b>Até Gale {self.martingale}</b>"
                                )
                                markup = InlineKeyboardMarkup()
                                botao = InlineKeyboardButton("🎰 Aposte Aqui", url="https://blaze.bet.br/pt/games/double")
                                markup.add(botao)
                                self.send_message(mensagem_sinal, reply_markup=markup)
                                self.analise_open = True


            await asyncio.sleep(1)
# Função principal para executar o bot
async def main():
    bot = BlazeBot()
    try:
        await bot.run()
    except Exception as e:
        if bot.depuracao:
            print("Depuração: Erro:", e)
    finally:
        await bot.close()

asyncio.run(main())
