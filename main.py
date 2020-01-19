from charbot import CharBot
from time import sleep


def main():
    bot = CharBot()
    sleep(1.5)
    bot.init_longpol()
    sleep(1.5)
    bot.run()


if __name__ == '__main__':
    main()
