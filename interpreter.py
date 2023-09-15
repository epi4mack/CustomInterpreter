from tkinter import *
from tkinter import scrolledtext
import re
from os import system

system("cls")

rights = []  # Список для хранения правых частей операторов
perems = {}  # Словарь "имя : значение" для хранения переменных

class Part():  # Класс для частей правой части, хранящий в себе значение части, индекс первого её символа и конечный индекс (сразу после последнего символа)
    last_index = -1
    starts = []
    ends = []
    START_PARSE = None
    START_HANDLE = 0
    PEREMS = []
    LAST_PART = None

    def __init__(self, value, start, end):
        Part.last_index += 1
        self.value = value
        self.start = start
        self.end = end
        self.index = Part.last_index  # Порядковый номер части в списке Part.PLIST
        Part.starts.append(self.start)
        Part.ends.append(self.end)

    @staticmethod
    def get_first_index(): return min(Part.starts)

    @staticmethod
    def get_last_index(): return max(Part.ends)

    def __str__(self): return self.value
    def __repr__(self): return self.value
    def __del__(self): Part.last_index -= 1

def set_error(text: str) -> None:  # Вставка текста красного цвета в поле для ошибок
    error_view["state"] = "normal"
    error_view.delete(1.0, END)
    error_view.insert(1.0, text, "tag")
    error_view["state"] = "disabled"


def set_result(text: str) -> None:  # Вставка текста в поле для результата
    result_view["state"] = "normal"
    result_view.delete(1.0, END)
    result_view.insert(1.0, text)
    result_view["state"] = "disabled"

def clean_error_view() -> None:  # Очистка текста в поле для ошибок
    error_view["state"] = "normal"
    error_view.delete(1.0, END)
    error_view["state"] = "disabled"


def clean_result_view() -> None:  # Очистка текста в поле для результата
    result_view["state"] = "normal"
    result_view.delete(1.0, END)
    result_view["state"] = "disabled"


def check_sign_name(name: str) -> bool:  # Проверка названия "Знака"
    if re.fullmatch(r"[а-яА-Я][а-яА-Я\d]*|\d+", name): return True
    return False

def index_shift(raw_text: str,
                single_index: int) -> str:  # Переводит единосимвольный индекс в индекс вида "строка.колонна"
    lst = list(raw_text)
    new = []

    row = 1
    column = 0
    for i, part in enumerate(lst):
        if i < single_index: new.append(part)

    row += new.count("\n")

    for part in new:
        if part == "\n":
            column = 0
        else:
            column += 1

    return f"{row}.{column}"

def generate_search_regex(blocks: list, index: int,
                          end=False):  # Генерирует регулярное выражение для поиска конкретного слова (блока) в исходном тексте
    reg = ""
    for i, block in enumerate(blocks):
        if i <= index:
            reg += f"{block} "
    reg = reg.strip()
    signs = "+-*/().$^|"
    for i in range(len(signs)): reg = reg.replace(signs[i], f"\{signs[i]}")
    if end:
        result = r"[\s\n]*" + r"[\s\n]+".join(reg.split()) + r"[\s\n]*"
        return result
    result = r"[\s\n]*" + r"[\s\n]+".join(reg.split())
    return result

def color_error(raw_text: str, splittted_text: list, index: int, minus=0, plus=0,
                startPlus=0) -> None:  # Помечает неверную инструкцию в редакторе кода красным цветом (используя список)
    length = len(splittted_text[index])  # Длина ошибочной инструкции
    reg = generate_search_regex(splittted_text, index)

    start, end = re.match(reg, raw_text).span();  # end -= 1

    end = end - minus + plus
    start = end - length + startPlus

    code_editor.tag_config("tag", foreground="#c2271b")
    code_editor.tag_add("tag", index_shift(raw_text, start), index_shift(raw_text, end))
    error_view.focus()

def color_error_raw(raw_text: str, index: int, minus=0,
                    plus=0) -> None:  # Помечает неверную инструкцию в редакторе кода красным цветом (используя исходный текст кода)
    code_editor.tag_config("tag", foreground="#c2271b")
    code_editor.tag_add("tag", index_shift(raw_text, index), index_shift(raw_text, index + 1))
    error_view.focus()

