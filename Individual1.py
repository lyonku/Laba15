#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   Выполнить индивидуальное задание 2 лабораторной работы 14, добавив аннтотации типов.
#   Выполнить проверку программы с помощью утилиты mypy.

from dataclasses import dataclass, field
import logging
import sys
from typing import List
import xml.etree.ElementTree as ET


# Класс пользовательского исключения в случае, если время введено
# не в правильном формате
class IllegalTimeError(Exception):

    def __init__(self, time, message="Illegal time (HH:MM)"):
        self.time = time
        self.message = message
        super(IllegalTimeError, self).__init__(message)

    def __str__(self):
        return f"{self.time} -> {self.message}"


# Класс пользовательского исключения в случае, если введенная
# команда является недопустимой.
class UnknownCommandError(Exception):

    def __init__(self, command, message="Unknown command"):
        self.command = command
        self.message = message
        super(UnknownCommandError, self).__init__(message)

    def __str__(self):
        return f"{self.command} -> {self.message}"


@dataclass(frozen=True)
class train:
    name: str
    num: str
    time: str


@dataclass
class Staff:
    trains: List[train] = field(default_factory=lambda: [])

    def add(self, name: str, num: str, time: str) -> None:

        if ":" not in time:
            raise IllegalTimeError(time)

        self.trains.append(
            train(
                name=name,
                num=num,
                time=time
            )
        )

        self.trains.sort(key=lambda train: train.name)

    def __str__(self) -> str:
        # Заголовок таблицы.
        table = []
        line = '+-{}-+-{}-+-{}-+-{}-+'.format(
            '-' * 4,
            '-' * 30,
            '-' * 20,
            '-' * 17
        )
        table.append(line)
        table.append(
            '| {:^4} | {:^30} | {:^20} | {:^17} |'.format(
                "№",
                "Пункт назначения",
                "Номер поезда",
                "Время отправления"
            )
        )
        table.append(line)

        # Вывести данные о всех поездах.
        for idx, train in enumerate(self.trains, 1):
            table.append(
                '| {:>4} | {:<30} | {:<20} | {:>17} |'.format(
                    idx,
                    train.name,
                    train.num,
                    train.time
                )
            )

        table.append(line)

        return '\n'.join(table)

    def select(self):

        parts = command.split(' ', maxsplit=2)

        numbers = int(parts[1])

        c = 0

        for trainn in self.trains:
            if trainn.num == numbers:
                c += 1
                print('Номер поезда:', trainn.num)
                print('Пункт назначения:', trainn.name)
                print('Время отправления(ЧЧ:ММ):', trainn.time)

        if c == 0:
            print("Таких поездов нет!")

    def load(self, filename: str) -> None:
        with open(filename, 'r', encoding='utf8') as fin:
            xml = fin.read()
        parser = ET.XMLParser(encoding="utf8")
        tree = ET.fromstring(xml, parser=parser)

        self.trains = []
        for train_element in tree:
            name, num, time = None, None, None

            for element in train_element:
                if element.tag == 'name':
                    name = element.text
                elif element.tag == 'num':
                    num = element.text
                elif element.tag == 'time':
                    time = element.text

                if name is not None and num is not None \
                        and time is not None:
                    self.trains.append(
                        train(
                            name=name,
                            num=num,
                            time=time
                        )
                    )

    def save(self, filename: str) -> None:
        root = ET.Element('trains')
        for train in self.trains:
            train_element = ET.Element('train')

            name_element = ET.SubElement(train_element, 'name')
            name_element.text = train.name

            num_element = ET.SubElement(train_element, 'num')
            num_element.text = train.num

            time_element = ET.SubElement(train_element, 'time')
            time_element.text = str(train.time)

            root.append(train_element)

        tree = ET.ElementTree(root)
        with open(filename, 'wb') as fout:
            tree.write(fout, encoding='utf8', xml_declaration=True)


if __name__ == '__main__':

    logging.basicConfig(
        filename='trains.log',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s:%(message)s'
    )

    trains = []
    staff = Staff()
    # Организовать бесконечный цикл запроса команд.
    while True:
        try:
            # Запросить команду из терминала.
            command = input(">>> ").lower()
            # Выполнить действие в соответствие с командой.
            if command == 'exit':
                break

            elif command == 'add':
                # Запросить данные о поезде.
                name = input("Название пункта назначения: ")
                num = input("Номер поезда: ")
                time = input("Время отправления: ")

                staff.add(name, num, time)
                logging.info(
                    f"Добавлен поезд: {num}, "
                    f"пункт назначения {name}, "
                    f"отправляющийся в {time} времени."
                )

            elif command == 'list':
                print(staff)
                logging.info("Отображен список поездов.")

            elif command.startswith('select '):
                parts = command.split(' ', maxsplit=2)

                numbers = int(parts[1])

                c = 0

                for trainn in trains:
                    if trainn.num == numbers:
                        c += 1
                        print('Номер поезда:', trainn.num)
                        print('Пункт назначения:', trainn.name)
                        print('Время отправления:', trainn.time)
                        logging.info(
                            f"Найден поезд с номером {num} ."
                        )

                if c == 0:
                    print("Таких поездов нет!")
                    logging.warning(
                        f"Поезд с номером {num} не найден."
                    )

            elif command.startswith('load '):
                # Разбить команду на части для выделения имени файла.
                parts = command.split(' ', maxsplit=1)
                staff.load(parts[1])
                logging.info(f"Загружены данные из файла {parts[1]}.")

            elif command.startswith('save '):
                # Разбить команду на части для выделения имени файла.
                parts = command.split(' ', maxsplit=1)
                staff.save(parts[1])
                logging.info(f"Сохранены данные в файл {parts[1]}.")

            elif command == 'help':

                print("Список команд:\n")
                print("add - добавить поезд;")
                print("list - вывести список поездов;")
                print("select <номер поезда> - запросить информацию о выбранном поезде;")
                print("help - отобразить справку;")
                print("load <имя файла> - загрузить данные из файла;")
                print("save <имя файла> - сохранить данные в файл;")
                print("exit - завершить работу с программой.")
            else:
                raise UnknownCommandError(command)

        except Exception as exc:
            logging.error(f"Ошибка: {exc}")
            print(exc, file=sys.stderr)
