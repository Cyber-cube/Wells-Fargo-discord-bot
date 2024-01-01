import os
import discord
import json
from discord import app_commands
from discord.ext import commands

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))
  try:
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} commands")
  except Exception as e:
    print(e)
    print("Worked!")

@bot.command()
async def ping(ctx):
  latency = round(bot.latency * 1000)
  await ctx.send(f"Pong! {latency}ms")

@bot.tree.command(name="greet")
async def greet(interaction: discord.Interaction):
  await interaction.response.send_message(f"Hello {interaction.user.mention}")

@bot.tree.command(name="say")
@app_commands.describe(message = "What do you want to say")
async def say(interaction: discord.Interaction, message: str):
  await interaction.response.send_message(f"{interaction.user.name} says ```{message}```")

@bot.tree.command(name="register", description="Register yourself")
@app_commands.describe(username= "Your minecraft username")
async def register(interaction: discord.Interaction, username: str):
  id = interaction.user.id
  with open(".data/users_balance.json") as f:
    users_balance = json.load(f)
  if id in users_balance:
    await interaction.response.send_message("You already have an account", ephemeral=True)
  else:
    users_balance[id] = {
      "username": username,
      "balance": 0,
      "transactions": {}
    }
    with open(".data/users_balance.json", "w") as f:
      json.dump(users_balance, f, indent=2)
    await interaction.response.send_message("Successfully created an account", ephemeral=True)

@bot.tree.command(name="deposit", description="Deposit money into your account")
@app_commands.describe(amount="The amount you have deposited", screenshot="The screenshot of your deposit (/db deposit WFB <amount)")
async def depsiit(interaction: discord.Interaction, amount: float, screenshot: discord.Attachment):
  id = interaction.user.id
  with open(".data/users_balance.json") as f:
    users_balance = json.load(f)
  if not id in users_balance:
    await interaction.response.send_message("You don't have an account yet", ephemeral=True)
  elif amount == 0:
    await interaction.response.send_message("You can't deposit 0", ephemeral=True)
  elif amount < 0:
    await interaction.response.send_message("Yoy can't deposit negative number", ephemeral=True)
  elif amount > 0 and amount != 0:
    with open(".data/pending_transactions.json") as file:
      pending_transactions = json.load(file)
    transaction_id = users_balance["latest_transaction_id"] + 1
    users_balance["latest_transaction_id"] = transaction_id
    pending_transactions[transaction_id] = {
      "id": id,
      "username": str(users_balance[id]["username"]),
      "type": "deposit",
      "amount": amount,
      "screenshot": screenshot,
      "is_approved": False
    }
    users_balance[id]["transactions"][transaction_id] = {
      "type": "deposit",
      "amount": amount,
      "screenshot": screenshot,
      "is_approved": False
    }
    with open(".data/users_balance.json", "w") as f:
      json.dump(users_balance, f, indent=2)
    with open(".data/pending_transactions.json", "w") as file:
      json.dump(pending_transactions,  file, indent=2)
    embed = discord.Embed(title="Deposit request sent!", description=f"Your deposit request has been sent, please wait till it's accepted\nTransaction ID: {transaction_id}", color=0x00ff00)
    embed.set_footer(text="You can use /transaction history to view the transaction history too!")
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
bot.run(os.getenv("TOKEN"))
