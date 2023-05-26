# botcbot.py
import os
import discord
import random
from dotenv import load_dotenv
from discord import app_commands, Member, Guild
from typing import List, Optional, Literal
import botc_dom
from botc_dom import Game, Player, Round, Nomination, Vote
import embed_builder
from logging_manager import logger
import time
from random import randrange

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))
PLAYER_ROLE_ID = int(os.getenv('PLAYER_ROLE_ID'))
VOTE_CHANNEL = int(os.getenv('VOTE_CHANNEL'))
MODERATOR_ACTION_CHANNEL = int(os.getenv('MODERATOR_ACTION_CHANNEL'))
MODERATOR_ROLE_ID = int(os.getenv('MODERATOR_ROLE_ID'))
BASE_PATH = os.getenv('BASE_PATH')

'''
game_factions = Literal["A",
                        "Van der Linde Gang",
                        "O'Driscoll Boys",
                        "Lemoyne Raiders",
                        "Del Lobo Gang",
                        "Pinkerton Detective Agency",
                        "Robber Baron - Cornwall",
                        "Robber Baron - Bronte",
                        "Robber Baron - Braithwaite",
                        "Robber Baron - Gray",
                        "Robber Baron - Fussar"]
'''
embed_choices = embed_builder.build_embeds()


class BotCBotClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild=discord.Object(id=GUILD_ID))
            self.synced = True
        print(f"We have logged in as {self.user}.")


client = BotCBotClient()
tree = app_commands.CommandTree(client)


async def player_list_autocomplete(interaction: discord.Interaction,
                                   current: str,
                             ) -> List[app_commands.Choice[str]]:
    game = await get_game(BASE_PATH)
    players = await get_valid_players(current, game.players)
    return [
        app_commands.Choice(name=player.player_discord_name, value=str(player.player_id))
        for player in players
    ]


async def get_valid_players(substr: str, players: List[Player]) -> List[Player]:
    player_list = []
    for player in sorted(players, key=lambda e: e.player_discord_name.lower()):
        if substr and substr.lower() not in player.player_discord_name.lower():
            continue
        if not player.is_dead:
            player_list.append(player)
    return player_list[:25]


async def vote_list_autocomplete(interaction: discord.Interaction,
                                   current: str,
                                   ) -> List[app_commands.Choice[str]]:
    game = await get_game(BASE_PATH)
    players = await get_valid_votes(current, game.players)
    return [
        app_commands.Choice(name=player.player_discord_name, value=str(player.player_id))
        for player in players
    ]


async def get_valid_votes(substr: str, players: List[Player]) -> List[Player]:
    player_list = []
    game = await get_game(BASE_PATH)
    latest_round = game.get_latest_round()
    for player in sorted(players, key=lambda e: e.player_discord_name.lower()):
        if substr and substr.lower() not in player.player_discord_name.lower():
            continue
        if str(player.player_id) in latest_round.get_nominated_player_ids():
            player_list.append(player)
    return player_list[:25]


@tree.command(name="toggle-activity",
              description="Enables/Disables bot commands for players",
              guild=discord.Object(id=GUILD_ID))
@app_commands.default_permissions(manage_guild=True)
async def toggle_activity(interaction: discord.Interaction,
                          active: Literal['True', 'False']):
    log_interaction_call(interaction)
    game = await get_game(BASE_PATH)

    game.is_active = True if active == 'True' else False

    await write_game(game, BASE_PATH)
    await interaction.response.send_message(f'Game state has been set to {active}!', ephemeral=True)


@tree.command(name="post-embed",
              description="Posts a pre-computed embed to a channel",
              guild=discord.Object(id=GUILD_ID))
@app_commands.default_permissions(manage_guild=True)
@app_commands.choices(embed=embed_choices)
async def post_embed(interaction: discord.Interaction,
                     embed: str,
                     channel: discord.TextChannel):
    log_interaction_call(interaction)
    embed_list = embed_builder.get_embed_dict().get(embed)

    await interaction.response.send_message(f"Post embed to channel {channel.name}", ephemeral=True)

    for embed_to_post in embed_list:
        await channel.send(embed=embed_to_post)


@tree.command(name="clear-messages",
              description="Clears up to 100 messages out of a discord channel",
              guild=discord.Object(id=GUILD_ID))
@app_commands.default_permissions(manage_guild=True)
async def clear_messages(interaction: discord.Interaction,
                         channel: discord.TextChannel,
                         channel_again: discord.TextChannel
                     ):
    log_interaction_call(interaction)

    if channel != channel_again:
        await interaction.response.send_message(f"Both channel arguments must be the same! This is a safety feature!")

    await interaction.response.send_message(f"Clearing messages from channel {channel.name}")
    await channel.purge(limit=100)
'''
@tree.command(name="add-faction",
              description="Adds a faction to the game",
              guild=discord.Object(id=GUILD_ID))
@app_commands.default_permissions(manage_guild=True)
async def add_faction(interaction: discord.Interaction,
                      faction: game_factions,
                      assets: app_commands.Range[int, 0, 50] = 0):
    log_interaction_call(interaction)
    game = await get_game(BASE_PATH)

    existing_faction = game.get_faction(faction)

    if existing_faction is None:
        new_faction = Faction(player_ids=[],
                              faction_name=faction,
                              assets=assets)
        game.add_faction(new_faction)

        await write_game(game, BASE_PATH)
        await interaction.response.send_message(f'Added faction {faction} to game with initial assets {assets}',
                                                ephemeral=True)
    else:
        await interaction.response.send_message(f'Failed to add faction {faction} to game!', ephemeral=True)
'''


@tree.command(name="add-player",
              description="Adds a player to the game",
              guild=discord.Object(id=GUILD_ID))
