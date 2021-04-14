import shelve
from collections import Counter
from collections import namedtuple


with shelve.open('./data/data', writeback=True) as file:  # врайтбек на перезапись
    data = file.items()
    print(dict(data)['3359']['teams'])
    # teams = list(dict(data)['2119']['teams'].values())
    # print(teams)
    # for elem in teams:
    #     print(elem['team_name'])
    #     print(list(elem['players'].values()))

"""

Первый словесный раунд. (обязательно удаление слов в чате, после нажатия кнопки "Угадал!"
"""

