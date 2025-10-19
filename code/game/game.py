from code.game.game_api import GameAPI

def level_1(game: GameAPI) -> None | str:
    player = game.get_player()
    actors = game.get_actors()

    player_actor = player["actor"]
    author_actor = actors["author"]
    unknown_actor = actors["unknown"]
    clock_actor = actors["clock"]
    aleksandr_actor = actors["aleksandr"]
    bus_actor = actors["bus"]
    controller_actor = actors["controller"]
    security_actor = actors["security"]

    game.talk(author_actor, "Уровень 1 (Пролог)")
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
        game.talk(author_actor, "Видимо вы хотите пойти в магазин после зачёта.")
        game.talk(author_actor, "Но может стоило взять 'Тройку'?")

    player["intelligence"] = 0
    wardrobe = ("Костюм", "Спортивыная футболка и шорты", "Повседневная одежда")
    while True:

        match game.select("Что одеть?", wardrobe):
            case 0:
                if sleep_more:
                    game.talk(author_actor, "Вы панически оглядываетесь. Костюм? В таком состоянии его не найти!")
                    continue
                player["intelligence"] += 10
                game.talk(author_actor, "Вы натягиваете костюм, чувствуя, как уверенность наполняет вас.")
                game.talk(author_actor, "+10 к интеллект")
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
        game.talk(controller_actor, "Предъявите ваш билет.")
        game.think(player_actor, "***")
        return "А вот надо было оплачивать проезд."

    game.look("pre_hall")
    game.talk(author_actor, "Вы выходите на остановке и подходите к посту охраны.")
    if player["intelligence"] < 0:
        game.talk(author_actor, "Вы пытаетесь войти, но вас останавливает охранник.")
        game.talk(security_actor, "Вы нарушаете форму одежды.")
        game.talk(security_actor, "Это не офисный стиль, так ещё и в шортах!")
        game.talk(player_actor, "Но мне очень надо пройти. У меня сегодня зачёт!")
        game.talk(security_actor, "Н-Е-Т-!")
        return "Что-то явно пошло не так."


    game.talk(author_actor, "Вы смотрите на часы и понимаете, что пара началась 5 минут назад.")
    game.talk(author_actor, "Сжав кулаки, вы бежите в аудиторию...")
    return