@app_commands.default_permissions(manage_guild=True)
async def add_player(interaction: discord.Interaction,
                     player: discord.Member,
                     alt_name: Optional[str] = None,
                     seat: Optional[int] = None):
                     #faction: game_factions,
                     #assets: app_commands.Range[int, 0, 50] = 0,
                     #faction_boss: Optional[Literal['True', 'False']] = 'False',
                     #withdraw_limit: Optional[int] = 2):
    log_interaction_call(interaction)
    game = await get_game(BASE_PATH)
    '''
    game_faction = game.get_faction(faction)
    existing_faction = game.get_faction_of_player(player.id)

    # Faction needs to exist first
    if game_faction is None:
        await interaction.response.send_message(
            f'Faction {faction} has not been defined yet! Please define this faction first!', ephemeral=True)
        return

    # Player can only exist in one faction at a time
    if existing_faction is not None:
        await interaction.response.send_message(
            f'Player already found in faction {existing_faction.faction_name}! Player can only exist in one faction!',
            ephemeral=True)
        return
    '''
    if game.get_player(player.id) is None:
        MOD_CHAT_CATEGORY = int(os.getenv('MOD_CHAT_CATEGORY'))
        guild = interaction.guild
        #category = discord.utils.get(guild.categories, id=MOD_CHAT_CATEGORY)
        chosen_player_ID = int(player.id)
        '''
        permissionOverwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.get_member(chosen_player_ID): discord.PermissionOverwrite(
                read_messages=True, read_message_history=True, add_reactions=True, attach_files=True,
                embed_links=True, external_emojis=True, external_stickers=True, manage_messages=False,
                mention_everyone=False, manage_channels=False, manage_permissions=False, manage_webhooks=False,
                create_instant_invite=False, send_messages=True, send_messages_in_threads=True,
                create_private_threads=False, create_public_threads=False, manage_threads=False,
                send_tts_messages=True, use_application_commands=True
            ),
        }
        '''
        if alt_name is None:
            use_name = player.name
        else:
            use_name = alt_name
        '''
        channelname1 = str('test-')+ str(use_name) + str('-mod-chat')
        channelnamemod = channelname1.lower()
        await guild.create_text_channel(name=channelnamemod, category=category, overwrites=permissionOverwrites)
        mod_channel = discord.utils.get(guild.text_channels, name=channelnamemod)
        mod_channel_id = int(mod_channel.id)
        OVERSEER_CHAT_CATEGORY = int(os.getenv('OVERSEER_CHAT_CATEGORY'))
        category_os = discord.utils.get(guild.categories, id=OVERSEER_CHAT_CATEGORY)
        permissionOverwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.get_member(chosen_player_ID): discord.PermissionOverwrite(
                read_messages=True, read_message_history=True, add_reactions=False, attach_files=False,
                embed_links=False, external_emojis=False, external_stickers=False, manage_messages=False,
                mention_everyone=False, manage_channels=False, manage_permissions=False, manage_webhooks=False,
                create_instant_invite=False, send_messages=True, send_messages_in_threads=False,
                create_private_threads=False, create_public_threads=False, manage_threads=False,
                send_tts_messages=True, use_application_commands=True
            ),
            guild.get_role(1062435912589516830): discord.PermissionOverwrite(
                read_messages=True, read_message_history=True, add_reactions=False, attach_files=False,
                embed_links=False, external_emojis=False, external_stickers=False, manage_messages=False,
                mention_everyone=False, manage_channels=False, manage_permissions=False, manage_webhooks=False,
                create_instant_invite=False, send_messages=True, send_messages_in_threads=False,
                create_private_threads=False, create_public_threads=False, manage_threads=False,
                send_tts_messages=True, use_application_commands=True
            )
        }
        channelname2 = str(use_name) + str('-overseer-chat')
        channelnameos = channelname2.lower()
        await guild.create_text_channel(name=channelnameos, category=category_os, overwrites=permissionOverwrites)
        overseer_channel = discord.utils.get(guild.text_channels, name=channelnameos)
        overseer_channel_id = int(overseer_channel.id)
        '''
        new_player = Player(player_id=player.id,
                            player_discord_name=use_name,
                            #mod_channel=mod_channel_id,
                            seat=seat)
                            #faction_name=faction,
                            #assets=assets,
                            #tension=0,
                            #withdraw_limit=withdraw_limit,
                            #is_faction_boss=True if faction_boss == 'True' else False)
        game.add_player(new_player)
        #game_faction.add_player(player.id)
        await write_game(game, BASE_PATH)
        await interaction.response.send_message(f'Added player {use_name} to game.', ephemeral=True)
    else:
        await interaction.response.send_message(f'Failed to add {player.name} to game.', ephemeral=True)


@tree.command(name="start-round",
              description="Creates and enables the current round, if possible",
              guild=discord.Object(id=GUILD_ID))
@app_commands.default_permissions(manage_guild=True)
async def start_round(interaction: discord.Interaction):
    log_interaction_call(interaction)
    game = await get_game(BASE_PATH)

    latest_round = game.get_latest_round()

    if latest_round is None:
        new_round = Round(nominations=[], round_number=1, is_active_round=True)
        game.add_round(new_round)
    elif latest_round.is_active_round:
        await interaction.response.send_message(f'There is already an active round; you must end the existing round first before creating another', ephemeral=True)
        return
    else:
        new_round = Round(nominations=[], round_number=latest_round.round_number + 1, is_active_round=True)
        game.add_round(new_round)

    await write_game(game, BASE_PATH)
    await interaction.response.send_message(f'Created round {new_round.round_number}!', ephemeral=True)


@tree.command(name="end-round",
              description="Ends the current round, if possible",
              guild=discord.Object(id=GUILD_ID))
@app_commands.default_permissions(manage_guild=True)
async def end_round(interaction: discord.Interaction):
    log_interaction_call(interaction)
    game = await get_game(BASE_PATH)

    latest_round = game.get_latest_round()

    if latest_round is None:
        await interaction.response.send_message(f'There is not currently an active round to end!', ephemeral=True)
        return
    else:
        latest_round.is_active_round = False

    await write_game(game, BASE_PATH)
    await interaction.response.send_message(f'Ended round {latest_round.round_number}!', ephemeral=True)
