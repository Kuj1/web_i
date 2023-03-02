## Перед запуском скрипта:
- Убедитесь, что у вас установлен Python 3.10:
```bash
   python -V
```
-  Убедитесь что у вас установлен пакетный менеджер poetry:
```bash
   poetry -V
```
- Если предыдущие шаги выполнены успешно, то скачайте / клонируйте репозиторий перейдите в корень и выполните:
```bash
   git clone https://github.com/Kuj1/yt_privacy.git  // this command clone this repo in your working directory
   poetry install
```
- Теперь вы готовы к запуску скрипта!

## Запуск скрипта:
- Для того, чтобы запустить скрипт выполните из корня проекта:
```bash
   poetry shell   
```
- Затем перейдите в папку app и выполните:
```bash
   cd app/ // change directory
   python main.py
```
## How to use
- После этого запуститься веб-приложение на localhost, в дебаг режиме.
- Перейдите по указаному в консоли адресу и вы увидете два окна.
- В первое надо вставить свой api ключ, а в окно под ним - прокси (каждое с новой строки), затем нажать на кнопку `check it`
- Если все сделано правильно, через некоторое время (зависит от кол-во прокси) вас перенаправит на страницу со списком уже проверенных прокси.
