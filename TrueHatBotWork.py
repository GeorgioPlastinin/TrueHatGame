import random
import shelve
import time
import itertools

class Player:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.player = {f'{self.id}': f'{self.name}'}

    def get_player_id(self):
        return self.id

    def get_player_name(self):
        return self.name

    def register_in_data(self):
        with shelve.open('./data/user_data', writeback=True) as file:
            file['players'].update(self.player)

    def create_room(self):
        room = Room()
        self.enter_room(room.get_room_id())
        return room.get_room_id()

    def enter_room(self, room_id):
        room_id = int(room_id)
        with shelve.open('./data/data', writeback=True) as file:
            try:
                file[str(room_id)]['room_players'].update(self.player)
                return f'Вы вошли в комнату #{room_id}'
            except KeyError:
                return 'Данной комнаты не существует!'

    def exit_room(self, room_id):
        with shelve.open('./data/data', writeback=True) as file:
            del file[str(room_id)]['room_players'][str(self.id)]


class Room:

    def __init__(self):
        self.room_id = random.randrange(1000, 10000)
        with shelve.open('./data/data', writeback=True) as file:
            file[str(self.room_id)] = {'words': [], 'room_players': {}, 'teams': []}

    def get_room_id(self):
        return self.room_id

    @staticmethod
    def del_room_as_ending(room_id):  # удаляет комнату по завершению игры
        with shelve.open('./data/data', writeback=True) as file:
            del file[str(room_id)]

    @staticmethod
    def read_room_data(room_id):
        with shelve.open('./data/data') as file:
            data = file[str(room_id)]
            return dict(data)

    @staticmethod
    def read_room_players_data(room_id):
        players_list = []
        with shelve.open('./data/data') as file:
            data = file[str(room_id)]['room_players']
        for elem in data:
            players_list.append(data[elem])
        return ', '.join(players_list)

    def change_room_settings(self):
        pass


class Game:

    def __init__(self, room_id):
        self.room_id = room_id

    def teams_for_class(self):
        with shelve.open('./data/data') as file:
            data = file[str(self.room_id)]['teams']
            setattr(self, 'teams', data)
        return data

    def words_for_game(self):
        with shelve.open('./data/data') as file:
            data = file[str(self.room_id)]['words']
            setattr(self, 'words', data)
        return data

    @staticmethod
    def timer(second):
        while second != 0:
            second -= 1
            time.sleep(1)

    @staticmethod
    def rand_word():
        word_list = []
        while len(word_list) < 10:
            word_file = (random.choice(list(open('word_rus.txt', encoding='UTF-8'))))
            word_list.append(str(word_file).rstrip('\n'))
        return word_list

    @staticmethod
    def append_words_in_word_list(words, room_id):
        with shelve.open('./data/data', writeback=True) as file:
            for elem in words:
                file[str(room_id)]['words'].append(elem)

    @staticmethod
    def player_list_for_game(room_id):
        player_list = []
        player_obj = Room.read_room_data(room_id)
        for elem in player_obj['room_players']:
            player_list.append(elem)
        return player_list

    @staticmethod
    def check_team_num(team, room_id):
        with shelve.open('./data/data', writeback=True) as file:
            data = file[str(room_id)]['teams']
            for elem in data:
                if str(team) in elem:
                    return True
                else:
                    continue
            return False

    @staticmethod
    def prepare_teams_for_game(team, room_id, player_id):
        with shelve.open('./data/data', writeback=True) as file:
            data = file[str(room_id)]['teams']
            if len(data) == 0:
                data.append({str(team): [player_id]})
            elif len(data) > 0:
                have_num = Game.check_team_num(team, room_id)
                if have_num:
                    for elem in data:
                        if str(team) in elem:
                            idx = data.index(elem)
                    data[idx][str(team)].append(player_id)
                elif not have_num:
                    data.append({str(team): [player_id]})

    @staticmethod
    def get_players_name(room_id, name_ids):
        players_name_list = []
        with shelve.open('./data/data') as file:
            players_data = file[str(room_id)]['room_players']
            for elem in name_ids:
                players_name_list.append(players_data[str(elem)])
            return players_name_list

    @staticmethod
    def check_teams(room_id):
        team_list = []
        with shelve.open('./data/data') as file:
            data = file[str(room_id)]['teams']
            for elem in data:
                team_num = ''.join(list(elem.keys()))
                team_person = ', '.join(Game.get_players_name(room_id, list(elem.values())[0]))
                team_list.append(f'Команда №{team_num} - {team_person}')
            return '\n'.join(team_list)

    @staticmethod
    def get_team_count(room_id):
        with shelve.open('./data/data') as file:
            data = file[str(room_id)]['teams']
            if len(data) < 2:
                return False
            else:
                return True

    def start_round_one(self):
        pass

    def start_round_two(self):
        pass

    def start_round_three(self):
        pass

    def scores(self):
        pass