'''


@tree.command(name="incarcerate-player",
              description="Toggles a player status of being incarcerated or not.",
              guild=discord.Object(id=GUILD_ID))
@app_commands.default_permissions(manage_guild=True)
@app_commands.autocomplete(player=player_list_autocomplete)
async def incarcerate_player(interaction: discord.Interaction,
                             player: str,
                             incarcerated: Literal['True', 'False']):
    log_interaction_call(interaction)
    game = await get_game(BASE_PATH)

    this_player = game.get_player(int(player))
    if this_player is None:
        await interaction.response.send_message(f'The selected player is not currently defined in this game!',
                                                ephemeral=True)
    else:
        this_player.is_incarcerated = True if incarcerated == 'True' else False

        await write_game(game, BASE_PATH)
        await interaction.response.send_message(f'Set incarceration status of {this_player.player_discord_name} to {incarcerated}!', ephemeral=True)
'''


@tree.command(name="kill-player",
              description="Toggles a player status of being dead or not.",
              guild=discord.Object(id=GUILD_ID))
@app_commands.default_permissions(manage_guild=True)
@app_commands.autocomplete(player=player_list_autocomplete)
async def kill_player(interaction: discord.Interaction,
                      player: str,
                      dead: Literal['True', 'False']):
    log_interaction_call(interaction)
    game = await get_game(BASE_PATH)

    this_player = game.get_player(int(player))
    if this_player is None:
        await interaction.response.send_message(f'The selected player is not currently defined in this game!',ephemeral=True)
    else:
        this_player.is_dead = True if dead == 'True' else False

        await write_game(game, BASE_PATH)
        await interaction.response.send_message(f'Set dead status of {this_player.player_discord_name} to {dead}!', ephemeral=True)