def level_2(game: GameAPI) -> None | str:
    player = game.player
    actors = game.get_actors()

    player_actor = player["actor"]
    author_actor = actors["author"]
    ss_teacher_actor = actors["social studies teacher"]

    game.look("class_1")
    game.talk(author_actor, "Уровень 2 (пара обществознания)")
    game.talk(author_actor, "Вы добрались до аудитории, остановившись около прикрытой двери.")

    player["reputation"] = 0
    variants = (
        "Зайти не постучавшись.",
        "Постучаться."
    )
    match game.select("Ваши действия:", variants): 
        case 0:
            game.talk(author_actor, "Вы как ни в чём не бывало заходите в аудиторию.")
            game.talk(author_actor, "Преподаватель явно был не очень рад вашей авантюре.")
            game.talk(ss_teacher_actor, "Выйдите и зайдите нормально.")
            game.talk(author_actor, "Вы развернулись и вышли из аудитории всё-таки постучав в дверь.")
            game.talk(ss_teacher_actor, "Войдите.")
            player["reputation"] -= 10
            game.talk(author_actor, "-10 к репутации")
        case 1:
            game.talk(author_actor, "Вы постучались и вам разрешили войти.")
        case _ :
            game.talk(author_actor, "")
            return
        
    game.talk(author_actor, "Вы вошли, и уже хотели сесть за парту, но вас вопросительно окликнул преподаватель.")
    game.talk(ss_teacher_actor, "Молодой человек а вы собственно говоря кто?")
    game.think(player_actor, "Ваш студент, пришёл на зачёт")
    game.talk(ss_teacher_actor, "Любопытно, я вас впервые вижу за год.")
    game.talk(ss_teacher_actor, "А где пропадали если не секрет?")
    
    variants = (
        "Сказать правду.",
        "Попытаться схитрить."
    )
    match game.select("Ваши действия:", variants):
        case 0 :
            game.think(player_actor, "Не буду скрывать, я прогуливал.")
            game.talk(ss_teacher_actor, "Достаточно опрометчиво с вашей стороны, но я ценю честность.")
            player["reputation"] += 10
            game.talk(author_actor, "+10 к репутации")
        case 1 :
            game.think(player_actor, "У меня развилась острая аллергия на гранит науки.")
            game.think(player_actor, "При приближении к учебному заведению у меня начинается чихание, кашель и появляется сыпь в виде лекций.")
            game.talk(ss_teacher_actor, "Могли что то и пооригинальнее придумать.")
            game.talk(ss_teacher_actor, "Недолюбливаю хитропопых студентов.")
            player["reputation"] -= 10
            game.talk(author_actor, "-10 к репутации")
            return
 
    if player["reputation"] < 0:
        game.talk(ss_teacher_actor, "Могу облегчить вам задачу в какой то степени.")
        game.talk(ss_teacher_actor, "Согласны сыграть в подбрасывание монетки?")
        game.talk(ss_teacher_actor, "Угадаете сторону монетки поставлю оценку автоматом за год")
        game.talk(ss_teacher_actor, "А если нет, пойдёте с миром Родине служить")

        variants = (
        "Согласиться.",
        "Отказаться."
    )
        match game.select("Ваши действия:", variants):
            case 0 :
                game.think(player_actor, "Я не против, мне всё равно нечего терять.")
                game.talk(ss_teacher_actor, "Итак начнём. Орёл или решка?")

                variants = (
        "Выбрать орёл.",
        "Выбрать решку."
    )
                match game.select("Ваши действия:", variants):
                    case 0 :
                        game.think(player_actor, "Я выбираю орёл.")
                        game.talk(author_actor, "Преподаватель подбрасывает монетку и ловким движением рук ловит монетку.")
                        game.talk(author_actor, "Монетка предательски была повернута противоположной стороной то есть решкой.")
                        game.talk(ss_teacher_actor, "Какая досада молодой человек, повезёт в следующий раз.")
                        return "Здравствуй небо в облаках, здравствуй юность в сапогах..."
                    case 1 :
                        game.think(player_actor, "Я выбираю решку.")
                        game.talk(author_actor, "Преподаватель подбрасывает монетку и ловким движением рук ловит монетку.")
                        game.talk(author_actor, "Монетка предательски была повернута противоположной стороной то есть орлом.")
                        game.talk(ss_teacher_actor, "Какая досада молодой человек, повезёт в следующий раз.")
                        return "Здравствуй небо в облаках, здравствуй юность в сапогах..."
            case 1 :
                game.talk(player_actor, "Простите, но я не азартный игрок, поэтому откажусь.")
                game.talk(ss_teacher_actor, "Желание студента для меня закон.")
                return
    if player["intelligence"] > 0:
        game.talk(author_actor, "Преподаватель оглядел вас с ног до головы и сказал:")
        game.talk(ss_teacher_actor, "Тогда тяни билет красавец.")
        game.talk(author_actor, "Вы долго раздумывали какой билет вытянуть и взяли первый какой попался под руку.")
        game.talk(author_actor, "Вам попался счастливый билет.")
        game.talk(author_actor, "Удача ли это или что то другое?")
        game.think(player_actor, "У меня счастливый билет!")
        game.talk(ss_teacher_actor, "Вот ж блин, везучий попался.")
        game.talk(ss_teacher_actor, "Давай зачётку, везунчик.")
        game.talk(author_actor, "Вы протягиваете зачётку")
        game.talk(author_actor, "Преподаватель ставит в зачётку пять.")
        return
    
    game.talk(ss_teacher_actor, "Тогда тяните билет.")
    game.talk(author_actor, "Вы тяните билет и садитесь за парту готовиться.")
    game.talk(author_actor, "Как только подготовились вы садитесь возле преподавателя рядом.")
    game.talk(author_actor, "Вы с большим трудом отвечаете на вопросы.")
    game.talk(author_actor, "Преподаватель буквально вытягивает вас на оценку три.")
    game.talk(ss_teacher_actor, "Согласны на оценку три?")

    variants = (
        "Согласиться.",
        "Отказаться."
    )
    match game.select("Ваши действия:", variants):
            case 0 :
                game.think(player_actor, "Да")
                game.talk(author_actor, "Преподаватель вам ставит три в зачётку.")
                game.talk(ss_teacher_actor, "Свободен")
                game.talk(author_actor, "Вы выходите из аудитории, довольный результатом.")
                return
            case 1 :
                game.think(player_actor, "Нет уж, я ответил на более высокую оценку.")
                game.talk(author_actor, "Преподаватель хихикнул и сказал:")
                game.talk(ss_teacher_actor, "Молодой человек, вы даже на три толком не ответили.")
                game.think(player_actor, "Я ответил.")
                game.talk(author_actor, "Преподаватель задал наипростейший вопрос, на который вы не ответили.")
                game.talk(ss_teacher_actor, "Что и требовалось доказать, я вам передумал даже три ставить.")
                game.think(player_actor, "Стойте стойте, ставьте три ладно.")
                game.talk(ss_teacher_actor, "Нет уж голубчик, не заслужили.")
                game.talk(author_actor, "Преподаватель ставит два в зачётку.")
                game.talk(author_actor, "Вы выходите из аудитории недовольным и напраляетесь домой.")
                return "Иногда не стоит наглеть."
    return