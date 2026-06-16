from config.config_loader import load_config, create_config_file
from config.errors import ConfigError
from gui.main_window import MainWindow
from gui.controller import OrganizerController

def startup():
    try:
        config = load_config()
        return config
    except ConfigError as e:
        if e.key == "no_config_file":
            create_config_file()
            return load_config()
        raise e

if __name__ == "__main__":
    config_data = startup()
    app = MainWindow()
    controller = OrganizerController(app, config_data)
    app.set_controller(controller)
    controller.scan()
    app.mainloop()