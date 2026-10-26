import os
import asyncio
from collections import Counter

import discord
from discord import app_commands
from dotenv import load_dotenv
from twscrape import API, gather

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

LIMITE_TWEETS = 20
TIMEOUT_BUSCA = 60  # segundos
MAX_SUSPEITOS_EXIBIDOS = 5

# Clientes oficiais considerados "normais". Qualquer outro é marcado com ⚠️.
FONTES_NORMAIS = {
    "Twitter Web App",
    "Twitter for iPhone",
    "Twitter for Android",
    "Twitter for iPad",
    "Twitter for Mac",
}

api = API("accounts.db")


class CheckerBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        print(f"Bot online as {self.user}")


bot = CheckerBot()


def fonte(tweet) -> str:
    return tweet.sourceLabel or "Unknown"


def resumo(texto: str, tamanho: int = 60) -> str:
    texto = " ".join(texto.split())  # remove quebras de linha
    texto = discord.utils.escape_markdown(texto)
    return texto if len(texto) <= tamanho else texto[:tamanho] + "…"


async def buscar_tweets(username: str):
    user = await api.user_by_login(username)
    if user is None:
        return None, []
    tweets = await gather(api.user_tweets(user.id, limit=LIMITE_TWEETS))
    # Ordena do mais recente pro mais antigo (o fixado costuma vir primeiro)
    tweets.sort(key=lambda t: t.date, reverse=True)
    return user, tweets[:LIMITE_TWEETS]


def montar_embed(username: str, tweets) -> discord.Embed:
    contagem = Counter(fonte(t) for t in tweets)
    suspeitos = [t for t in tweets if fonte(t) not in FONTES_NORMAIS]
    total = len(tweets)

    # Veredito
    if not suspeitos:
        veredito = f"✅ NORMAL — all {total} tweets came from common clients"
        cor = discord.Color.green()
    elif len(suspeitos) / total > 0.5:
        veredito = f"🚨 HIGH RISK — {len(suspeitos)}/{total} tweet(s) from unusual sources"
        cor = discord.Color.dark_red()
    else:
        veredito = f"⚠️ SUSPICIOUS — {len(suspeitos)}/{total} tweet(s) from unusual sources"
        cor = discord.Color.red()

    embed = discord.Embed(
        title=f"🔎 @{username} — Last {total} tweets",
        url=f"https://x.com/{username}",
        color=cor,
    )

    linhas_fontes = []
    for nome, qtd in contagem.most_common():
        icone = "✅" if nome in FONTES_NORMAIS else "⚠️"
        linhas_fontes.append(f"{icone} **{discord.utils.escape_markdown(nome)}** ({qtd}x)")
    embed.add_field(name="Sources", value="\n".join(linhas_fontes), inline=False)

    if suspeitos:
        linhas_susp = [
            f"⚠️ **{discord.utils.escape_markdown(fonte(t))}:** [\"{resumo(t.rawContent)}\"]({t.url})"
            for t in suspeitos[:MAX_SUSPEITOS_EXIBIDOS]
        ]
        restantes = len(suspeitos) - MAX_SUSPEITOS_EXIBIDOS
        if restantes > 0:
            linhas_susp.append(f"…and {restantes} more")
        embed.add_field(
            name=f"🚨 SUSPICIOUS ({len(suspeitos)})",
            value="\n".join(linhas_susp)[:1024],
            inline=False,
        )

    embed.add_field(name="⚡ Verdict", value=veredito, inline=False)
    embed.set_footer(text="provider: twscrape • analysis by sourceLabel")
    return embed


@bot.tree.command(name="check", description="Analyzes where an account's latest tweets were posted from")
@app_commands.describe(username="The account's @ (with or without @)")
async def check(interaction: discord.Interaction, username: str):
    await interaction.response.defer(thinking=True)
    usuario = username.strip().lstrip("@")

    try:
        user, tweets = await asyncio.wait_for(buscar_tweets(usuario), timeout=TIMEOUT_BUSCA)
    except asyncio.TimeoutError:
        await interaction.followup.send(
            "⏱️ Timed out. The twscrape accounts are probably rate-limited or logged out."
        )
        return
    except Exception as e:
        await interaction.followup.send(f"❌ Error fetching tweets: `{e}`")
        return

    if user is None:
        await interaction.followup.send(f"❌ Account **@{usuario}** not found.")
        return
    if not tweets:
        await interaction.followup.send(f"ℹ️ **@{user.username}** has no visible tweets.")
        return

    await interaction.followup.send(embed=montar_embed(user.username, tweets))


if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise SystemExit("Set DISCORD_TOKEN in the .env file")
    bot.run(DISCORD_TOKEN)