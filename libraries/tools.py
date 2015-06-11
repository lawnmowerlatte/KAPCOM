#!/usr/bin/python

import logging


def breakpoint():
    """Python debug breakpoint."""
    
    from code import InteractiveConsole
    from inspect import currentframe

    caller = currentframe().f_back

    env = {}
    env.update(caller.f_globals)
    env.update(caller.f_locals)

    shell = InteractiveConsole(env)
    shell.interact(
        '* Break: {0} ::: Line {1}\n'
        '* Continue with Ctrl+D...'.format(
            caller.f_code.co_filename, caller.f_lineno
        )
    )


class KAPCOMLog:
    def __init__(self, name="KAPCOM Generic Logger", level=logging.WARNING):
        # Logging
        self.log = logging.getLogger(name)
        if not len(self.log.handlers):
            self.log.setLevel(level)

            long_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-10.10s]  %(message)s")
            short_formatter = logging.Formatter("[%(levelname)-8.8s]  %(message)s")

            file_handler = logging.FileHandler("logs/{0}/{1}.log".format("./", name))
            file_handler.setFormatter(long_formatter)
            self.log.addHandler(file_handler)
        
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(short_formatter)
            self.log.addHandler(console_handler)
        
            self.log.critical("Set up logging for " + name)
        else:
            self.log.warn("Logging already set up for " + name)
            
    def set_level(self, level):
        self.log.critical("Changing log level to " + logging.getLevelName(level))
        self.log.setLevel(level)