'''
@tree.command(name="refresh-specials",
              description="Refreshes specials",
              guild=discord.Object(id=GUILD_ID))
@app_commands.default_permissions(manage_guild=True)
async def refresh_specials(interaction: discord.Interaction):
    log_interaction_call(interaction)
    game = await get_game(BASE_PATH)

    for player in game.players:
        if not player.is_dead:
            player.daily_special_available = True

    await write_game(game, BASE_PATH)
    await interaction.response.send_message(f'Refreshed the daily special for all players!', ephemeral=True)


@tree.command(name="deposit",
              description="Deposit assets from your personal stash to your faction's holdings",
              guild=discord.Object(id=GUILD_ID))
@app_commands.checks.cooldown(1, 5, key=lambda i: i.guild_id)
async def deposit(interaction: discord.Interaction,
                  amount: app_commands.Range[int, 0, 20]):
    log_interaction_call(interaction)
    game = await get_game(BASE_PATH)

    if not game.is_active:
        await interaction.response.send_message(
            f'The bot has been put in an inactive state by the moderator. Please try again later.', ephemeral=True)
        return

    depositing_player = game.get_player(interaction.user.id)
    player_faction = game.get_faction_of_player(interaction.user.id)

    if depositing_player is None:
        await interaction.response.send_message(f'Player {interaction.user.name} is not currently defined in this game!', ephemeral=True)
    elif player_faction is None:
        await interaction.response.send_message(f'Player {interaction.user.name} does not have a valid faction!', ephemeral=True)
    elif depositing_player.is_dead or depositing_player.is_incarcerated:
        await interaction.response.send_message(f'Incarcerated or dead players cannot deposit assets!', ephemeral=True)
    else:
        if depositing_player.assets < amount:
            await interaction.response.send_message(f'Amount {amount} exceeds available assets of {depositing_player.assets}! Cannot deposit that amount!', ephemeral=True)
            return
        else:
            depositing_player.set_assets(depositing_player.assets - amount)
            player_faction.set_assets(player_faction.assets + amount)

            await write_game(game, BASE_PATH)
            await interaction.response.send_message(f'Deposited {amount} assets to {player_faction.faction_name}', ephemeral=True)
            await interaction.followup.send(f'Current personal assets are {depositing_player.assets}', ephemeral=True)

@tree.command(name="withdraw",
              description="Withdraw assets from your faction's holdings into your personal stash",
              guild=discord.Object(id=GUILD_ID))
@app_commands.checks.cooldown(1, 5, key=lambda i: i.guild_id)
async def withdraw(interaction: discord.Interaction,
                   amount: app_commands.Range[int, 0, 20]):
    log_interaction_call(interaction)
    game = await get_game(BASE_PATH)

    if not game.is_active:
        await interaction.response.send_message(
            f'The bot has been put in an inactive state by the moderator. Please try again later.', ephemeral=True)
        return

    withdrawing_player = game.get_player(interaction.user.id)
    player_faction = game.get_faction_of_player(interaction.user.id)

    if withdrawing_player is None:
        await interaction.response.send_message(f'Player {interaction.user.name} is not currently defined in this game!', ephemeral=True)
    elif player_faction is None:
        await interaction.response.send_message(f'Player {interaction.user.name} does not have a valid faction!', ephemeral=True)
    elif withdrawing_player.is_dead or withdrawing_player.is_incarcerated:
        await interaction.response.send_message(f'Incarcerated or dead players cannot withdraw assets!', ephemeral=True)
    else:
        if player_faction.assets < amount:
            await interaction.response.send_message(f'Amount {amount} exceeds available assets! Cannot withdraw that amount!', ephemeral=True)
        elif amount > withdrawing_player.withdraw_limit:
            await interaction.response.send_message(f'Amount {amount} exceeds withdrawal limit of {withdrawing_player.withdraw_limit}! Cannot Withdraw that amount!', ephemeral=True)
        elif not withdrawing_player.daily_withdraw_available:
            await interaction.response.send_message(f'No remaining withdrawals available for this phase!', ephemeral=True)
        else:
            withdrawing_player.daily_withdraw_available = False
            player_faction.set_assets(player_faction.assets - amount)
            withdrawing_player.set_assets(withdrawing_player.assets + amount)

            await write_game(game, BASE_PATH)
            await interaction.response.send_message(f'Withdrew {amount} assets from {player_faction.faction_name} holdings!', ephemeral=True)
            await interaction.followup.send(f'Current personal assets are {withdrawing_player.assets}', ephemeral=True)

@tree.command(name="transfer",
              description="Transfer assets from your personal stash to another player",
              guild=discord.Object(id=GUILD_ID))
@app_commands.checks.cooldown(1, 5, key=lambda i: i.guild_id)
@app_commands.autocomplete(player=player_list_autocomplete)
async def transfer(interaction: discord.Interaction,
                   player: str,
                   amount: app_commands.Range[int, 0, 20]):
    log_interaction_call(interaction)
    game = await get_game(BASE_PATH)

    if not game.is_active:
        await interaction.response.send_message(
            f'The bot has been put in an inactive state by the moderator. Please try again later.', ephemeral=True)
        return

    sending_player = game.get_player(interaction.user.id)
    receiving_player = game.get_player(int(player))

    if sending_player is None:
        await interaction.response.send_message(
            f'Player {interaction.user.name} is not currently defined in this game!', ephemeral=True)
        return
    elif receiving_player is None:
        await interaction.response.send_message(f'The selected player is not currently defined in this game!', ephemeral=True)
        return
    elif sending_player.is_dead or sending_player.is_incarcerated:
        await interaction.response.send_message(f'Incarcerated or dead players cannot send or receive assets!')
        return
    elif receiving_player.is_dead or receiving_player.is_incarcerated:
        await interaction.response.send_message(f'Incarcerated or dead players cannot send or receive assets!')
        return
    else:
        if sending_player.assets < amount:
            await interaction.response.send_message(
                f'Amount {amount} exceeds available assets of {sending_player.assets}! Cannot send that amount!',
                ephemeral=True)
            return
        else:
            sending_player.set_assets(sending_player.assets - amount)
            receiving_player.set_assets(receiving_player.assets + amount)

            await write_game(game, BASE_PATH)
            await interaction.response.send_message(f'Transferred {amount} assets to {receiving_player.player_discord_name}', ephemeral=True)
            await interaction.followup.send(f'Current personal assets are {sending_player.assets}', ephemeral=True)

@tree.command(name="balance",
              description="Get the current balance of assets in your personal stash, or your faction's holdings",
              guild=discord.Object(id=GUILD_ID))
@app_commands.checks.cooldown(1, 5, key=lambda i: i.guild_id)
async def balance(interaction: discord.Interaction,
                  of_type: Literal['Player', 'Faction', 'Tension']):
    log_interaction_call(interaction)
    game = await get_game(BASE_PATH)

    # if not game.is_active:
    #     await interaction.response.send_message(f'The bot has been put in an inactive state by the moderator. Please try again later.', ephemeral=True)
    #     return

    requesting_player = game.get_player(interaction.user.id)

    if of_type == "Player":
        if requesting_player is None or requesting_player.is_dead:
            await interaction.response.send_message(f'Player {interaction.user.name} was not found in this game!', ephemeral=True)
        else:
            await interaction.response.send_message(f'Current personal assets for player {interaction.user.name} is {requesting_player.assets}', ephemeral=True)

    elif of_type == "Tension":
        if requesting_player is None or requesting_player.is_dead:
            await interaction.response.send_message(f'Player {interaction.user.name} was not found in this game!', ephemeral=True)
        else:
            await interaction.response.send_message(f'Current tension level for player {interaction.user.name} is {requesting_player.tension}', ephemeral=True)
    else:
        if requesting_player is None or requesting_player.is_dead:
            await interaction.response.send_message(f'Player {interaction.user.name} was not found in this game!', ephemeral=True)
            return
        elif not requesting_player.is_faction_boss:
            await interaction.response.send_message(f'Only faction-boss players may view faction asset holdings!', ephemeral=True)
            return

        requested_faction = game.get_faction_of_player(interaction.user.id)
        if requested_faction is None:
            await interaction.response.send_message(f'Could not find faction for player {interaction.user.name}!', ephemeral=True)
        else:
            await interaction.response.send_message(f'Current faction holdings for Faction {requested_faction.faction_name} is {requested_faction.assets}', ephemeral=True)

@tree.command(name="day-action",
              description="Tracks and notifies moderators of day action submissions that have a cost associated with them",
              guild=discord.Object(id=GUILD_ID))
@app_commands.checks.cooldown(1, 5, key=lambda i: i.guild_id)
async def day_action(interaction: discord.Interaction,
                     action: str,
                     cost: app_commands.Range[int, 0, 20]):
    log_interaction_call(interaction)
    game = await get_game(BASE_PATH)

    if not game.is_active:
        await interaction.response.send_message(f'The bot has been put in an inactive state by the moderator. Please try again later.', ephemeral=True)
        return

    requesting_player = game.get_player(interaction.user.id)

    if requesting_player is None:
        await interaction.response.send_message(f'Player {interaction.user.name} is not currently defined in this game!', ephemeral=True)
        return
    elif requesting_player.is_dead or requesting_player.is_incarcerated:
        await interaction.response.send_message(f'Incarcerated or dead players cannot use actions!')
        return
    else:
        if requesting_player.assets < cost:
            await interaction.response.send_message(f'Amount {cost} exceeds available assets of {requesting_player.assets}! Cannot perform this action!', ephemeral=True)
            return
        else:
            mod_action_channel = interaction.guild.get_channel(MODERATOR_ACTION_CHANNEL)

            requesting_player.set_assets(requesting_player.assets - cost)
            await write_game(game, BASE_PATH)
            await interaction.response.send_message(f'Submitted request for action {action} at a cost of {cost} assets', ephemeral=True)
            await mod_action_channel.send(f'<@&{MODERATOR_ROLE_ID}>\nPlayer **{requesting_player.player_discord_name}** has submitted an action request of **{action}** and has paid **{cost}** assets')
'''


@tree.command(name="nominate-player",
              description="Nominates a particular player",
              guild=discord.Object(id=GUILD_ID))
