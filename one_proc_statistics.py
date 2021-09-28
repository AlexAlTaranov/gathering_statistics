import sys
import psutil
import subprocess

def gather_statistics(*args):
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