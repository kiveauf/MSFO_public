# -*- coding: utf-8 -*-

# С помощью JSON файла rpg.json задана "карта" подземелья.
# Подземелье было выкопано монстрами и они всё ещё скрываются где-то в его глубинах,
# планируя набеги на близлежащие поселения.
# Само подземелье состоит из двух главных разветвлений и нескольких развилок,
# и лишь один из путей приведёт вас к главному Боссу
# и позволит предотвратить набеги и спасти мирных жителей.

# Напишите игру, в которой пользователь, с помощью консоли,
# сможет:
# 1) исследовать это подземелье:
#   -- передвижение должно осуществляться присваиванием переменной и только в одну сторону
#   -- перемещаясь из одной локации в другую, пользователь теряет время, указанное в конце названия каждой локации
# Так, перейдя в локацию Location_1_tm500 - вам необходимо будет списать со счёта 500 секунд.
# Тег, в названии локации, указывающий на время - 'tm'.
#
# 2) сражаться с монстрами:
#   -- сражение имитируется списанием со счета персонажа N-количества времени и получением N-количества опыта
#   -- опыт и время указаны в названиях монстров (после exp указано значение опыта и после tm указано время)
# Так, если в локации вы обнаружили монстра Mob_exp10_tm20 (или Boss_exp10_tm20)
# необходимо списать со счета 20 секунд и добавить 10 очков опыта.
# Теги указывающие на опыт и время - 'exp' и 'tm'.
# После того, как игра будет готова, сыграйте в неё и наберите 280 очков при положительном остатке времени.

# По мере продвижения вам так же необходимо вести журнал,
# в котором должна содержаться следующая информация:
# -- текущее положение
# -- текущее количество опыта
# -- текущая дата (отсчёт вести с первой локации с помощью datetime)
# После прохождения лабиринта, набора 280 очков опыта и проверки на остаток времени (remaining_time > 0),
# журнал необходимо записать в csv файл (назвать dungeon.csv, названия столбцов взять из field_names).

# Пример лога игры:
# Вы находитесь в Location_0_tm0
# У вас 0 опыта и осталось 1234567890.0987654321 секунд
# Прошло уже 0:00:00
# Внутри вы видите:
# -- Монстра Mob_exp10_tm0
# -- Вход в локацию: Location_1_tm10400000
# -- Вход в локацию: Location_2_tm333000000
# Выберите действие:
# 1.Атаковать монстра
# 2.Перейти в другую локацию
# 3.Выход

import json
import time
from decimal import *

# если изначально не писать число в виде строки - теряется точность!
field_names = ['current_location', 'current_experience', 'current_date']

getcontext().rounding = ROUND_HALF_UP
getcontext().prec = 20


def walk(locations):
    global remaining_time
    global current_location
    global play_time
    
    current_location = list(locations.values())[0]
    time_to_walk = list(locations.keys())[0].rsplit("_")[2]
    number_time = Decimal(time_to_walk[2:len(time_to_walk)])
    remaining_time -= number_time
    play_time += return_time(number_time)
    #return cur_loc # if location -> return as dict

def fight(enemy):
    global experience
    global remaining_time
    global play_time
    
    if isinstance(enemy, str) == True:
        enemy_exp = enemy.split("_")[1]
        exp = int(enemy_exp[3:len(enemy_exp)])
        enemy_time_to_kill = enemy.split("_")[2]
        experience += exp
        number_time = Decimal(enemy_time_to_kill[2:len(enemy_time_to_kill)])
        play_time += return_time(number_time)
        remaining_time -= number_time
    if isinstance(enemy, list) == True:
        for mob in enemy:
            enemy_exp = mob.split("_")[1]
            exp = int(enemy_exp[3:len(enemy_exp)])
            enemy_time_to_kill = mob.split("_")[2]
            experience += exp
            number_time = Decimal(enemy_time_to_kill[2:len(enemy_time_to_kill)])
            play_time += return_time(number_time)
            remaining_time -= number_time

def make_actions(location = list()):
    action_list = list()
    for way in location:
        if isinstance(way, str) == True:
            action_list.append(way.split("_")[0])
        if isinstance(way, list) == True:
            action_list.append(f"Group of {len(way)} mobs")
        if type(way) == dict:
            action_list.append(list(way.keys())[0].rsplit("_",1)[0])
    action_list.append("Quit")
    return action_list

def logger():
    global remaining_time
    global experience
    global play_time
    global start_time

    print("________________________________")
    print()
    print(f"Your exp = {experience}")
    print(f"Remaining time = {remaining_time}")
    print(f"Time spent = {play_time - start_time}")
    print("________________________________")
    print()

def return_time(decimal_time):
    return int(decimal_time.quantize(Decimal('1')))

def take_action(actions = list(), list_of_actions = list()):
    global step

    action = str()
    print("Выберите действие. Ваш ход: ")
    while isinstance(action, int) != True or action > len(list_of_actions): # check if chosen action is from the list
        if __name__ == "__main__":
            action = input()
        if __name__ == "dungeon":
            action = actions[step]
        if action.isdigit() == False or int(action) > len(list_of_actions) or int(action) < 1:
            step += 1
            print("Введите номер из списка доступных действий!")
            continue
        else:
            action = int(action)
        if len(list_of_actions) == 1:
            logger()
            break
    return action

def print_result(l = list()):
    print(f"Вы видите {l}")
    print("Возможные действия:")
    for i in range(len(l)):
        print(f"{i+1}: {l[i]}")

def greeting(dungeon):
    global remaining_time
    global current_location
    print("Welcome to the Dungeon!")
    print("You see the enter of the Dungeon.")
    print("Do you wish to walk in?")
    #action = input("Y/N? \n")
    action = "Y"
    if action == "Y":
        walk(dungeon)
    else:
        current_location = "You pussy"
    return current_location

def play(actions = list()):
    global remaining_time
    global current_location
    global experience
    global list_of_actions
    global step
    global start_time
    global play_time
    global delta_time

    start_time = time.time_ns()
    play_time = time.time_ns()
    delta_time = start_time - play_time
    remaining_time = Decimal(1234567890.0987654321)
    current_location = list()
    experience = 0
    list_of_actions = list()
    step = 0
    action = str()

    with open("rpg.json", mode = "r") as file:
        dungeon = json.load(file)

    current_location = greeting(dungeon) # Start of the run
    if isinstance(current_location, str) == True:
        print(current_location)
        raise ZeroDivisionError("Thanks for the game")

    while remaining_time > 0 and experience < 280:
        if len(current_location) == 0 :
            logger()
            break
        list_of_actions = make_actions(current_location) # make list of actions from the current position
        print_result(list_of_actions)
        action = take_action(actions, list_of_actions)
        print(action)
        if list_of_actions[action - 1] == "Mob" or list_of_actions[action - 1] == "Boss" or list_of_actions[action-1].split()[0] == "Group": # fight if chosen
            print(f"You chose to fight with {list_of_actions[action - 1]}!")
            fight(current_location[action - 1])
            current_location.remove(current_location[action - 1])
        if list_of_actions[action - 1].split("_")[0] == "Location": # go further if chosen
            print(f'You chose move forward to {list_of_actions[action - 1]}!')
            walk(current_location[action - 1])
        if list_of_actions[action - 1] == "Quit":
            print("You've scared, pathetic worm!")
            logger()
            break
        logger()
        step += 1
    
    remaining_time = return_time(remaining_time)
    print("Thanks for the game!")
    print("________________________________")

    return [experience, remaining_time]

if __name__ == "__main__":
    play()

# Учитывая время и опыт, не забывайте о точности вычислений!

