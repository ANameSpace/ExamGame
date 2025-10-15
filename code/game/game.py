from code.game.game_api import GameAPI

def level_0(game: GameAPI) -> None | str:
    player = game.get_player()
    actors = game.get_actors()

    # Действующие лица уровня. Предворительно добавь их в game_data.py
    player_actor = player["actor"]
    author_actor = actors["author"]
    unknown_actor = actors["unknown"]
    clock_actor = actors["clock"]
    aleksandr_actor = actors["aleksandr"]
    bus_actor = actors["bus"]
    controller_actor = actors["controller"]
    security_actor = actors["security"]

    game.do(clock_actor, "звонит")
    game.think(player_actor, "Какой жуткий звук! Зачем я поставил будильник на такое раннее время?")
    variants = (
        "Поспать ещё пару минут.",
        "Встать сразу."
    )
    sleep_more = False
    match game.select("Может поспать ещё?", variants):
        case 0:
            game.talk(author_actor, "Вы устало переворачиваетесь на бок, в надежде вновь окунуться в сладкие объятия сна...")
            game.do(unknown_actor, "звук уведомления")
            game.phone(aleksandr_actor, "Эй, ты где? Не забыл про зачёты?")
            game.phone(player_actor, "Что? Нет-нет, я помню! Просто... сейчас... ещё сплю!")
            game.phone(aleksandr_actor, "Нам сегодня к первой паре...")
            game.talk(author_actor, "Вы мгновенно вскакиваете с кровати.")
            sleep_more = True
        case 1:
            game.talk(author_actor, "Вы медленно встаете, борясь с чувством тяжести в веках...")
        case _:
            game.talk(author_actor, "У ТЕБЯ ОШИБКА В КОДЕ ИГРЫ!")
            return

    game.look("room")

    game.think(player_actor, "Нужно собрать рюкзак и скорее выходить.")
    items = ("Тройка (карта)", "Скидочная карта", "Купон на скидку в магазине мебели")
    if game.select("Что взять (только 1)?", items) == 0:
        player["inventory"].append("Тройка (карта)")
        game.talk(author_actor,"Вы берёте в руки 'Тройку' и кладёте её в карман.")
    else:
        game.talk(author_actor, "Видимо вы хотите пойти в магазин после зачёта. Но может стоило взять 'Тройку'?")

    player["intelligence"] = 0
    wardrobe = ("Костюм (+10 интеллекта)", "Спортивыная футболка и шорты", "Повседневная одежда")
    while True:

        match game.select("Что одеть?", wardrobe):
            case 0:
                if sleep_more:
                    game.talk(author_actor, "Вы панически оглядываетесь. Костюм? В таком состоянии его не найти!")
                    continue
                player["intelligence"] += 10
                game.talk(author_actor, "Вы натягиваете костюм, чувствуя, как уверенность наполняет вас.")
                break
            case 1:
                player["intelligence"] -= 10
                break
            case _:
                break

    game.talk(author_actor, "Вы выбегаете из дома и вскоре садитесь в автобус. Свежий воздух бодрит!")
    game.look("bus")

    ticket = False
    if game.select("Оплатить проезд?", ("Да", "Мне повезёт!")) == 0:
        if "Тройка (карта)" in player["inventory"]:
            ticket = True
        else:
            game.talk(author_actor, "Внезапно вы осознаете, что забыли 'Тройку' дома. Как же так?!")
            game.talk(author_actor, "Вы хотели оплатить проезд, но вспомнили, что без карты это невозможно...")

    game.do(bus_actor, "начинает движение")

    if not ticket:
        game.do(bus_actor, "останавливается на остановке")
        game.do(controller_actor, "заходит")
        game.think(player_actor, "Нужно спрятаться. Просто нужно исчезнуть.")
        game.talk(controller_actor, "Здравствуйте, молодой человек.")
        game.talk(controller_actor, "Предъявите ваш билет")
        game.think(player_actor, "***")
        return "А вот надо было оплачивать проезд."

    game.look("pre_hall")
    game.talk(author_actor, "Вы выходите на остановке и подходите к посту охраны.")
    if player["intelligence"] < 0:
        game.talk(author_actor, "Вы пытаетесь войти, но вас останавливает охранник.")
        game.talk(security_actor, "Вы нарушает форму одежды. Это не офисный стиль, так ещё и в шортах!")
        game.talk(player_actor, "Но мне очень надо пройти. У меня сегодня зачёт!")
        game.talk(security_actor, "Н-Е-Т-!")
        return "Что-то явно пошло не так."


    game.talk(author_actor, "Вы смотрите на часы и понимаете, что пара началась 5 минут назад.")
    game.talk(author_actor, "Сжав кулаки, вы бежите в аудиторию...")
    return


def level_1(game: GameAPI) -> None | str:
    player = game.get_player()
    actors = game.get_actors()

    player_actor = player["actor"]
    author_actor = actors["author"]

    game.look("class_1")
    game.talk(author_actor, "Начало уровня 1 (пара обществознания)")

    return

# Для добавления новых уровней добавь def level_НОМЕР(game: GameAPI) -> None | str: и впиши это в game_data.pt (load_levels())