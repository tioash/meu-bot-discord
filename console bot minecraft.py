import discord
from discord.ext import commands
from discord import Embed
from discord.ui import Button, View
from mcstatus import MinecraftServer
from mcrcon import MCRcon  # Usando a biblioteca mcrcon

# Substitua pelo token do seu bot do Discord
TOKEN = ''  # Coloque seu token aqui

# Substitua pelo endereço do seu servidor Minecraft e as credenciais do RCON
MINECRAFT_SERVER = ''  # Ex: 'play.exemplo.com'
MINECRAFT_PORT = 25555 # A porta do Minecraft pode ser personalizada
RCON_PORT = 25575  # A porta padrão do RCON geralmente é 25575 (se estiver ativada sem senha)

# Criação do client do bot Discord com comandos de barra
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Função para verificar o status do servidor Minecraft
def get_minecraft_status():
    try:
        print("Tentando conectar ao servidor Minecraft...")
        # Conecta ao servidor Minecraft
        server = MinecraftServer.lookup(f'{MINECRAFT_SERVER}:{MINECRAFT_PORT}')
        status = server.status()  # Obtém o status do servidor
        players_online = status.players.online
        version = status.version.name

        # Corrigido para acessar o nome do jogador corretamente
        player_names = ', '.join(player.name for player in status.players.sample) if status.players.sample else "Nenhum jogador online"
        print(f"Conexão bem-sucedida ao servidor. Status: {players_online} jogadores online")
        return version, players_online, player_names
    except Exception as e:
        print(f"Erro ao conectar ao servidor Minecraft: {str(e)}")
        return None, None, f"Erro ao conectar ao servidor Minecraft: {str(e)}"

# Função para criar o Embed com tradução
def create_embed(language="pt"):
    print(f"Criando embed no idioma: {language}")
    version, players_online, player_names = get_minecraft_status()

    title = "🟩 Status do Servidor Minecraft 🟩" if language == "pt" else "🟩 Minecraft Server Status 🟩"
    description = f"**Servidor:** {MINECRAFT_SERVER}\n**Porta:** {MINECRAFT_PORT}"

    embed = Embed(title=title, description=description, color=discord.Color.green())

    if version and players_online is not None:
        embed.add_field(name="🔹 **Versão do Servidor**" if language == "pt" else "🔹 **Server Version**", value=f"**{version}**", inline=False)
        embed.add_field(name="🕹️ **Jogadores Online**" if language == "pt" else "🕹️ **Players Online**", value=f"**{players_online}**", inline=False)
        embed.add_field(name="👾 **Jogadores no Servidor**" if language == "pt" else "👾 **Players on Server**", value=player_names, inline=False)
    else:
        embed.add_field(name="❌ **Erro**" if language == "pt" else "❌ **Error**", value=player_names, inline=False)

    embed.set_thumbnail(url="https://cdn1.site-media.eu/images/0/13394007/download.png")
    embed.set_footer(text="BOT  | Desenvolvido por [Tioash]" if language == "pt" else "BOT  | Developed by [Tioash]")

    print("Embed criado com sucesso!")
    return embed

# Função para o botão "Bom Dia"
class GoodMorningView(View):
    def __init__(self, embed_pt, embed_en):
        super().__init__()
        self.embed_pt = embed_pt
        self.embed_en = embed_en

    @discord.ui.button(label="🌞 Bom Dia!", style=discord.ButtonStyle.success)
    async def good_morning_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        print("Botão 'Bom Dia' clicado!")

        # Enviar "Bom Dia" no chat do servidor Minecraft usando RCON
        try:
            with MCRcon(MINECRAFT_SERVER, password="SuaSenhaRCON", port=RCON_PORT) as mcr:
                mcr.command("say Bom dia, jogadores! ☀️")  # Envia uma mensagem no chat do Minecraft
            await interaction.response.send_message("Mensagem de 'Bom Dia' enviada para o servidor Minecraft!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Erro ao enviar 'Bom Dia' para o servidor: {str(e)}", ephemeral=True)

    @discord.ui.button(label="PT", style=discord.ButtonStyle.primary)
    async def pt_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        print("Botão PT clicado!")
        await interaction.response.edit_message(embed=self.embed_pt, view=self)

    @discord.ui.button(label="EN", style=discord.ButtonStyle.primary)
    async def en_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        print("Botão EN clicado!")
        await interaction.response.edit_message(embed=self.embed_en, view=self)

# Comando de barra para o status do servidor
@bot.tree.command(name="status", description="Verifique o status do servidor Minecraft")
async def status(interaction: discord.Interaction):
    print("Comando /status acionado.")  # Log: Comando acionado
    await interaction.response.defer()  # Defere a interação para evitar expiração rápida

    embed_pt = create_embed(language="pt")  # Criação do Embed em português
    embed_en = create_embed(language="en")  # Criação do Embed em inglês

    view = GoodMorningView(embed_pt=embed_pt, embed_en=embed_en)  # Adicionando o botão "Bom Dia" e botões de idioma

    try:
        # Enviar a mensagem com embed e botões para o canal
        print("Enviando mensagem com embed e botões...")
        await interaction.followup.send(embed=embed_pt, view=view)  # Usando followup.send() para evitar erro
        print("Mensagem enviada com sucesso!")  # Log: Mensagem enviada
    except Exception as e:
        print(f"Erro ao enviar a mensagem: {str(e)}")

# Evento quando o bot está pronto
@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')  # Log: Bot está online
    try:
        await bot.tree.sync()  # Sincroniza os comandos de barra quando o bot estiver pronto
        print("Comandos de barra registrados!")  # Log: Comandos sincronizados
    except Exception as e:
        print(f"Erro ao registrar os comandos de barra: {str(e)}")

# Inicia o bot do Discord
async def run_bot():
    print("Iniciando o bot...")
    await bot.start(TOKEN)

# Chama o bot de maneira assíncrona
import asyncio
asyncio.run(run_bot())
