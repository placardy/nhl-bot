import requests
import telebot
from telebot import types
import json
from config import TOKEN


token = TOKEN         #обращаемсся к нашему конкретному боту
bot = telebot.TeleBot(token) #бот - это бот в тг с токеном конкретным


@bot.message_handler(commands=['start'])    #когда боту отправляется /start
def start_message(message):
  # Отправка клавиатуры с двумя параметрами, автоматическая высота кнопки, второй - кнопка появляется один раз
  keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
  # Создание самой кнопки через запятую
  keyboard.add(types.KeyboardButton('Команды NHL'), types.KeyboardButton('Random GIF'))
  # Вторая строка клавиатуры
  keyboard.add(types.KeyboardButton('Player search'))
  bot.send_message(message.chat.id, f"Welcome! {message.from_user.first_name}!", reply_markup=keyboard)


@bot.message_handler(content_types=['text'])      
def new_message(message):            #функция реагируют но новое собощение, не на стартовое
  if message.text == "Команды NHL":
      url = "https://statsapi.web.nhl.com/api/v1/teams"
      # Отправка запроса к NHL API
      response = requests.get(url)
      data = response.json()
      # Получение списка команд из ответа
      teams = data['teams']
      #Создание словаря {'id': 'name'} из данных, которые достали по API
      global dict
      teams_dict = dict()
      for team in teams:
        team_id = team['id']
        team_name = team['name']
        teams_dict[team_id] = team_name
      # Создание сообщения с идентификаторами и названиями команд
      teams_string = "Список команд NHL:\n"
      inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
      # Создание двух столбцов кнопок
      for i in range(0, len(teams), 2):
        row = []
        for team in teams[i: i+2]:
          team_id = team['id']
          team_name = team['name']
        # inlineKeyboard.add(types.InlineKeyboardButton(f'{team_name} |ID: {team_id}|  ', callback_data=f'{team_id}'))
          row.append(telebot.types.InlineKeyboardButton(team_name, callback_data=f'team_{team_id}'))
        inline_keyboard.row(*row)
        # teams_string += f"ID: {team_id} |  Name: {team_name}\n"
      # bot.send_message(message.chat.id, teams_string)
      bot.send_message(message.chat.id, 'TEAMS:', reply_markup=inline_keyboard)
  elif message.text == 'Player search':
    bot.reply_to(message, "Print the player's name")
    @bot.message_handler(content_types=['text'])  #Создаём новую функцию ,реагирующую на любое сообщение
    def message_input_step(message):
      name = message.text
      url = f'https://suggest.svc.nhl.com/svc/suggest/v1/minplayers/{name}/10'
      response = requests.get(url)
      data = response.json()
      players_info = data['suggestions']
      inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
      for i in range(0, len(players_info), 2):
        row = []
        for player in players_info[i: i+2]:
          player_list = player.split('|')
          player_id = player_list[0]
          player_name = player_list[2] + ' ' + player_list[1]
          row.append(telebot.types.InlineKeyboardButton(player_name, callback_data=f'player_{player_id}'))
        inline_keyboard.row(*row)
      bot.send_message(message.chat.id, text=f"Your text: {name}", reply_markup=inline_keyboard)
    bot.register_next_step_handler(message, message_input_step)
  elif message.text == 'Random GIF':
    url = 'http://api.giphy.com/v1/gifs/random?api_key=bEMogaKjVOcfQBnXkn3n202pgIrotHsv&tag=nhl+goal&rating=g'
    response = requests.get(url)
    data = response.json()
    print(data['data']['images']['original']['url'], '!!!!!!!!!!!!')
    if response.status_code == 200:
      gif_link = data['data']['images']['original']['url']
    bot.send_animation(message.chat.id, gif_link)


# Обработка нажатия на кнопку
@bot.callback_query_handler(func=lambda call: True) # Анонимная функция(лямбда функция), если этот параметр пустой то возвращаем ТРУ 
def handle_team_click(call): # Тот же параметр как и в декораторе
    if call.data.startswith('team_'):
        team_id = call.data.split('_')[1]
        url = f'https://statsapi.web.nhl.com/api/v1/teams/{team_id}/roster'
        # edit massage или delete message
        response = requests.get(url)
        if response.status_code == 200:
            roster_data = response.json()
            roster = roster_data['roster']
            inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
            for i in range(0, len(roster), 2):
                row = []
                for player in roster[i: i + 2]:
                    player_id = player['person']['id']
                    name = player['person']['fullName']
                    row.append(telebot.types.InlineKeyboardButton(name, callback_data=f'player_{player_id}'))
                inline_keyboard.row(*row)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text = 'Roster:', reply_markup=inline_keyboard)
        bot.answer_callback_query(call.id)
    elif call.data.startswith('player_'):
        player_id = call.data.split('_')[1]
        print(player_id)
        player_data = requests.get(f'https://statsapi.web.nhl.com/api/v1/people/{player_id}').json()
        string_info = ''
        player_data = player_data['people'][0]
        print(player_data)
        for key, value in player_data.items():
            string_info = f'{string_info} + {key}: {value}\n'
            string_info = f"*Name:* {player_data['fullName']}\n*Birthday:* {player_data['birthDate']}\
              \n*Birthday City:* {player_data['birthCity']}\n*Country:* {player_data['birthCountry']}\
              \n*Team:* {player_data['currentTeam']['name']}\
              \n*Position* {player_data['primaryPosition']['name']}, type: {player_data['primaryPosition']['type']}"
        bot.edit_message_text(chat_id=call.message.chat.id,  message_id=call.message.id, text=string_info, parse_mode="Markdown")
        bot.answer_callback_query(call.id)


if __name__ == '__main__':
  bot.polling(none_stop = True)