@app_commands.checks.cooldown(1, 5, key=lambda i: i.guild_id)
@app_commands.autocomplete(player=player_list_autocomplete)
async def nominate_player(interaction: discord.Interaction,
                      player: str):
    log_interaction_call(interaction)
    game = await get_game(BASE_PATH)

    if not game.is_active:
        await interaction.response.send_message(f'The bot has been put in an inactive state by the moderator. Please try again later.', ephemeral=True)
        return

    latest_round = game.get_latest_round()
    if latest_round is None or not latest_round.is_active_round:
        await interaction.response.send_message(f'No currently active round found for this game!', ephemeral=True)
        return

    requesting_player = game.get_player(interaction.user.id)
    if requesting_player is None or requesting_player.is_dead:
        await interaction.response.send_message(f'Player {interaction.user.name} was not found in this game!', ephemeral=True)
        return

    if player is not None and player not in game.get_living_player_ids():
        await interaction.response.send_message(f'Invalid player selection! Please resubmit your nomination.', ephemeral=True)
        return

    if player in latest_round.get_nominated_player_ids():
        await interaction.response.send_message(f'Player is already nominated.',
                                                ephemeral=True)
        return

    nominated_player = None if player is None else game.get_player(int(player))

    if nominated_player is not None and nominated_player.is_dead:
        await interaction.response.send_message(f'Player {nominated_player.player_discord_name} is dead and cannot be nominated!', ephemeral=True)
    else:
        round_current_player_nomination = latest_round.get_player_nomination(requesting_player.player_id)
        if nominated_player is None:
            await interaction.response.send_message(f'Invalid player selection! Please resubmit your nomination.',
                                                    ephemeral=True)
            return
        else:
            if round_current_player_nomination is None:
                latest_round.add_nomination(Nomination([], requesting_player.player_id, int(nominated_player.player_id), round(time.time())+60*60*24))
            else:
                await interaction.response.send_message(f'You have already nominated this round.',
                                                        ephemeral=True)
                return
        await write_game(game, BASE_PATH)

        success_nomination_target = nominated_player.player_discord_name
        await interaction.response.send_message(f'Registered Nomination for {success_nomination_target}!', ephemeral=True)

        vote_channel = interaction.guild.get_channel(VOTE_CHANNEL)

        response_value = nominated_player.player_discord_name

        if vote_channel is not None:
            await interaction.followup.send(f'Sending public nomination announcement in channel #{vote_channel}', ephemeral=True)
            await vote_channel.send(f'Player **{requesting_player.player_discord_name}** has nominated **{response_value}**')
        else:
            await interaction.followup.send(f'Sending public nomination results now...', ephemeral=True)
            await interaction.followup.send(f'Player **{requesting_player.player_discord_name}** has nominated **{response_value}**', ephemeral=False)


@tree.command(name="vote-player",
              description="Votes an already nominated player",
              guild=discord.Object(id=GUILD_ID))
@app_commands.checks.cooldown(1, 5, key=lambda i: i.guild_id)
@app_commands.autocomplete(player=vote_list_autocomplete)
async def vote_player(interaction: discord.Interaction,
                      player: str,
                      is_for: bool,
                      hidden: bool):
    log_interaction_call(interaction)
    game = await get_game(BASE_PATH)

    if not game.is_active:
        await interaction.response.send_message(f'The bot has been put in an inactive state by the moderator. Please try again later.', ephemeral=True)
        return

    latest_round = game.get_latest_round()
    if latest_round is None or not latest_round.is_active_round:
        await interaction.response.send_message(f'No currently active round found for this game!', ephemeral=True)
        return

    requesting_player = game.get_player(interaction.user.id)
    if requesting_player is None or requesting_player.is_dead:
        await interaction.response.send_message(f'Player {interaction.user.name} was not found in this game!', ephemeral=True)
        return

    if player is not None and player not in game.get_living_player_ids():
        await interaction.response.send_message(f'Invalid player selection! Please resubmit your vote.', ephemeral=True)
        return

    voted_player = game.get_player(int(player))

    if voted_player is not None and voted_player.is_dead:
        await interaction.response.send_message(f'Player {voted_player.player_discord_name} is dead and cannot be voted!', ephemeral=True)
    else:
        active_nomination = latest_round.get_nomination_from_nominated_id(voted_player.player_id)
        nomination_current_player_vote = active_nomination.get_player_vote(requesting_player.player_id)
        if round(time.time()) > active_nomination.end_time:
            await interaction.response.send_message(f'Voting has closed on that nomination',
                                                    ephemeral=True)
            return
        if voted_player is None:
            await interaction.response.send_message(f'Invalid player selection! Please resubmit your nomination.',
                                                    ephemeral=True)
            return
        else:
            if nomination_current_player_vote is None:
                active_nomination.add_vote(Vote(requesting_player.player_id, is_for, round(time.time()), hidden))
            else:
                start_seat = game.get_player(active_nomination.nominated_id).seat
                if start_seat == len(game.players):
                    current_seat = 1
                else:
                    current_seat = start_seat + 1
                vote_locked = True
                while vote_locked and current_seat != requesting_player.seat:
                    temp_player = game.get_player_with_seat(current_seat)
                    temp_vote = active_nomination.get_player_vote(temp_player.player_id)
                    if temp_vote is None:
                        vote_locked = False
                    else:
                        if current_seat == len(game.players):
                            current_seat = 1
                        else:
                            current_seat = current_seat + 1
                if vote_locked:
                    await interaction.response.send_message(f'Your vote in this nomination is locked', ephemeral=True)
                    return
                else:
                    nomination_current_player_vote.is_for = is_for
                    nomination_current_player_vote.timestamp = round(time.time())
        await write_game(game, BASE_PATH)

        success_voted_target = voted_player.player_discord_name
        if hidden:
            for_str = "hidden"
        else:
            if is_for:
                for_str = "for"
            else:
                for_str = "against"
        await interaction.response.send_message(f'Voted {for_str} {success_voted_target}!', ephemeral=True)

        vote_channel = interaction.guild.get_channel(VOTE_CHANNEL)

        response_value = voted_player.player_discord_name

        if vote_channel is not None:
            await interaction.followup.send(f'Sending public vote announcement in channel #{vote_channel}', ephemeral=True)
            await vote_channel.send(f'Player **{requesting_player.player_discord_name}** has voted {for_str} **{response_value}**')
        else:
            await interaction.followup.send(f'Sending public vote results now...', ephemeral=True)
            await interaction.followup.send(f'Player **{requesting_player.player_discord_name}** has voted {for_str} **{response_value}**', ephemeral=False)


