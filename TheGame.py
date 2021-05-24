import telebot
from TrueHatBotGame import TrueHatBotWork
from telebot import types
import itertools



token = ''
bot = telebot.TeleBot(token)

global_admin_dict = {}  # Только для создателей комнаты
global_dict = {}  # Вообще все игроки в текущей сессии
word_count = 10


@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Создать комнату", callback_data="create_room"))
    keyboard.add(types.InlineKeyboardButton(text="Войти в существующую комнату", callback_data="enter_room"))
    try:
        name = message.from_user.first_name + ' ' + message.from_user.last_name
    except TypeError:
        name = message.from_user.first_name
    player = TrueHatBotWork.Player(user_id, name)
    player.register_in_data()
    bot.send_message(message.from_user.id, """Приветствую вас в игре "Шляпа". Правила игры:
        ****Правила игры шляпа*****""", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: 'create_room' in call.data)
def create_room(message):
    user_id = message.from_user.id
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Все в сборе!", callback_data="start_game"))
    keyboard.add(types.InlineKeyboardButton(text="Посмотреть игроков в комнате", callback_data="check_players"))
    try:
        name = message.from_user.first_name + ' ' + message.from_user.last_name
    except TypeError:
        name = message.from_user.first_name
    player = TrueHatBotWork.Player(user_id, name)
    room_id = player.create_room()
    global_admin_dict.update({str(user_id): str(room_id)})
    global_dict.update({str(user_id): str(room_id)})
    bot.edit_message_text(chat_id=message.from_user.id, message_id=message.message.id, text=
    f'Вы создали комнату {room_id}\n'
    f'Подождите пока все игроки зайдут в комнату и начните игру!',
                          reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: 'enter_room' in call.data)
def invite_user_room(message):
    msg = bot.send_message(message.from_user.id, 'Введите номер комнаты: ')
    bot.register_next_step_handler(msg, enter_room)


def enter_room(message):
    user_id = message.from_user.id
    try:
        name = message.from_user.first_name + ' ' + message.from_user.last_name
    except TypeError:
        name = message.from_user.first_name
    player = TrueHatBotWork.Player(user_id, name)
    room_id = message.text
    global_dict.update({str(user_id): str(room_id)})
    bot.send_message(message.from_user.id, player.enter_room(room_id))


@bot.callback_query_handler(func=lambda call: 'check_players' in call.data)
def check_players(message):
    user_id = message.from_user.id
    players = TrueHatBotWork.Room.read_room_players_data(global_admin_dict[str(user_id)])
    bot.send_message(message.from_user.id, players)


@bot.callback_query_handler(func=lambda call: 'start_game' in call.data)
def start(message):
    user_id = message.from_user.id
    player_list = TrueHatBotWork.Game.player_list_for_game(global_admin_dict[str(user_id)])
    bot.delete_message(chat_id=message.from_user.id, message_id=message.message.id)
    for elem in player_list:
        msg = bot.send_message(elem, f'Игра началась! Придумайте {10} слов или используйте /randomize .\n'
                                     f'Слова вводите через пробел. После отправки сообщения дописать '
                                     f'или исправить слова нельзя! '
                                     f'Помните, без полного заполнения {10} слов игра не начнется!\n')
        bot.register_next_step_handler(msg, insert_word_in_game_list)


def insert_word_in_game_list(message):
    words = message.text.split()
    user_id = message.from_user.id
    players = TrueHatBotWork.Room.read_room_data(global_dict[str(user_id)])['room_players']
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Поделиться на команды!", callback_data="prepare_teams"))
    if message.text == '/randomize':
        rand = TrueHatBotWork.Game.rand_word()
        TrueHatBotWork.Game.append_words_in_word_list(rand, global_dict[str(user_id)])
        bot.send_message(message.from_user.id, 'Ваши слова:\n\n' + ' '.join(rand).title())
    elif len(words) >= word_count:
        words = words[0:word_count]
        TrueHatBotWork.Game.append_words_in_word_list(words, global_dict[str(user_id)])
        bot.send_message(message.from_user.id, 'Ваши слова:\n\n' + ' '.join(words).title())
    else:
        bot.send_message(message.from_user.id,
                         'Слов меньше чем нужно! Пересоздай комнату')  # тут нужно предусмотреть возможность дописать
    if len(TrueHatBotWork.Room.read_room_data(global_dict[str(user_id)])['words']) \
            == len(players) * word_count:
        bot.send_message(list(players)[0], 'Игроки готовы к первому раунду! '
                                           'Все слова записаны', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: 'prepare_teams' in call.data)
def prepare_teams(message):
    user_id = message.from_user.id
    player_list = TrueHatBotWork.Game.player_list_for_game(global_admin_dict[str(user_id)])
    for elem in player_list:
        msg = bot.send_message(elem, 'Перед тем как начнется первый раунд, поделитесь на команды.\n'
                                     'Для этого договоритесь кто будет находится в какой команде,'
                                     'придумайте название.\n'
                                     'Введите номер команды, в которой вы будете находится, например: 1')
        bot.register_next_step_handler(msg, prepare_teams_step2)


def prepare_teams_step2(message):
    user_id = message.from_user.id
    # user_name = message.from_user.first_name
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Команды сформированы, начинаем игру!", callback_data="teams_confirm"))
    keyboard.add(types.InlineKeyboardButton(text="Проверить составы команд", callback_data="teams_check"))
    teams = message.text
    players = TrueHatBotWork.Room.read_room_data(global_dict[str(user_id)])['room_players']
    TrueHatBotWork.Game.prepare_teams_for_game(teams, global_dict[str(user_id)], user_id)
    # вот тут должна быть проверка деления
    bot.send_message(list(players)[0], 'Деление на команды завершено!', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: 'teams_check' in call.data)
def team_check(message):
    user_id = message.from_user.id
    bot.send_message(message.from_user.id,
                     'Составы команд:\n' + str(TrueHatBotWork.Game.check_teams(global_admin_dict[str(user_id)])))


@bot.callback_query_handler(func=lambda call: 'teams_confirm' in call.data)
def start_round_one(message):
    user_id = message.from_user.id
    cnt = TrueHatBotWork.Game.get_team_count(global_admin_dict[str(user_id)])
    if not cnt:
        bot.send_message(user_id, 'Не могу начать игру, команд меньше 2х!')
    elif cnt:
        player_list = TrueHatBotWork.Game.player_list_for_game(global_admin_dict[str(user_id)])
        for elem in player_list:
            msg = bot.send_message(elem, 'Начинаем превый раунд!')
            bot.register_next_step_handler(msg, round_one_step_1)


def round_one_step_1(message):
    user_id = message.from_user.id
    game = TrueHatBotWork.Game(global_dict[str(user_id)])
    words = game.words_for_game().copy()
    teams = game.teams_for_class().copy()
    game_steps = itertools.cycle(teams)
    pass


if __name__ == "__main__":
    bot.polling()