def color_error_start_end(raw_text: str, start: int, end: int, plus=0,
                          minus=0) -> None:  # Подсвечивание ошибки имея начальный и конечный индексы слова в исходном тексте
    code_editor.tag_config("tag", foreground="#c2271b")
    start = index_shift(raw_text, start)
    end = end + plus - minus
    end = index_shift(raw_text, end)
    code_editor.tag_add("tag", start, end)
    error_view.focus()


def color_part(raw_text: str, part: Part) -> None:  # Подсвечивает объект класса Part в исходном тексте
    color_error_start_end(raw_text, part.start, part.end)

def get_sign_error(sign: str) -> str:  # Возвращает строку с формулировкой ошибки в написании Знака
    return "Ошибка! Неверный формат Знака."

def interpret() -> None:
    clean_error_view()
    clean_result_view()

    raw = code_editor.get(1.0, END)
    stripped = raw.strip()
    blocks = raw.split()

    if stripped == "":
        set_error("Ошибка! На вход подана пустая программа.")
        code_editor.delete(1.0, END)
        return

    code_editor.tag_config("red", foreground="#c2271b")

    if blocks[0] != "Программа":
        set_error(f'Ошибка! Программа должна начинаться словом "Программа".')
        color_error(raw, blocks, 0)
        return

    if blocks[-1] != "программы":
        set_error(f'Ошибка! Программа должна заканчиваться словами "Конец программы".')
        color_error(raw, blocks, len(blocks) - 1)
        return

    if blocks[-2] != "Конец":
        set_error(f'Ошибка! Программа должна заканчиваться словами "Конец программы".')
        color_error(raw, blocks, len(blocks) - 1)
        return

    if len(blocks) == 3:
        set_error(f'Ошибка! После ключевого слова "Программа" должен идти Заголовок.')
        color_error(raw, blocks, 0)
        return

    if blocks[1] != "Метки":
        set_error(f'Ошибка! Заголовок должен начинаться с ключевого слова "Метки".')
        color_error(raw, blocks, 1)
        return

    if len(blocks) == 4:
        set_error(f'Ошибка! После ключевого слова "Метки" должен идти хотя бы один Знак.')
        color_error(raw, blocks, 1)
        return

    if not check_sign_name(blocks[2]):
        set_error(get_sign_error(blocks[2]))
        color_error(raw, blocks, 2)
        return

    if len(blocks) == 5:
        set_error("Ошибка! Отсутствует блок Операторов.")
        color_error(raw, blocks, 2)
        return

    ###############################################  Обработка цикла Знаков и определение начала цикла Операторов  #############################################################################################
    metka_start = None  # Индекс метки (в случае если двоеточие идёт через пробел)
    oper_start = None  # Индекс слова в массиве blocks, в котором вторым словом встречается ":"
    for i in range(3, len(blocks)):
        if ":" in blocks[i][1:]:
            metka = blocks[i].split(":")[0]
            if not re.fullmatch("\d+", metka):
                set_error("Ошибка! Метка должна являться целым числом.")
                start, end = re.search(f"[\s\n]+{metka}:", raw).span()[0], re.search(f"[\s\n]+{metka}:", raw).span()[1] - 1
                color_error_start_end(raw, start, end)
                return
            oper_start = i
            break
        try:
            blocks[i + 1]
            has_next = True
        except:
            has_next = False
        if has_next:
            if blocks[i + 1][0] == ":":
                metka = blocks[i]
                if not re.fullmatch("\d+", metka):
                    set_error("Ошибка! Метка должна являться целым числом.")
                    color_error(raw, blocks, i)
                    return
                oper_start = i + 1
                metka_start = i
                break
        if not check_sign_name(blocks[i]):
            set_error(get_sign_error(blocks[i]))
            color_error(raw, blocks, i)
            return

    ############################################### ^ Обработка цикла Знаков и определение начала цикла Операторов ^ #############################################################################################

    if not oper_start:
        set_error("Ошибка! Отсутствует блок Операторов.")
        index = len(blocks) - 3
        color_error(raw, blocks, index)
        return

    if not metka_start:
        raw_oper_start = re.search(generate_search_regex(blocks, oper_start - 1, end=True), raw.strip()).span()[1]
    else:
        reg1 = generate_search_regex(blocks, oper_start - 1)
        reg2 = generate_search_regex(blocks, oper_start)
        end1 = int(re.search(reg1, raw).span()[1])
        end2 = int(re.search(reg2, raw).span()[1])
        raw_part = raw[end1:end2]
        colon_count = raw_part.count(":")
        metka_len = end2 - end1 - 4 + len(blocks[oper_start - 1])
        raw_oper_start = re.search(generate_search_regex(blocks, oper_start - 1, end=True), raw.strip()).span()[
                             1] - metka_len + 1 + colon_count - 2  # Индекс первого символа первого оператора в raw

    for i in range(raw_oper_start - 1, len(raw)):  # Для получения индекса первого двоеточия первого оператора
        if raw[i] == ":":
            colon_index = i  # Индекс двоеточия в первом операторе
            break

    startMetka = None
    for i in range(colon_index - 1, -1, -1):
        current = raw[i]
        if current.strip() != "":
            for j in range(i - 1, -1, -1):
                if raw[j].strip() == "":
                    startMetka = j + 1
                    break
            break

    def get_type(part: Part) -> str:  # Возвращает тип переденного символа. Например: "1" -> integer, "a" -> word и т.д.
        value = part.value
        if value == "=": return "equals"
        if re.fullmatch(r"\d+", value): return "integer"
        if re.fullmatch(r"[\=\+\*\&\/\|]+", value): return "oper"
        if value == "(": return "open"
        if value == ")": return "close"
        if value == "!": return "not"
        if value == "-": return "minus"
        if value == ";": return "semi"
        return "perem"

    def get_valid_type(type: str) -> list:  # Возвращает список типов символов, которые могут идти после переданного символа
        if type == "integer": return ["oper", "close", "minus", "semi"]
        if type == "minus": return ["perem", "integer", "open"]
        if type == "not": return ["perem", "integer", "open"]
        if type == "oper": return ["perem", "integer", "open"]
        if type == "open": return ["perem", "integer", "open", "not", "minus"] ###
        if type == "close": return ["oper", "close", "semi", "minus", "not"]
        if type == "perem": return ["oper", "close", "minus", "semi"]
        if type == "equals": return ["perem", "integer", "open", "not", "minus"]
        if type == "semi": return ["perem", "integer", "open", "not", "minus", "oper", "semi", "equals", "close"]

    def get_error(type1: str, type2: str) -> str:  # Возвращает формулировку ошибки в зависимости от типов элементов, которые ошибочно идут друг за другом
        if type1 == "equals" and type2 == "oper": return 'Ошибка! После знака "=" не может идти знак операции.'
        if type1 in ["oper", "minus", "not"] and type2 in ["oper", "minus", "not"]: return 'Ошибка! Не может идти два знака операции подряд.'
        if (type1 == "oper" and type2 == "close"): return 'Ошибка! Перед закрывающейся скобкой не может стоять знак операции.'
        if (type1 == "minus" and type2 == "close"): return 'Ошибка! Перед закрывающейся скобкой не может стоять знак операции.'
        if (type1 == "not" and type2 == "close"): return 'Ошибка! Перед закрывающейся скобкой не может стоять знак операции.'
        if (type1 == "open" and type2 == "oper"): return 'Ошибка! После открывающей скобки не может идти знак операции.'
        if (type1 == "open" and type2 == "close"): return 'Ошибка! После открывающей скобки не может идти закрывающая скобка.'
        if (type1 == "close" and type2 == "open"): return 'Ошибка! После закрывающей скобки не может идти открывающая скобка.'
        if (type1 == "integer" and type2 == "open"): return 'Ошибка! Отсутствует знак операции.'
        if (type1 == "integer" and type2 == "integer"): return 'Ошибка! Отсутствует знак операции.'
        if (type1 == "close" and type2 == "integer"): return 'Ошибка! Отсутствует знак операции.'
        if (type1 == "close" and type2 == "perem"): return 'Ошибка! Отсутствует знак операции.'
        if (type1 == "perem" and type2 == "perem"): return 'Ошибка! Отсутствует знак операции.'
        if (type1 == "oper" and type2 == "semi"): return 'Ошибка! После знака операции должно стоять целое число или переменная.'
        if (type1 == "minus" and type2 == "semi"): return 'Ошибка! После знака операции должно стоять целое число или переменная.'
        if (type1 == "not" and type2 == "semi"): return 'Ошибка! После знака операции должно стоять целое число или переменная.'
        if (type1 == "integer" and type2 == "perem") or (type1 == "perem" and type2 == "integer"): return 'Ошибка! Отсутствует знак операции.'

    def check_for_close(part: Part, right: str) -> any:
        start = part.index + 1

        new = right[start:]
        new = list(map(lambda x: str(x), new))

        if new.count(")") == 0: return "Ошибка! Отсутствует закрывающая скобка."

        seen_open = 0
        for i in range(start, len(right)):
            current = right[i].value
            if i == len(right) - 1:
                if current != ")": return "Ошибка! Отсутствует закрывающая скобка."
                if current == ")":
                    if seen_open != 0:
                        return "Ошибка! Отсутствует закрывающая скобка."
                    else:
                        return None

            if current in "()":
                if current == ")":
                    if seen_open == 0: return None
                    seen_open -= 1
                if current == "(":
                    seen_open += 1
        return None

    def check_for_open(part: Part, right: str) -> any:
        start = part.index - 1

        new = right[:part.index]
        new = list(map(lambda x: str(x), new))

        if new.count("(") == 0: return "Ошибка! Отсутствует открывающая скобка."

        seen_close = 0
        for i in range(start, -1, -1):
            current = right[i].value

            if i == 0:
                if current != "(": return "Ошибка! Отсутствует открывающая скобка."
                if current == "(":
                    if seen_close != 0:
                        return "Ошибка! Отсутствует открывающая скобка."
                    else:
                        return None

            if current in "()":
                if current == "(":
                    if seen_close == 0: return None
                    seen_close -= 1
                if current == ")": seen_close += 1
        return None

    def get_right_part_list(raw_text: str, start: int, end: int) -> dict:
        result = []
        part = ""
        first = None
        last = None
        for i in range(start, end):
            current = raw_text[i]
            if i < end - 1:
                nxt = raw_text[i + 1]
            else:
                nxt = None
            if i > 0:
                prev = raw_text[i - 1]
            else:
                prev = None
            if current.strip() != "":
                if current in ";()+-*/!|&=:":
                    last = i
                    if part.strip() != "": result.append(Part(part, first, last))
                    first = None
                    last = None
                    part = ""
                    result.append(Part(current, i, i + 1))
                elif current == "0" and first is None:
                    if part.strip() != "": result.append(Part(part, first, last))
                    part = ''
                    result.append(Part(current, i, i + 1))
                elif current in ",.":
                    if prev is not None:
                        if re.fullmatch("\d+", prev):
                            if nxt is not None:
                                if re.fullmatch("\d+", nxt):
                                    part += current
                                else:
                                    if part.strip() != "": result.append(Part(part, first, i))
                                    part = ''
                                    result.append(Part(current, i, i + 1))
                                    first = None
                                    last = None
                        else:
                            if part.strip() != "": result.append(Part(part, first, i))
                            part = ''
                            result.append(Part(current, i, i + 1))
                            first = None
                            last = None
                elif re.fullmatch("\d+", current):
                    if first is None: first = i
                    part += current
                else:
                    if first is None: first = i
                    part += current
            else:
                last = i
                if part.strip() != "": result.append(Part(part, first, last))
                first = None
                last = None
                part = ""
        return result

    def check_right(right, add):
        right = get_right_part_list(raw, add, program_end)

        index = 0
        for part in right:
            part.index = index
            index += 1

        oper_end = None
        last_type = "equals"
        for i, part in enumerate(right):
            current = right[i].value
            current_type = get_type(part)

            if len(right) == 1 and current in "-!":
                set_error('Ошибка! После знака операции должно стоять целое число или переменная.')
                color_part(raw, part)
                return "error"

            if current_type == "not" and last_type not in ["equals", "open"]:
                set_error('Ошибка! Знак операции "!" может стоять только после "=" и после открывающей скобки.')
                color_part(raw, part)
                return "error"

            if re.fullmatch("\d+[.,]\d+", current):
                set_error('Ошибка! В правой части только целые числа.')
                color_part(raw, part)
                return "error"

            if re.fullmatch("[\dа-яА-Я]+[.,][\dа-яА-Я]+", current):
                set_error('Ошибка! Некорректная запись переменной.')
                color_part(raw, part)
                return "error"

            if not re.fullmatch("[а-яА-Я\d\+\-\*\/\!\&\|\(\)\;\=]+", current):
                set_error(f'Ошибка! Символ "{current}" не может стоять в правой части.')
                color_part(raw, part)
                return "error"

            if current in "()":
                if current == "(":
                    if check_for_close(part, right):
                        set_error(check_for_close(part, right))
                        color_part(raw, part)
                        return "error"
                    else:
                        if current_type in get_valid_type(last_type):
                            last_type = get_type(part)
                        else:
                            if get_error(last_type, current_type) == "Ошибка! Отсутствует знак операции.":
                                set_error("Ошибка! Отсутствует знак операции.")
                                color_part(raw, right[i - 1])
                                return "error"
                            else:
                                set_error(get_error(last_type, current_type))
                                color_part(raw, part)
                                return "error"
                else:
                    if check_for_open(part, right):
                        set_error(check_for_open(part, right))
                        color_part(raw, part)
                        return "error"
                    else:
                        if current_type in get_valid_type(last_type):
                            last_type = get_type(part)
                        else:
                            if get_error(last_type, current_type) == "Ошибка! Перед закрывающейся скобкой не может стоять знак операции.":
                                set_error("Ошибка! Перед закрывающей скобкой не может стоять знак операции.")
                                color_part(raw, right[i - 1])
                                return "error"
                            if get_error(last_type, current_type) == 'Ошибка! После знака операции должно стоять целое число или переменная.':
                                set_error("Ошибка! После знака операции должно стоять целое число или переменная.")
                                color_part(raw, right[i - 1])
                                return "error"
                            else:
                                set_error(get_error(last_type, current_type))
                                color_part(raw, part)
                                return "error"
            else:
                if not re.fullmatch("[\d\+\-\/\*\=\!\&\|]+", current):

                    if current == ";" and right[i - 1].value in "+-*/&|!":
                        set_error("Ошибка! После знака операции должно стоять целое число или переменная.")
                        color_part(raw, right[i - 1])
                        return "error"

                    if current == ";":
                        oper_end = part.end
                        break

                    if get_error(last_type, current_type) == "Ошибка! Отсутствует знак операции.":
                        set_error("Ошибка! Отсутствует знак операции.")
                        color_part(raw, right[i - 1])
                        return "error"

                    if not re.fullmatch(r"[а-яА-Я][а-яА-Я|\d]*", current):

                        if not re.fullmatch(r"[а-яА-Я]", current[0]):
                            set_error('Ошибка! Переменная должна начинаться с буквы.')
                            color_part(raw, part)
                            return "error"
                        for i in range(1, len(current)):
                            if not re.fullmatch("[\dа-яА-Я]", current[i]):
                                set_error("Ошибка! Некорректная запись Переменной.")
                                color_part(raw, part)
                                return "error"

                    if current not in perems:
                        set_error("Ошибка! Такой переменной нет.")
                        color_part(raw, part)
                        return "error"

                if current == "0" and right[i-1].value == "/":
                    set_error("Ошибка! Деление на ноль.")
                    color_part(raw, part)
                    return "error"

                if get_error(last_type, current_type) == 'Ошибка! После знака "=" не может идти знак операции.':
                    set_error(f'Ошибка! Знак "{current}" не может стоять после знака равно.')
                    color_part(raw, right[i])
                    return "error"

                if get_error(last_type,
                             current_type) == 'Ошибка! После открывающей скобки не может идти знак операции.':
                    set_error(f'Ошибка! Знак "{current}" не может стоять после открывающей скобки.')
                    color_part(raw, right[i])
                    return "error"

                if current in "+-*/!&|" and i == len(right) - 1 and i != 0:
                    set_error("Ошибка! После знака операции должно стоять целое число или переменная.")
                    color_part(raw, part)
                    return "error"

                if i == 0 and current in "!-" and len(right) == 3:
                    set_error('Ошибка! После знака операции должно стоять целое число или переменная.')
                    color_part(raw, right[0])
                    return "error"

                if current == "=":
                    set_error('Ошибка! Знак "=" не может стоять в правой чаcти.')
                    color_part(raw, part)
                    return "error"

                if current_type in get_valid_type(last_type):
                    last_type = get_type(part)
                else:
                    if get_error(last_type, current_type) == "Ошибка! Отсутствует знак операции.":
                        set_error("Ошибка! Отсутствует знак операции.")
                        color_part(raw, right[i - 1])
                        return "error"
                    else:
                        set_error(get_error(last_type, current_type))
                        color_part(raw, part)
                        return "error"

        if right[-1].value == ";":
            set_error('Ошибка! После ";" должен стоять оператор.')
            color_part(raw, right[-1])
            return "error"
        return

    def parse_oper(raw_text: str, start: int, end: int) -> list:
        result = []
        oper = []
        part = ""
        first = None
        last = None

        raw_text = list(raw_text)
        raw_text = raw_text[:end - 1]
        raw_text = "".join(raw_text).strip()

        debug = 0

        for i in range(start, len(raw_text)):
            current = raw_text[i]

            if current.strip() == "":  # Если встречается пустой символ
                if part.strip() != "": oper.append(Part(part, first, i))
                first = None
                last = None
                part = ""

            elif current in ":=+-*/&|!()":  # Если встречается какой-то спец. символ из оператора

                if i == len(raw_text) - 1:  # Если спецсимвол последний в строке
                    if part.strip != "": oper.append(Part(part, first, i))  # !!!
                    oper.append(Part(current, i, i + 1))
                    result.append(oper)
                    return result
                if part.strip() != "": oper.append(Part(part, first, i))
                first = None
                last = None
                part = ""
                oper.append(Part(current, i, i + 1))

            elif current == ";":  # Встречаем точку с запятой (разделят операторы)
                if part.strip() != "": oper.append(Part(part, first, i))
                oper.append(Part(current, i, i + 1))
                result.append(oper)
                oper = []
                first = None
                last = None
                part = ""

            else:  # Встречаем любой другой символ кроме вышеперечисленных
                if i == len(raw_text) - 1:
                    part += current
                    if first is None: first = i
                    oper.append(Part(part, first, i + 1))
                    result.append(oper)
                    return result

                part += current
                if first is None: first = i

        return result

    def oper_handler(rawText, plist):

        if not re.fullmatch("\d+", plist[0].value):
            set_error('Ошибка! Метка должна являться целым числом.')
            color_part(rawText, plist[0])
            return "error"

        if len(plist) == 1:
            set_error('Ошибка! После метки должнен стоять знак ":".')
            color_part(rawText, plist[0])
            return "error"

        if plist[1].value != ":":
            set_error('Ошибка! После метки должен стоять знак ":".')
            color_part(rawText, plist[0])
            return "error"

        if len(plist) == 2:
            set_error('Ошибка! После ":" должна быть переменная.')
            color_part(rawText, plist[1])
            return "error"

        if plist[2].value == ":":
            set_error('Ошибка! После Метки не может идти более одного знака ":" подряд.')
            color_part(rawText, plist[2])
            return "error"

        if plist[2].value == "=":
            set_error('Ошибка! После ":" должна быть переменная.')
            color_part(rawText, plist[1])
            return "error"

        if plist[2].value in "+-*/!|&":
            set_error('Ошибка! После ":" не может идти знак операции.')
            color_part(rawText, plist[2])
            return "error"

        if not re.fullmatch("[а-яА-Я][а-яА-Я\d]*", plist[2].value):
            if not re.fullmatch(r"[а-яА-Я]", plist[2].value[0]):
                set_error('Ошибка! Переменная должна начинаться с буквы.')
                color_part(rawText, plist[2])
                return "error"
            for i in range(1, len(plist[2].value)):
                if not re.fullmatch("[\dа-яА-Я]", plist[2].value[i]):
                    set_error("Ошибка! Некорректная запись Переменной.")
                    color_part(rawText, plist[2])
                    return "error"

        perem = plist[2].value

        if len(plist) == 3:
            set_error('Ошибка! После переменной должен стоять знак "=".')
            color_part(rawText, plist[2])
            return "error"

        if plist[3].value != "=":
            set_error('Ошибка! После Переменной должен идти знак "=".')
            color_part(rawText, plist[2])
            return "error"

        if len(plist) == 4:
            set_error('Ошибка! После "=" должна следовать правая часть.')
            color_part(rawText, plist[3])
            return "error"

        if plist[4].value == ";":
            set_error('Ошибка! После "=" должна следовать правая часть.')
            color_part(rawText, plist[3])
            return "error"

        right = ""
        for i in plist[4:]:
            if ";" in i.value:
                right += f"{i.value} "
                break
            right += f"{i.value} "
        right = right.strip()

        if check_right(right, plist[4].start) == "error": return "error"
        parted_right = get_right_part_list(raw, plist[4].start, program_end)

        def format_right(right: list) -> str:
            right = "".join(right.split())
            right = right.replace("!", " not ").replace("&", " and ").replace("|", " or ").replace(";", "").replace("/", "//")
            return right

        formatted = format_right(right)

        if re.findall("[а-яА-Я][а-яА-Я\d]*", formatted) == []:
            try: perems[perem] = eval(formatted)
            except ZeroDivisionError:
                set_error('Ошибка! Деление на ноль.')
                color_error_start_end(raw, parted_right[0].start, parted_right[-1].end)
                return "error"
        else:
            for per in re.findall("[а-яА-Я][а-яА-Я\d]*", formatted):
                formatted = formatted.replace(per, str(perems[per]))
            try: perems[perem] = eval(formatted)
            except ZeroDivisionError:
                set_error('Ошибка! Деление на ноль.')
                color_error_start_end(raw, parted_right[0].start, parted_right[-1].end)
                return "error"

    program_end = re.search("Конец[\s\n]+программы[\s\n]*$", raw).span()[0]
    opers = parse_oper(raw, startMetka, program_end)

    new = []

    for oper in opers:
        oper = list(filter(lambda x: x.value != "", oper))
        new.append(oper)

    opers = new

    for oper in opers:
        if oper_handler(raw, oper) == "error":
            perems.clear()
            return

    result_string = ''
    for key in perems:
        result_string += f"{key} = {perems[key]}\n"
    set_result(result_string.strip())
    perems.clear()