@tree.command(name="vote-report",
              description="Generates a report of current voting totals",
              guild=discord.Object(id=GUILD_ID))
@app_commands.checks.cooldown(1, 5, key=lambda i: i.guild_id)
async def vote_report(interaction: discord.Interaction,
                      for_round: Optional[app_commands.Range[int, 0, 20]] = None,
                      with_history: Optional[Literal['Yes', 'No']] = 'No'):
    log_interaction_call(interaction)
    game = await get_game(BASE_PATH)

    if not game.is_active:
        await interaction.response.send_message(f'The bot has been put in an inactive state by the moderator. Please try again later.', ephemeral=True)
        return

    if for_round is None:
        report_round = game.get_latest_round()
    else:
        report_round = game.get_round(for_round)

    if report_round is None:
        await interaction.response.send_message(f'No active or matching round found for this game!', ephemeral=True)
        return

    formatted_votes = f"**Vote Totals for round {report_round.round_number} as of <t:{int(time.time())}>**\n"
    formatted_votes += "\n"
    for nomination in report_round.nominations:
        nominated = game.get_player(nomination.nominated_id).player_discord_name
        nominator = game.get_player(nomination.nominator_id).player_discord_name
        end_time = nomination.end_time
        formatted_votes += f"Votes for **{nominated}** (nominated by {nominator}, ends <t:{end_time}:R>):\n"
        for_votes = 0
        against_votes = 0
        hidden_votes = 0
        start_seat = game.get_player(nomination.nominated_id).seat
        if start_seat == len(game.players):
            current_seat = 1
        else:
            current_seat = start_seat + 1
        i = 1  # Next to vote tracker
        while current_seat != start_seat:
            player = game.get_player_with_seat(current_seat)
            formatted_voter = player.player_discord_name
            vote = nomination.get_player_vote(player.player_id)
            if vote is None:
                if i == 1:
                    vote_str = 'Next to vote'
                    i += 1
                else:
                    vote_str = 'Not yet voted'
            else:
                if vote.hidden and i != 1:
                    vote_str = 'Hidden Vote'
                    hidden_votes += 1
                else:
                    if vote.is_for:
                        vote_str = 'For'
                        for_votes += 1
                    else:
                        vote_str = 'Against'
                        against_votes += 1
            formatted_votes += f"   {formatted_voter}: {vote_str}"
            formatted_votes += "\n"
            if current_seat == len(game.players):
                current_seat = 1
            else:
                current_seat = current_seat + 1
        current_seat = start_seat
        player = game.get_player_with_seat(current_seat)
        formatted_voter = player.player_discord_name
        vote = nomination.get_player_vote(player.player_id)
        if vote is None:
            if i == 1:
                vote_str = 'Next to vote'
                i += 1
            else:
                vote_str = 'Not yet voted'
        else:
            if vote.is_for:
                vote_str = 'For'
            else:
                vote_str = 'Against'
        formatted_votes += f"   {formatted_voter}: {vote_str}"
        formatted_votes += "\n"
        formatted_votes += f"    For: {for_votes}, Against: {against_votes}, Hidden: {hidden_votes}\n"
        formatted_votes = formatted_votes.rstrip(', ')
        formatted_votes += "\n"
    formatted_votes += "\n"

    vote_channel = interaction.guild.get_channel(VOTE_CHANNEL)

    if vote_channel is not None:
        await interaction.response.send_message(f'Sending query response in channel ', ephemeral=True)
        await vote_channel.send(formatted_votes)
    else:
        await interaction.response.send_message(f'Sending vote results now...', ephemeral=True)
        await interaction.followup.send(formatted_votes, ephemeral=False)

    #With History to-be-implemented


