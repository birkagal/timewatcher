import os
import re
from configparser import ConfigParser
from pathlib import Path

from termcolor import colored

from . import consts


class Config:
    """Configuration manager helper class to initilize configuration
    from well known config.ini file and exposing relevant configurations."""

    company_number: str
    employee_number: str
    employee_password: str
    start_time_hour: str
    start_time_minute: str
    end_time_hour: str
    end_time_minute: str
    auto_end_time: bool = True
    date_format: str = "%Y-%m-%d"

    def __init__(self):
        configs = self._initilize_configs()

        self.company_number = configs["company_number"]
        self.employee_number = configs["employee_number"]
        self.employee_password = configs["employee_password"]

        self.auto_end_time = configs["auto_end_time"].lower() == "true"
        self.start_time_hour, self.start_time_minute = re.findall(
            r"\d{2}",
            configs["start_time"],
        )
        self.end_time_hour, self.end_time_minute = re.findall(
            r"\d{2}",
            configs["end_time"],
        )

    def _initilize_configs(
        self,
    ) -> dict[str, any]:
        """Initilizes the configuration object from a well know location of config.ini file.

        :return: a dict holding all the user configuration settings.
        """
        config = ConfigParser()
        config.read(f"{os.path.expanduser(consts.CONFIG_FILE_PATH)}/config.ini")
        is_config_updated = False

        if config.has_section(consts.AUTHENTICATION) is False:
            print(colored(consts.CANT_FIND_CONFIGURATION_TEXT, "yellow"))
            config.add_section(consts.AUTHENTICATION)
        for option, text, default in consts.AUTHENTICATION_VALUES:
            if config.has_option(
                consts.AUTHENTICATION,
                option,
            ) is False or not config.get(consts.AUTHENTICATION, option):
                is_config_updated = True
                config.set(
                    consts.AUTHENTICATION,
                    option,
                    input(colored(text, "light_cyan")) or default,
                )

        if config.has_section(consts.PREFERENCES) is False:
            config.add_section(consts.PREFERENCES)
        for option, text, default in consts.PREFERENCES_VALUES:
            if config.has_option(consts.PREFERENCES, option) is False:
                is_config_updated = True
                config.set(
                    consts.PREFERENCES,
                    option,
                    input(colored(text, "light_cyan")) or default,
                )

        if is_config_updated is True:
            p = Path(os.path.expanduser(consts.CONFIG_FILE_PATH))
            p.mkdir(parents=True, exist_ok=True)
            config.write(open(f"{str(p)}/config.ini", "w"))
            print(
                colored(
                    consts.CONFIGURATION_INITILIZED_TEXT.format(path=str(p)),
                    "yellow",
                ),
            )

        return dict(config[consts.AUTHENTICATION].items()) | dict(
            config[consts.PREFERENCES].items(),
        )
