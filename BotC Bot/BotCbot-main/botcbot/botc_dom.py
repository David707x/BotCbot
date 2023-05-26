#! banker_dom.py
# a class for managing game state details
import json
from typing import Optional, List
from datetime import datetime


class Player:
    def __init__(self, player_id: int, player_discord_name: str, seat: int,
                 is_dead: bool = False):
        self.player_id = player_id
        self.player_discord_name = player_discord_name
        self.is_dead = is_dead
        self.seat = seat


'''
class Message:
    def __init__(self, replied_to: bool, message_id: int, from_player_id: int, to_player_id: int):
        self.replied_to = replied_to
        self.message_id = message_id
        self.from_player_id = from_player_id
        self.to_player_id = to_player_id


class Faction:
    def __init__(self, player_ids: [int], faction_name: str, assets: int):
        self.player_ids = player_ids
        self.faction_name = faction_name
        self.assets = assets

    def add_player(self, player_id: int):
        self.player_ids.append(player_id)

    def set_assets(self, assets: int):
        self.assets = assets
'''


class Vote:
    def __init__(self, player_id: int, is_for: bool, timestamp: int, hidden: bool):
        self.player_id = player_id
        self.is_for = is_for
        self.timestamp = timestamp
        self.hidden = hidden


class Nomination:
    def __init__(self, votes: [Vote], nominator_id: int, nominated_id: int, end_time: int):
        self.nominator_id = nominator_id
        self.nominated_id = nominated_id
        self.votes = votes
        self.end_time = end_time

    def get_player_vote(self, player_id: int) -> Optional[Vote]:
        player_vote = None
        for vote in self.votes:
            if vote.player_id == player_id:
                player_vote = vote
        return player_vote

    def add_vote(self, vote: Vote):
        self.votes.append(vote)

    def remove_vote(self, vote: Vote):
        self.votes.remove(vote)


class Round:
    def __init__(self, nominations: [Nomination], round_number: int, is_active_round: bool):
        self.nominations = nominations
        self.round_number = round_number
        self.is_active_round = is_active_round

    def get_player_nomination(self, player_id: int) -> Optional[Nomination]:
        player_nomination = None
        for nomination in self.nominations:
            if nomination.nominator_id == player_id:
                player_nomination = nomination
        return player_nomination

    def add_nomination(self, nomination: Nomination):
        self.nominations.append(nomination)

    def remove_nomination(self, nomination: Nomination):
        self.nominations.remove(nomination)

    def get_nominated_player_ids(self) -> List[str]:
        nominated_player_ids = []
        for nomination in self.nominations:
            nominated_player_ids.append(str(nomination.nominated_id))
        return nominated_player_ids

    def get_nomination_from_nominated_id(self, nominated_id: int) -> Optional[Nomination]:
        for a_nomination in self.nominations:
            if a_nomination.nominated_id == nominated_id:
                return a_nomination
        return None


class Game:
    def __init__(self, is_active: bool, players: [Player], rounds: [Round]):
        self.is_active = is_active
        ##self.factions = factions
        self.players = players
        self.rounds = rounds
    '''
    def get_faction(self, faction_name: str) -> Optional[Faction]:
        for faction in self.factions:
            if faction.faction_name == faction_name:
                return faction
        return None

    def add_faction(self, faction: Faction):
        self.factions.append(faction)
    '''

    def get_player(self, player_id: int) -> Optional[Player]:
        for player in self.players:
            if player.player_id == player_id:
                return player
        return None

    def get_player_with_seat(self, seat: int) -> Optional[Player]:
        for player in self.players:
            if player.seat == seat:
                return player
        return None

    def add_player(self, player: Player):
        self.players.append(player)
    '''
    
    def get_faction_of_player(self, player_id: int) -> Optional[Faction]:
        for faction in self.factions:
            if player_id in faction.player_ids:
                return faction
        return None
    '''

    def get_living_player_ids(self) -> List[str]:
        game_player_ids = []
        for player in self.players:
            game_player_ids.append(str(player.player_id))
        return game_player_ids

    def add_round(self, a_round: Round):
        self.rounds.append(a_round)

    def get_round(self, round_num: int) -> Optional[Round]:
        for a_round in self.rounds:
            if a_round.round_number == round_num:
                return a_round
        return None

    def get_latest_round(self) -> Optional[Round]:
        latest_round = None
        previous_round_num = 0
        for a_round in self.rounds:
            if a_round.round_number > previous_round_num:
                previous_round_num = a_round.round_number
                latest_round = a_round
        return latest_round