'''
@tree.command(name="private-channel",
              description="Creates a private channel with a given name",
              guild=discord.Object(id=GUILD_ID))
#@app_commands.default_permissions(manage_guild=True)
@app_commands.checks.cooldown(1, 5, key=lambda i: i.guild_id)
@app_commands.autocomplete(player=player_list_autocomplete)
async def private_channel(interaction: discord.Interaction,
                       channelname: str,
                       player: str):
    log_interaction_call(interaction)
    game = await get_game(BASE_PATH)
    if not game.is_active:
        await interaction.response.send_message(f'The bot has been put in an inactive state by the moderator. Please try again later.', ephemeral=True)
        return

    requesting_player = game.get_player(interaction.user.id)
    if requesting_player is None or requesting_player.is_dead:
        await interaction.response.send_message(f'Player {interaction.user.name} was not found in this game!', ephemeral=True)
        return

    if player is not None and player not in game.get_living_player_ids():
        await interaction.response.send_message(f'Invalid player selection! Please resubmit.', ephemeral=True)
        return

    chosen_player = None if player is None else game.get_player(int(player))

    if chosen_player is not None and chosen_player.is_dead:
        await interaction.response.send_message(f'Player {chosen_player.player_discord_name} is dead and cannot be chosen!', ephemeral=True)
        return

    if chosen_player is None:
        await interaction.response.send_message(f'Player was not found in this game!', ephemeral=True)
        return
    else:
        #await interaction.response.send_message(f'{chosen_player}', ephemeral=True)
        PRIVATE_CHAT_CATEGORY = int(os.getenv('PRIVATE_CHAT_CATEGORY'))
        guild = interaction.guild
        category = discord.utils.get(guild.categories, id=PRIVATE_CHAT_CATEGORY)
        chosen_player_ID = int(chosen_player.player_id)
        #chosen_player_ID = 680823159330570274
        #await interaction.response.send_message(f'{chosen_player_ID}', ephemeral=True)
        #gm = guild.get_member(chosen_player_ID)
        #await interaction.response.send_message(f'{gm}', ephemeral=True)
        permissionOverwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True),
            guild.get_member(chosen_player_ID): discord.PermissionOverwrite(read_messages=True)
        }


        await guild.create_text_channel(name=channelname, category=category, overwrites=permissionOverwrites)
        channelname = channelname.replace(" ", "-")
        new_channel = discord.utils.get(guild.text_channels, name=channelname)
        #new_channel_id = int(new_channel.id)
        mod_action_channel = interaction.guild.get_channel(MODERATOR_ACTION_CHANNEL)
        await interaction.response.send_message(f'Created private channel {new_channel.mention} with **{chosen_player.player_discord_name}**', ephemeral=True)
        await mod_action_channel.send(
            f'<@&{MODERATOR_ROLE_ID}>\n'
            f'Player **{requesting_player.player_discord_name}** has created private channel {new_channel.mention} with **{chosen_player.player_discord_name}**')
        await new_channel.send(f'You can use this chat freely this round until midnight.')


@tree.command(name="private-message",
              description="Sends a private message",
              guild=discord.Object(id=GUILD_ID))
@app_commands.checks.cooldown(1, 5, key=lambda i: i.guild_id)
@app_commands.autocomplete(player=player_list_autocomplete)
async def private_message(interaction: discord.Interaction,
                       player: str,
                       message: str):
    log_interaction_call(interaction)
    game = await get_game(BASE_PATH)
    if not game.is_active:
        await interaction.response.send_message(f'The bot has been put in an inactive state by the moderator. Please try again later.', ephemeral=True)
        return

    requesting_player = game.get_player(interaction.user.id)
    if requesting_player is None or requesting_player.is_dead:
        await interaction.response.send_message(f'Player {interaction.user.name} was not found in this game!', ephemeral=True)
        return

    if player is not None and player not in game.get_living_player_ids():
        await interaction.response.send_message(f'Invalid player selection! Please resubmit.', ephemeral=True)
        return

    chosen_player = None if player is None else game.get_player(int(player))

    if chosen_player is not None and chosen_player.is_dead:
        await interaction.response.send_message(f'Player {chosen_player.player_discord_name} is dead and cannot be chosen!', ephemeral=True)
        return

    if chosen_player is None:
        await interaction.response.send_message(f'Player {player.name} was not found in this game!', ephemeral=True)
        return
    else:
        guild = interaction.guild
        chosen_player_mod_chat = int(chosen_player.mod_channel)
        channel = guild.get_channel(chosen_player_mod_chat)
        await channel.send(f"You have received an anonymous private message: \n '{message}' \n")
        await interaction.response.send_message(f'Sent a message to {chosen_player.player_discord_name} with content:\n'
                                                f'{message}', ephemeral=True)
        mod_action_channel = interaction.guild.get_channel(MODERATOR_ACTION_CHANNEL)
        await mod_action_channel.send(f'{interaction.user.name} Sent a message to {chosen_player.player_discord_name} with content:\n'
                                                f'{message}')


@tree.command(name="reply",
              description="Replies to a private message",
              guild=discord.Object(id=GUILD_ID))
#@app_commands.default_permissions(manage_guild=True)
@app_commands.checks.cooldown(1, 5, key=lambda i: i.guild_id)
async def reply(interaction: discord.Interaction,
                          message_id: int,
                          message_content: str):
    log_interaction_call(interaction)
    game = await get_game(BASE_PATH)
    if not game.is_active:
        await interaction.response.send_message(f'The bot has been put in an inactive state by the moderator. Please try again later.', ephemeral=True)
        return

    requesting_player = game.get_player(interaction.user.id)
    if requesting_player is None or requesting_player.is_dead:
        await interaction.response.send_message(f'Player {interaction.user.name} was not found in this game!', ephemeral=True)
        return

    if message_id not in game.get_message_ids():
        await interaction.response.send_message(f'Could not find message with ID {message_id}', ephemeral=True)
        return
    else:
        initial_message = game.get_message(int(message_id))
        if initial_message.replied_to:
            await interaction.response.send_message(f'Message with ID {message_id} is already replied to', ephemeral=True)
            return
        other_player_id = int(initial_message.from_player_id)
        chosen_player = game.get_player(int(other_player_id))
        guild = interaction.guild
        chosen_player_mod_chat = int(chosen_player.mod_channel)
        channel = guild.get_channel(chosen_player_mod_chat)
        initial_message.replied_to = True
        await write_game(game, BASE_PATH)
        await channel.send(f"You have received a reply to message {message_id} from **{requesting_player.player_discord_name}**: \n "
                           f"'{message_content}'")
        await interaction.response.send_message(
            f'Sent a reply to message id {message_id} with content:\n'
            f'{message_content}', ephemeral=True)
        mod_action_channel = interaction.guild.get_channel(MODERATOR_ACTION_CHANNEL)
        await mod_action_channel.send(
            f'{interaction.user.name} Sent a reply to {chosen_player.player_discord_name} id {message_id} with content:\n'
            f'{message_content}')


@tree.command(name="tannoy",
              description="Make a tannoy announcement",
              guild=discord.Object(id=GUILD_ID))
@discord.app_commands.checks.has_role(1062435912589516830) #Overseer
@app_commands.checks.cooldown(1, 5, key=lambda i: i.guild_id)
async def tannoy(interaction: discord.Interaction,
                       message: str):
    log_interaction_call(interaction)
    game = await get_game(BASE_PATH)
    if not game.is_active:
        await interaction.response.send_message(f'The bot has been put in an inactive state by the moderator. Please try again later.', ephemeral=True)
        return

    requesting_player = game.get_player(interaction.user.id)
    if requesting_player is None or requesting_player.is_dead:
        await interaction.response.send_message(f'Player {interaction.user.name} was not found in this game!', ephemeral=True)
        return

    if not requesting_player.daily_special_available:
        await interaction.response.send_message(f'You have already used this command this round.',ephemeral=True)
    else:
        requesting_player.daily_special_available = False
        await write_game(game, BASE_PATH)
        guild = interaction.guild
        main_channel_id = int(1107339999067774996)
        main_channel = guild.get_channel(main_channel_id)
        await main_channel.send(f"The <@&{1062435912589516830}> has made the following tannoy announcement: \n '{message}' \n")
        await interaction.response.send_message(f'Made a tannoy announcement with content:\n'
                                                f'{message}', ephemeral=True)
        mod_action_channel = interaction.guild.get_channel(MODERATOR_ACTION_CHANNEL)
        await mod_action_channel.send(f'{interaction.user.name} made a tannoy announcement with content:\n'
                                                f'{message}')


def moon_check(interaction: discord.Interaction) -> bool:
    return interaction.user.id == 151506205012000768 or interaction.user.id == 1


@tree.command(name="secret-channel",
              description="Creates/Joins a secret channel",
              guild=discord.Object(id=GUILD_ID))
#@app_commands.check(moon_check)
#@app_commands.default_permissions(manage_guild=True)
@app_commands.checks.cooldown(1, 5, key=lambda i: i.guild_id)
async def private_chat(interaction: discord.Interaction):
    log_interaction_call(interaction)
    game = await get_game(BASE_PATH)
    if not game.is_active:
        await interaction.response.send_message(f'The bot has been put in an inactive state by the moderator. Please try again later.', ephemeral=True)
        return

    requesting_player = game.get_player(interaction.user.id)
    if requesting_player is None or requesting_player.is_dead:
        await interaction.response.send_message(f'Player {interaction.user.name} was not found in this game!', ephemeral=True)
        return

    if not requesting_player.daily_special_available:
        await interaction.response.send_message(f'You have already used this command this round.',ephemeral=True)
    else:
        requesting_player.daily_special_available = False
        await write_game(game, BASE_PATH)
        #await interaction.response.send_message(f'{chosen_player}', ephemeral=True)
        PRIVATE_CHAT_CATEGORY = int(os.getenv('PRIVATE_CHAT_CATEGORY'))
        guild = interaction.guild
        category = discord.utils.get(guild.categories, id=PRIVATE_CHAT_CATEGORY)
        #chosen_player_ID = int(chosen_player.player_id)
        #chosen_player_ID = 680823159330570274
        #await interaction.response.send_message(f'{chosen_player_ID}', ephemeral=True)
        #gm = guild.get_member(chosen_player_ID)
        #await interaction.response.send_message(f'{gm}', ephemeral=True)
        permissionOverwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True)
            #guild.get_member(chosen_player_ID): discord.PermissionOverwrite(read_messages=True)
        }

        current_round = game.get_latest_round()
        current_round_number = str(current_round.round_number)
        channelname = 'secret-channel-round-'+current_round_number
        new_channel = discord.utils.get(guild.text_channels, name=channelname)
        if new_channel is None:
            await guild.create_text_channel(name=channelname, category=category, overwrites=permissionOverwrites)
            new_channel = discord.utils.get(guild.text_channels, name=channelname)
            created = True
            created_text = 'Created'
        else:
            await new_channel.set_permissions(interaction.user, read_messages=True)
            created = False
            created_text = 'Joined'
        #new_channel_id = int(new_channel.id)
        mod_action_channel = interaction.guild.get_channel(MODERATOR_ACTION_CHANNEL)

        await interaction.response.send_message(f'{created_text} secret channel {new_channel.mention}', ephemeral=True)
        await mod_action_channel.send(
            f'<@&{MODERATOR_ROLE_ID}>\n'
            f'Player **{requesting_player.player_discord_name}** has {created_text} secret channel {new_channel.mention}')
        if created:
            await new_channel.send(f'You can use this chat freely this round until midnight.')
        await new_channel.send(f'Player **{requesting_player.player_discord_name}** joined.')
'''


