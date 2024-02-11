import os
import re
import subprocess
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
            self._initilize_config_file(config)
        if config[consts.PREFERENCES]["auto_execute"].lower() == "true":
            filepath = os.path.expanduser(consts.LAUNCH_AGENT_FILE_PATH)
            if os.path.isfile(filepath) is False:
                self._initilize_launchd(filepath, config)
        return dict(config[consts.AUTHENTICATION].items()) | dict(
            config[consts.PREFERENCES].items(),
        )

    def _initilize_config_file(
        self,
        config: ConfigParser,
    ) -> None:
        """Create the config.ini file in the well-know location for future program calls.

        :param config: ConfigParser object to save to the config.ini file."""
        p = Path(os.path.expanduser(consts.CONFIG_FILE_PATH))
        p.mkdir(parents=True, exist_ok=True)
        config.write(open(f"{str(p)}/config.ini", "w"))
        print(
            colored(
                consts.CONFIGURATION_INITILIZED_TEXT.format(path=str(p)),
                "yellow",
            ),
        )

    def _initilize_launchd(
        self,
        filepath: str,
        config: ConfigParser,
    ) -> None:
        """Initilizes the Launchd file with the appropiate configuration.
        This file is used to run TimeWatcher every "day_to_run" of the month
        at "hour_to_run" time.

        :param filepath: The path to created the launchd file at.
        :param config: ConfigParser object with the day_to_execute and hour_to_execute
        configuration parameters."""
        day_to_execute, hour_to_execute = config.get(
            consts.PREFERENCES,
            "day_to_execute",
        ), config.get(
            consts.PREFERENCES,
            "hour_to_execute",
        )
        p = Path(os.path.expanduser(consts.LAUNCH_AGENT_FILE_PATH))
        p.mkdir(parents=True, exist_ok=True)
        file_content = consts.LAUNCH_AGENT_FILE_CONTENT.format(
            day_to_execute=day_to_execute,
            hour_to_execute=hour_to_execute,
        )
        with open(filepath, "w") as f:
            f.writelines(file_content)
        subprocess.run(["launchctl", "load", consts.LAUNCH_AGENT_FILE_NAME], check=True)
        print(
            colored(
                consts.LAUNCHD_INITILIZED_TEXT.format(path=filepath),
                "yellow",
            ),
        )
