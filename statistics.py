import sys
import psutil

def gather_statistics(*args):
    """
    Модуль предназначен циклического сбора и записи в файл статистических данных о состоянии хоста.
    Модуль рассчитан для работы с ОС на базе Linux.

    Входные параметры:
    '_имя_файла_'           -  имя файла (с путем, например: /home/user/laptop_stat.txt)
    '_интервал_в_секундах_' -  интервал меджу замерами данных

    Возвращаемое значение отсутствуют

    В результате работы формируется файл, пригодный для дальнейшего парсинга, и содержащий
    записи в формате:
    cpu1;...;cpuN;rss;vms;file_descriptors_in_use;
    cpu1;...;cpuN;rss;vms;file_descriptors_in_use;
    cpu1;...;cpuN;rss;vms;file_descriptors_in_use;
    ....
    В каждой строке файла:
     - cpu1;...;cpuN - средняя загрузка ядер CPU (с 1-го по N-е) за заданный пользователем интервал
     - rss - величина параметра Resident Set Size
     - vms - величина параметра Virtual Memory Size
     - file_descriptors_in_use  - количество открытых файловых дескрипторов

    Исполнение файла прерывается пользователем (Ctrl+C, Ctrl+Z)

    Автор: Александр Таранов
    email: al.alex.taranov@gmail.com
    дата: 21.09.2021
    """
    # Проверка аргументов
    if len(sys.argv) < 3:
        print('Введите параметры в формате: python3 _имя_файла_  _интервал_в_секундах_')
        return
    try:
        INTERVAL = int(sys.argv[2])
    except ValueError:
        print('Интервал должен быть целым числом (секунд)')
        return
    FILENAME = sys.argv[1]
    
    # Вход в цикл сбора статстики
    index = 0
    while(True):
        try:
            # Сбор статистических данных
            index +=1
            cpu_load_list = psutil.cpu_percent(interval=INTERVAL, percpu=True)
            memory_values = psutil.Process().memory_info()
            with open('/proc/sys/fs/file-nr', 'r') as rf:
                lines_list = rf.read().splitlines()
                descriptors_info_list = lines_list[0].split('\t')
                file_descriptors_in_use = descriptors_info_list[0]

            # Запись в файл
            try:
                with open(FILENAME, 'a') as wf:
                    for elem in cpu_load_list:
                        wf.write(str(elem))
                        wf.write(';')
                    wf.write(str(memory_values.rss))
                    wf.write(';')
                    wf.write(str(memory_values.vms ))
                    wf.write(';')
                    wf.write(str(file_descriptors_in_use))
                    wf.write('\n')
            except FileNotFoundError as e:
                print('Указан неверный путь к файлу записи:  ' + FILENAME)
                return
            except PermissionError as e:
                print('Нет прав на запись в указанную папку:  ' + FILENAME)
                return
            print('замер произведён  ' + str(index))
        except KeyboardInterrupt:
            print('\nсбор статистики осановлен пользователем')
            return
    return

gather_statistics()