@tree.command(name="assign_random_seating",
              description="Randomly Seats Players",
              guild=discord.Object(id=GUILD_ID))
@app_commands.default_permissions(manage_guild=True)
async def assign_random_seating(interaction: discord.Interaction):
    log_interaction_call(interaction)
    game = await get_game(BASE_PATH)
    players = game.players
    random.shuffle(players)
    i = 0
    output_string = '**Seating:**\n'
    for player in players:
        i = i+1
        player.seat = i
        output_string += f"{str(i)}: {player.player_discord_name}\n"
    await write_game(game, BASE_PATH)
    await interaction.response.send_message(f"{output_string}", ephemeral=True)


@tree.command(name="check_seating",
              description="Check Seating of Players",
              guild=discord.Object(id=GUILD_ID))
# @app_commands.default_permissions(manage_guild=True)
async def check_seating(interaction: discord.Interaction):
    log_interaction_call(interaction)
    game = await get_game(BASE_PATH)
    output_string = '**Seating:**\n'
    for i in range(1, len(game.players)+1):
        player = game.get_player_with_seat(i)
        if player is not None:
            output_string += f"{str(i)}: {player.player_discord_name}\n"
        else:
            output_string += f"{str(i)}: Error\n"
    await interaction.response.send_message(f"{output_string}", ephemeral=True)


@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"Cooldown is in force, please wait for {round(error.retry_after)} seconds", ephemeral=True)
    else:
        raise error

async def get_game(path: str) -> Game:
    json_file_path = f'{path}/game.json'
    logger.info(f'Grabbing game info from {json_file_path}')
    return botc_dom.read_json_to_dom(json_file_path)


async def write_game(game: Game, path: str):
    json_file_path = f'{path}/game.json'
    logger.info(f'Wrote game data to {json_file_path}')
    botc_dom.write_dom_to_json(game, json_file_path)


def log_interaction_call(interaction: discord.Interaction):
    logger.info(
        f'Received command {interaction.command.name} with parameters {interaction.data} initiated by user {interaction.user.name}')

client.run(TOKEN)
