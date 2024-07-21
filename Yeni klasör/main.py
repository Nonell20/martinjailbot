import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

JAIL_ROLE_ID = 1254837898700918804
ALLOWED_ROLE_ID = 1254837897501081642
ENTRY_ROLES = [
    1244049280852033607, 1244198506772693044, 1244203181383356436,
    1244202350743388231, 1244202307105587221, 1244202134325432379,
    1247987363133788281, 1248358964668928081, 1248358948466069634,
    1244198539194667129, 1251272755253346456
]
EXTRA_ROLES = [
    1244049280852033607, 1244049280852033607, 1244198506772693044,
    1244203181383356436, 1244202350743388231, 1244202307105587221,
    1244202134325432379, 1247987363133788281, 1248358964668928081,
    1248358948466069634, 1244198539194667129, 1251272755253346456
]

user_roles = {}

app = Flask('')


@app.route('/')
def home():
    return "I'm alive"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()


keep_alive()


@bot.event
async def on_ready():
    print(f'Bot {bot.user} olarak giriş yaptı!')


@bot.command()
@commands.has_role(ALLOWED_ROLE_ID)
async def jail(ctx, member: discord.Member):
    jail_role = discord.utils.get(ctx.guild.roles, id=JAIL_ROLE_ID)
    if jail_role is None:
        await ctx.send(
            f'Jail rolü bulunamadı. Lütfen `{JAIL_ROLE_ID}` ID\'li rolü oluşturun.'
        )
        return

    if jail_role in member.roles:
        await ctx.send(f'{member.mention} zaten jail rolüne sahip.')
        return

    user_roles[member.id] = [
        role for role in member.roles if role.id != ctx.guild.default_role.id
    ]

    await member.add_roles(jail_role)
    await member.remove_roles(*user_roles[member.id])

    await ctx.send(
        f'{member.mention} isimli üye jail\'e alındı ve tüm rollerini kaybettirdi.'
    )


@bot.command()
@commands.has_role(ALLOWED_ROLE_ID)
async def unjail(ctx, member: discord.Member):
    jail_role = discord.utils.get(ctx.guild.roles, id=JAIL_ROLE_ID)
    if jail_role is None:
        await ctx.send(
            f'Jail rolü bulunamadı. Lütfen `{JAIL_ROLE_ID}` ID\'li rolü oluşturun.'
        )
        return

    if member.id in user_roles:
        await member.remove_roles(jail_role)
        await member.add_roles(*user_roles[member.id])
        del user_roles[member.id]
        await ctx.send(
            f'{member.mention} isimli üye jail\'den çıkarıldı ve eski rollerini geri aldı.'
        )
    else:
        await ctx.send(
            f'{member.mention} isimli üyenin eski rollerini bulamadım.')


@bot.event
async def on_member_join(member):
    jail_role = discord.utils.get(member.guild.roles, id=JAIL_ROLE_ID)
    if jail_role:
        if member.id in user_roles:
            roles_to_remove = [
                discord.utils.get(member.guild.roles, id=role_id)
                for role_id in ENTRY_ROLES
            ]
            roles_to_remove = [
                role for role in roles_to_remove if role in member.roles
            ]
            await member.remove_roles(*roles_to_remove)

            extra_roles_to_remove = [
                discord.utils.get(member.guild.roles, id=role_id)
                for role_id in EXTRA_ROLES
            ]
            extra_roles_to_remove = [
                role for role in extra_roles_to_remove if role in member.roles
            ]
            await member.remove_roles(*extra_roles_to_remove)

            await member.add_roles(jail_role)
            await member.remove_roles(*member.roles)
            await member.add_roles(*user_roles[member.id])
            await member.send(
                f'{member.mention}, sunucuya tekrar katıldığınızda jail rolü tekrar verildi ve eski rolleriniz geri alındı.'
            )
        else:
            pass


bot.run('DISCORD_TOKEN')
