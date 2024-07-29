import re
import time
from dataclasses import dataclass
from datetime import date
from datetime import datetime
from urllib.parse import parse_qs
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from termcolor import colored

from . import configs
from . import consts
from . import data


@dataclass
class Job:
    """Helper class to hold the data of a required date job.
    Each job has the target date and the needed amount of hours."""

    needed_hours: int
    date: date


class TimeWatcher:
    def __init__(
        self,
    ) -> None:
        self.config = configs.Config()
        self.session = requests.Session()
        self.request_headers = data.HEADERS
        self.request_data = data.DATA
        self.current_date = datetime.now()
        self.skip_dates: set[str] = set()

    def _initialize_timewatch(
        self,
    ) -> None:
        """Kickstart the Timewatch initialization process.
        Login to the Timewatch website, and update the session referer to the
        correct URL based on the current date."""

        login_soup = self._login()
        self._set_referer_header(login_soup)
        self._update_request_data()

    def _login(
        self,
    ) -> BeautifulSoup:
        """Login to Timewatch using the validate_user URL and the user information.

        :return: BeautifulSoup object of the homepage after signing in."""
        print(colored(consts.LOGGING_IN_TEXT, "light_blue"))
        res = self.session.post(
            consts.TIMEWATCH_USER_VALIDATION_URL,
            data={
                "comp": self.config.company_number,
                "name": self.config.employee_number,
                "pw": self.config.employee_password,
            },
        )
        return BeautifulSoup(res.text, "html.parser")

    def _set_referer_header(
        self,
        login_soup: BeautifulSoup,
    ) -> None:
        """Taking the BeatufilSoup object of the Timewatch homepage and extracting the
        Punch page URL with the relevant params from it. Setting the "referer" header to that
        URL.

        :param: login_soup: BeautifulSoup object of the homepage after singning in."""

        script_tag = login_soup.find(
            "script",
            text=re.compile(r"function updateAttendance"),
        )
        url_pattern = re.compile(
            r'window\.location\s*=\s*"(/punch/editwh\.php\?[^"]+)"',
        )
        url = url_pattern.search(script_tag.string).group(1)
        params = parse_qs(url.split("?")[1])
        ixemplee = params["ee"][0] if params.get("ee") else ""
        self.request_data["e"] = ixemplee
        self.request_data["tl"] = ixemplee
        self.request_headers["referer"] = url

    def _update_request_data(
        self,
    ) -> None:
        """Update the request_data variable with user configuration information."""

        self.request_data["c"] = self.config.company_number
        self.request_data["ehh0"] = self.config.start_time_hour
        self.request_data["emm0"] = self.config.start_time_minute
        self.request_data["xmm0"] = self.config.end_time_minute

    def _get_punch_page(
        self,
    ) -> BeautifulSoup:
        """After successful login, browse to the main punch page.
        Also updates the request_data with the new generated csrf_token

        :return: BeatifulSoup object of the main punch page."""

        res = self.session.get(
            f'{consts.TIMEWATCH_BASE_URL}{self.request_headers["referer"]}',
        )
        self.request_data["csrf_token"] = re.search(
            r'var csrf_token="(.*)";',
            res.content.decode(),
        ).group(1)
        punch_page = BeautifulSoup(res.text, "html.parser")
        return punch_page

    def _get_required_dates(
        self,
    ) -> list[Job]:
        """Using the BeatifulSoup object of the main punch page, iterate over the
        dates table rows and find dates that need to be filled in.
        Extract the date and required hours and store them in a Jobs list.

        :return: Job list of the required dates that needs to be filled.."""

        punch_page = self._get_punch_page()
        jobs: list[Job] = []
        for row in punch_page.find_all("tr", {"class": "update-data"}):
            if consts.HOURS_UPDATE_REQUIRED_TEXT in row.text:
                row_text: str = row.text
                match = re.search(r"(\d{2}-\d{2}-\d{4})", row_text)
                if not match:
                    continue
                row_date = datetime.strptime(
                    re.search(r"(\d{2}-\d{2}-\d{4})", row_text).group(1),
                    "%d-%m-%Y",
                ).date()
                if row_date.strftime(self.config.date_format) not in self.skip_dates:
                    needed_hours = int(
                        re.search(
                            rf'{row_date.strftime("%d-%m-%Y")}.*(\d):\d\d',
                            row_text,
                        ).group(1),
                    )
                    jobs.append(
                        Job(
                            date=row_date,
                            needed_hours=needed_hours,
                        ),
                    )
        return jobs

    def _fill_dates(
        self,
        jobs: list[Job],
        retries=0,
    ) -> None:
        """Iterate over the jobs list and fill the required hours for each job.
        Call itself recusively if not all the jobs have been filled. Can be called
        up to a maximum of 5 retries before failing.

        :param jobs: List of jobs that require filling up.
        :param retreis: Number of retries that attempted to fulfill the jobs list."""

        MAX_RETRIES = 5
        if retries > MAX_RETRIES:
            print(colored(consts.MAX_RETIRES_TEXT, "red"))
            return
        if len(jobs) == 0:
            print(colored(consts.FULLY_FILLED_TEXT, "light_blue"))
            return
        print(
            colored(
                consts.START_FILL_HOURS_TEXT.format(num_dates=len(jobs)),
                "light_blue",
            ),
        )
        for job in jobs:
            self.request_data["xhh0"] = (
                str(int(self.config.start_time_hour) + job.needed_hours)
                if self.config.auto_end_time
                else self.config.end_time_hour
            )
            job_date = job.date.strftime(self.config.date_format)
            if job_date not in self.skip_dates:
                self.request_data["d"] = job_date
                self.submit_hours(self.request_data)

        jobs_left = self._get_required_dates()
        if jobs_left:
            print(
                colored(
                    f"{consts.MISSING_DATES_RETRY_TEXT}, jobs_left={len(jobs_left)}",
                    "light_blue",
                ),
            )
            time.sleep(3)
            self._fill_dates(
                jobs=jobs_left,
                retries=retries + 1,
            )

    def submit_hours(
        self,
        data: dict[str, str],
    ) -> None:
        """Send a post request to fill the hours of a given data.

        :param data: Dictionary containing the data of a single date to be filled.
        The data is formatted in the cryptic way of Timewatch."""

        print(
            colored(
                consts.SUBMITTING_HOURS_TEXT.format(
                    date=data["d"],
                    start_time=f'{data["ehh0"]}:{data["emm0"]}',
                    end_time=f'{data["xhh0"]}:{data["xmm0"]}',
                ),
                "light_blue",
            ),
        )
        time.sleep(0.25)
        res = self.session.post(
            consts.TIMEWATCH_HOUR_UPDATE_URL,
            headers=self.request_headers,
            data=data,
        )
        if res.text == consts.TIMEWATCH_SET_TIME_ISSUE_TEXT:
            print(
                colored(
                    f'{consts.UNABLE_TO_FILL_TEXT}, problematic_date={data["d"]}',
                    "red",
                ),
            )
            self.skip_dates.add(data["d"])

    def fill(
        self,
    ) -> None:
        """Fill the Timewatch card of the user."""
        self._initialize_timewatch()
        jobs = self._get_required_dates()
        self._fill_dates(jobs)
