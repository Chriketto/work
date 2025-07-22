import discord
from discord.ext import commands
import sqlite3

TOKEN = 'INSERISCI_IL_TUO_TOKEN_DISCORD'
RUOLO_AUTORIZZATO = 'Soldato'

# Connessione al database
conn = sqlite3.connect('magazzino.db')
c = conn.cursor()

# Creazione tabelle
c.execute('''CREATE TABLE IF NOT EXISTS saldo (
    user_id TEXT PRIMARY KEY,
    dollari REAL DEFAULT 0
)''')

c.execute('''CREATE TABLE IF NOT EXISTS magazzino (
    user_id TEXT,
    oggetto TEXT,
    quantita INTEGER,
    PRIMARY KEY (user_id, oggetto)
)''')

conn.commit()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Helper per check ruolo
def ha_ruolo_autorizzato(ctx):
    return any(r.name == RUOLO_AUTORIZZATO for r in ctx.author.roles)

@bot.event
async def on_ready():
    print(f'Bot connesso come {bot.user}')

@bot.command()
async def saldo(ctx):
    if not ha_ruolo_autorizzato(ctx): return
    user_id = str(ctx.author.id)
    c.execute('SELECT dollari FROM saldo WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    saldo = row[0] if row else 0
    await ctx.send(f"💰 Saldo attuale: ${saldo:.2f}")

@bot.command()
async def aggiungi_saldo(ctx, importo: float):
    if not ha_ruolo_autorizzato(ctx): return
    user_id = str(ctx.author.id)
    c.execute('INSERT INTO saldo (user_id, dollari) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET dollari = dollari + ?', (user_id, importo, importo))
    conn.commit()
    await ctx.send(f"✅ Aggiunti ${importo:.2f} al saldo.")

@bot.command()
async def togli_saldo(ctx, importo: float):
    if not ha_ruolo_autorizzato(ctx): return
    user_id = str(ctx.author.id)
    c.execute('UPDATE saldo SET dollari = dollari - ? WHERE user_id = ?', (importo, user_id))
    conn.commit()
    await ctx.send(f"❌ Rimossi ${importo:.2f} dal saldo.")

@bot.command()
async def aggiungi_oggetto(ctx, nome: str, quantita: int):
    if not ha_ruolo_autorizzato(ctx): return
    user_id = str(ctx.author.id)
    c.execute('INSERT INTO magazzino (user_id, oggetto, quantita) VALUES (?, ?, ?) ON CONFLICT(user_id, oggetto) DO UPDATE SET quantita = quantita + ?', (user_id, nome, quantita, quantita))
    conn.commit()
    await ctx.send(f"📦 Aggiunti {quantita}x {nome} al magazzino.")

@bot.command()
async def togli_oggetto(ctx, nome: str, quantita: int):
    if not ha_ruolo_autorizzato(ctx): return
    user_id = str(ctx.author.id)
    c.execute('UPDATE magazzino SET quantita = quantita - ? WHERE user_id = ? AND oggetto = ?', (quantita, user_id, nome))
    conn.commit()
    await ctx.send(f"📤 Rimossi {quantita}x {nome} dal magazzino.")

@bot.command()
async def magazzino(ctx):
    if not ha_ruolo_autorizzato(ctx): return
    user_id = str(ctx.author.id)
    c.execute('SELECT oggetto, quantita FROM magazzino WHERE user_id = ?', (user_id,))
    righe = c.fetchall()
    if not righe:
        await ctx.send("📭 Il tuo magazzino è vuoto.")
        return
    msg = "📦 Magazzino:\n" + "\n".join([f"- {r[0]}: {r[1]}" for r in righe])
    await ctx.send(msg)

bot.run(TOKEN)