def read_json_to_dom(filepath: str) -> Game:
    with open(filepath, 'r', encoding="utf8") as openfile:
        json_object = json.load(openfile)

        is_active = json_object.get("is_active")
        players = []
        rounds = []
        '''
        if json_object.get("factions") is not None:
            for faction_entry in json_object.get("factions"):
                player_ids = []
                for player_id in faction_entry.get("player_ids"):
                    player_ids.append(player_id)
                faction_name = faction_entry.get("faction_name")
                assets = faction_entry.get("assets")
                factions.append(Faction(player_ids=player_ids,
                                        faction_name=faction_name,
                                        assets=assets))
        '''
        if json_object.get("players") is not None:
            for player_entry in json_object.get("players"):
                player_id = player_entry.get("player_id")
                player_discord_name = player_entry.get("player_discord_name")
                is_dead = player_entry.get("is_dead")
                seat = player_entry.get("seat")
                players.append(Player(player_id=player_id,
                                      player_discord_name=player_discord_name,
                                      is_dead=is_dead,
                                      seat=seat))

        if json_object.get("rounds") is not None:
            for round_entry in json_object.get("rounds"):
                round_num = round_entry.get("round_number")
                round_is_active = round_entry.get("is_active_round")
                nominations = []
                if round_entry.get("nominations") is not None:
                    for nomination_entry in round_entry.get("nominations"):
                        nominator_id = nomination_entry.get("nominator_id")
                        nominated_id = nomination_entry.get("nominated_id")
                        end_time = nomination_entry.get("end_time")
                        votes = []
                        if nomination_entry.get("votes") is not None:
                            for vote_entry in nomination_entry.get("votes"):
                                player_id = vote_entry.get("player_id")
                                is_for = vote_entry.get("is_for")
                                timestamp = vote_entry.get("timestamp")
                                hidden = vote_entry.get("hidden")
                                votes.append(Vote(player_id=player_id,
                                                  is_for=is_for,
                                                  timestamp=timestamp,
                                                  hidden=hidden))
                        nominations.append(Nomination(nominator_id=nominator_id,
                                                      nominated_id=nominated_id,
                                                      votes=votes,
                                                      end_time=end_time))
                rounds.append(Round(round_number=round_num,
                                    is_active_round=round_is_active,
                                    nominations=nominations))

        return Game(is_active, players, rounds)


def write_dom_to_json(game: Game, filepath: str):
    with open(filepath, 'w', encoding="utf8") as outfile:

        #convert Game to dictionary here
        game_dict = {"is_active": game.is_active}
        #faction_dicts = []
        '''
        for faction in game.factions:
            faction_dicts.append({"player_ids": faction.player_ids,
                                  "faction_name": faction.faction_name,
                                  "assets": faction.assets
                                  })
        game_dict["factions"] = faction_dicts
        '''
        player_dicts = []
        for player in game.players:
            player_dicts.append({"player_id": player.player_id,
                                 "player_discord_name": player.player_discord_name,
                                 "is_dead": player.is_dead,
                                 "seat": player.seat
                                 })
        game_dict["players"] = player_dicts
        message_dicts = []
        round_dicts = []
        for a_round in game.rounds:
            nomination_dicts = []
            for nomination in a_round.nominations:
                vote_dicts = []
                for vote in nomination.votes:
                    vote_dicts.append({"player_id": vote.player_id,
                                       "is_for": vote.is_for,
                                       "timestamp": vote.timestamp,
                                       "hidden": vote.hidden})
                nomination_dicts.append({"nominator_id": nomination.nominator_id,
                                         "nominated_id": nomination.nominated_id,
                                         "votes": vote_dicts,
                                         "end_time": nomination.end_time})
            round_dicts.append({"round_number": a_round.round_number,
                                "is_active_round": a_round.is_active_round,
                                "nominations": nomination_dicts})
        game_dict["rounds"] = round_dicts
        json.dump(game_dict, outfile, indent=2, ensure_ascii=False)
