from discord.ext import commands
import asyncpg
import discord

from utils import checks


def pin_check(m):
    return not m.pinned


class Owner:
    def __init__(self, bot):
        self.bot = bot


###################
#                 #
# PLONKING        #
#                 #
###################

    @checks.db
    @commands.command()
    @commands.is_owner()
    async def plonk(self, ctx, user: discord.Member):
        """Adds a user to the bot's blacklist"""
        try:
            async with ctx.con.transaction():
                await ctx.con.execute('''
                    INSERT INTO plonks (guild_id, user_id) VALUES ($1, $2)
                    ''', ctx.guild.id, user.id)
        except asyncpg.UniqueViolationError:
            await ctx.send('User is already plonked.')
        else:
            await ctx.send('User has been plonked.')

    @checks.db
    @commands.command()
    @commands.is_owner()
    async def unplonk(self, ctx, user: discord.Member):
        """Removes a user from the bot's blacklist"""
        async with ctx.con.transaction():
            res = await ctx.con.execute('''
                DELETE FROM plonks WHERE guild_id = $1 and user_id = $2
                ''', ctx.guild.id, user.id)
        deleted = int(res.split()[-1])
        if deleted:
            await ctx.send('User is no longer plonked.')
        else:
            await ctx.send('User is not plonked.')

###################
#                 #
# COGS            #
#                 #
###################

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, *, ext):
        """Reload a cog."""
        if not ext.startswith('cogs.'):
            ext = f'cogs.{ext}'
        try:
            self.bot.unload_extension(ext)
        except:
            pass
        try:
            self.bot.load_extension(ext)
        except Exception as e:
            await ctx.send(e)
        else:
            await ctx.send(f'Cog {ext} reloaded.')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, ext):
        """Load a cog."""
        if not ext.startswith('cogs.'):
            ext = f'cogs.{ext}'
        try:
            self.bot.load_extension(ext)
        except Exception as e:
            await ctx.send(e)
        else:
            await ctx.send(f'Cog {ext} loaded.')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, ext):
        """Unload a cog."""
        if not ext.startswith('cogs.'):
            ext = f'cogs.{ext}'
        try:
            self.bot.unload_extension(ext)
        except:
            await ctx.send(f'Cog {ext} is not loaded.')
        else:
            await ctx.send(f'Cog {ext} unloaded.')

###################
#                 #
# DATABASE        #
#                 #
###################

    @checks.db
    @commands.command(hidden=True, name='execute')
    @commands.is_owner()
    async def _execute(self, ctx, *, sql: str):
        await ctx.con.execute(sql)
        await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')

    @checks.db
    @commands.command(hidden=True, name='fetchval')
    @commands.is_owner()
    async def _fetchval(self, ctx, *, sql: str):
        val = await ctx.con.fetchval(sql)
        await ctx.send(val)


def setup(bot):
    bot.add_cog(Owner(bot))