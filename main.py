from app import MyApp
from config import Config
import os


if __name__ == '__main__':
    if not os.path.exists(Config.temp):
        os.makedirs(Config.temp)
    app = MyApp()
    app.MainLoop()