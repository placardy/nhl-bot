import requests
import telebot
from telebot import types # Для создания кнопок
import json


token='6463259053:AAGBXM7DegIjwCN2uakmWTpVm7fGNSrRoS8'          #обращаемсся к нашему конкретному боту

bot = telebot.TeleBot(token) #бот - это бот в тг с токеном конкретным

@bot.message_handler(commands=['start'])    #когда боту отправляется /start
def start_message(message):
  bot.send_message(message.chat.id,"Привет ✌️ ")
  # Отправка клавиатуры с двумя параметрами, автоматическая высота кнопки, второй - кнопка появляется один раз
  keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
  # Создание самой кнопки через запятую
  keyboard.add(types.KeyboardButton('Команды NHL'), types.KeyboardButton('Вопрос'))
  # Вторая строка клавиатуры
  keyboard.add(types.KeyboardButton('Player search'))
  bot.send_message(message.chat.id, f"Привет {message.from_user.first_name}!", reply_markup=keyboard)

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
          row.append(telebot.types.InlineKeyboardButton(team_name, callback_data=team_id))
        inline_keyboard.row(*row)
        # teams_string += f"ID: {team_id} |  Name: {team_name}\n"
      # bot.send_message(message.chat.id, teams_string)

      bot.send_message(message.chat.id, 'TEAMS:', reply_markup=inline_keyboard)


  # elif message.text == "Вопрос":
  #     inlineKeyboard = types.InlineKeyboardMarkup()
  #     inlineKeyboard.add(types.InlineKeyboardButton('2', callback_data='первая'))
  #     inlineKeyboard.add(types.InlineKeyboardButton('4', callback_data='вторая'))
  #     inlineKeyboard.add(types.InlineKeyboardButton('6', callback_data='третья'))
  #     bot.send_message(message.chat.id, '2+2', reply_markup=inlineKeyboard)

  elif message.text == 'Player search':
    bot.reply_to(message, 'Введите текст')
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


# Обработка нажатия на кнопку
@bot.callback_query_handler(func=lambda call: True) # Анонимная функция(лямбда функция), если этот параметр пустой то возвращаем ТРУ 
def touch_button(call): # Тот же параметр как и в декораторе
  team_id = call.data
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
      # string = string + f"{name} | id: {id} \n"
          row.append(telebot.types.InlineKeyboardButton(name, callback_data=player_id))
        inline_keyboard.row(*row)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text = 'Roster:', reply_markup=inline_keyboard)
    #bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text = f'Roster:\n {string}')
  else:
    bot.send_message(call.message.chat.id, 'Информация о составе команды недоступна.')
  # Чтобы избавиться от часиков
  bot.answer_callback_query(call.id)

bot.polling(none_stop = True)