########################################################################################################################################################################
root = Tk()

root.title("Интерпретатор")
bg_color = "#232323"

root.config(background=bg_color)

WIDTH, HEIGHT = 900, 700

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width / 2) - (WIDTH / 2)
y = (screen_height / 2) - (HEIGHT / 2)
root.geometry(F"{WIDTH}x{HEIGHT}+{int(x)}+{int(y) - 40}")

root.resizable(False, False)

try:
    icon = PhotoImage(file="WindowIcon.png")
    root.iconphoto(False, icon)
except: pass

def on_editor_focus(e=None):
    for tag in code_editor.tag_names(): code_editor.tag_delete(tag)

code_editor = scrolledtext.ScrolledText(root, width=52, height=20, font="Consolas 11", padx=2, pady=2)
code_editor.grid(row=0, column=0, padx=8, pady=10)
code_editor.bind("<FocusIn>", on_editor_focus)

scheme = Text(root, width=54, height=20, font="Consolas 11", padx=2, pady=2)
scheme.insert(1.0,
              'Язык = "Программа" Заголовок Опер ";" ... Опер "Конец программы"\nЗаголовок = "Метки" Знак ... Знак\nЗнак = Перем ! Цел\nОпер = Метка ":"'
              ' Перем "=" Прав. часть\nПрав. часть = </"-"/> Блок1 зн1 ... Блок1\nзн1 = "+" ! "-"\nБлок1 = Блок2 зн2 ... Блок2\nзн2 = "*" ! "/"\n'
              'Блок2 = Блок3 зн3 ... Блок3\nзн3 = "&" ! "|"\nБлок3 = </"!"/>Блок4\nБлок4 = Перем! Цел!"(" Прав. часть ")"\nМетка = Цел\nЦел = Цифра ... Цифра\n'
              'Перем = Буква </Символ ... Символ/>\nСимвол = Буква ! Цифра\nБуква = "А" ! "Б" ! ... ! "Я"\nЦифра = "0" ! "1" ! ... ! "9"')

code_editor.insert(1.0, "Программа\n\nМетки знак1 знак2 знак3\n\n1:а=14*(3+9+(4+1));\n2:б=а*2-4;\n3:в=б+а*(а/2)\n\nКонец программы")

scheme.config(state="disabled", cursor="")
scheme.grid(row=0, column=1, pady=10)

error_label = Label(root, text="Ошибки", font=("Default", 16), bg=bg_color, fg="White")
error_label.place(x=5, y=385)

error_view = Text(root, width=97, height=1, padx=3, pady=2, font="Calibri 13", state="disabled", cursor="")
error_view.place(x=10, y=420)
error_view.tag_config("tag", foreground="#c2271b")

result_label = Label(root, text="Результат", font=("Default", 16), bg=bg_color, fg="White")
result_label.place(x=5, y=455)

result_view = scrolledtext.ScrolledText(root, width=95, height=7, padx=2, pady=2, font="Calibri 13", state="normal",
                                        cursor="")
result_view.place(x=10, y=490)
result_view["state"] = "disabled"

run = Button(root, text="Запустить", font="Calibri 13", command=interpret)
run.place(x=395, y=658)

code_editor.focus()
########################################################################################################################################################################

if __name__ == "__main__": root.mainloop()