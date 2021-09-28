import sys
import psutil
import subprocess

def gather_statistics(*args):
    """
    Эта функция предназначена для запуска стороннего процесса и сбора статистики о нём.
    
    Собираются следующие статистические данные:
     - процент загрузки CPU;
     - Resident Set Size
     - Virtual Memory Size
     - количество открытых файловых дескрипторов
    Эта информация циклически записывается в файл. Период записи указывается 
    пользователем при запуске.

    Для корректного запуска программы необходимо указать имя процесса и интервал.
    Например:
    user# python3 one_proc_statistics.py vlc 2.5
    где 'vlc' - это название процесса, а '2.5' - это интервал сбора статистики


    В результате работы формируется файл, пригодный для дальнейшего парсинга, и содержащий
    записи в формате:
        cpu_usage;rss;vms;file_descriptors_in_use;
        cpu_usage;rss;vms;file_descriptors_in_use;
        cpu_usage;rss;vms;file_descriptors_in_use;
        ....
    В каждой строке файла:
        - cpu_usage- средняя загрузка CPU за заданный пользователем интервал
        - rss - величина параметра Resident Set Size
        - vms - величина параметра Virtual Memory Size
        - file_descriptors_in_use  - количество открытых файловых дескрипторов

    Исполнение файла прерывается пользователем (Ctrl+C, Ctrl+Z)

    Автор: Александр Таранов
    дата: 29.09.2021
    """


    # Проверяем правильность ввода параметров и запускаем процесс
    if len(sys.argv) < 3:
        print('Введите параметры в формате: \
            python3 one_proc_statistics.py _имя_процесса_  _временной_интервал_')
        return
    try:
        INTERVAL = float(sys.argv[2])
    except ValueError:
        print('Временной интервал введён некорректно')
        return
    try:
        process = subprocess.Popen(sys.argv[1])
        process_id = process.pid
    except FileNotFoundError as e:
        print('Имя процесса введено некорректно')
        return

    # Запускаем циклический сбор и сохранение статистики
    while(True):
        try:
            processes = [proc for proc in psutil.process_iter()]
            for proc in processes:
                if proc.pid == process_id:

                    # Получаем информацию о цп и памяти
                    cpu_usage = proc.cpu_percent(interval=INTERVAL)
                    rss = proc.memory_info().rss
                    vms = psutil.Process().memory_info().vms

                    # Получаем информацию о файловых дескрипторах
                    check_fd = subprocess.Popen(('ls', '-l', '/proc/' + str(process_id)\
                         +'/fd'), stdout=subprocess.PIPE)
                    output = subprocess.check_output(('wc', '-l'), stdin=check_fd.stdout)
                    amount_of_fd = str(int(output.decode('UTF-8')) - 1)

                    # Пишем в файл
                    with open('output_stat.txt', 'a') as wf:
                        wf.write(str(cpu_usage))
                        wf.write(';')
                        wf.write(str(rss))
                        wf.write(';')
                        wf.write(str(vms ))
                        wf.write(';')
                        wf.write(amount_of_fd)
                        wf.write('\n')
            print('замер произведён')
        except KeyboardInterrupt:
            process.kill()
            print('\nпроцесс остановлен; сбор статистики завершён')
            return
    return


if __name__=="__main__":
    gather_statistics()