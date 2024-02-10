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
        self.ixemplee: str = ""
        self.skip_dates: set[str] = set()

    def _initilize_timewatch(
        self,
    ) -> None:
        login_soup = self._login()
        self._set_referer_header(login_soup)
        self._update_request_data()

    def _login(
        self,
    ) -> BeautifulSoup:
        print(colored(consts.LOGGING_IN_TEXT, "light_blue"))
        res = self.session.post(
            consts.TIMEWATCH_USER_VALIDATION_URL,
            data={
                "comp": self.config.company_number,
                "name": self.config.employee_number,
                "pw": self.config.employee_password,
            },
        )
        # self.config.cookies['PHPSESSID'] = self.session.cookies.get('PHPSESSID')
        return BeautifulSoup(res.text, "html.parser")

    def _set_referer_header(
        self,
        login_soup: BeautifulSoup,
    ) -> None:
        link = next(
            link
            for link in login_soup.find_all("a", {"class": "new-link"})
            if consts.UPDATE_HOURS_LINK_TEXT in link.text
        )
        parsed_url = urlparse(link.get("href"))
        params = parse_qs(parsed_url.query)
        self.ixemplee = params["ee"][0] if params.get("ee") else ""
        self.request_headers["referer"] = (
            "https://c.timewatch.co.il/punch/editwh.php"
            f'?ee={self.ixemplee}&e={self.config.company_number}&m={params["m"][0]}&y={params["y"][0]}'
        )

    def _update_request_data(
        self,
    ) -> None:
        self.request_data["c"] = self.config.company_number
        self.request_data["e"] = self.ixemplee
        self.request_data["tl"] = self.ixemplee
        self.request_data["ehh0"] = self.config.start_time_hour
        self.request_data["emm0"] = self.config.start_time_minute
        self.request_data["xmm0"] = self.config.end_time_minute

    def _get_punch_page(
        self,
    ) -> BeautifulSoup:
        res = self.session.get(
            consts.TIMEWATCH_DATE_TABLE_URL,
            params={
                "ee": self.ixemplee,
                "e": self.config.company_number,
                "m": self.current_date.month,
                "y": self.current_date.year,
            },
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
        if retries > 5:
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
                self.submit_hours()

        jobs_left = self._get_required_dates()
        if jobs_left:
            print(
                colored(
                    f"consts.MISSING_DATES_RETRY_TEXT, jobs_left={len(jobs_left)}",
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
    ) -> None:
        print(
            colored(
                consts.SUBMITTING_HOURS_TEXT.format(
                    date=self.request_data["d"],
                    start_time=f'{self.request_data["ehh0"]}:{self.request_data["emm0"]}',
                    end_time=f'{self.request_data["xhh0"]}:{self.request_data["xmm0"]}',
                ),
                "light_blue",
            ),
        )
        time.sleep(0.25)
        res = self.session.post(
            consts.TIMEWATCH_HOUR_UPDATE_URL,
            headers=self.request_headers,
            # cookies=self.config.cookies,
            data=self.request_data,
        )
        if res.text == consts.TIMEWATCH_SET_TIME_ISSUE_TEXT:
            print(
                colored(
                    f'{consts.UNABLE_TO_FILL_TEXT}, problematic_date={self.request_data["d"]}',
                    "red",
                ),
            )
            self.skip_dates.add(self.request_data["d"])

    def fill(
        self,
    ) -> None:
        self._initilize_timewatch()
        jobs = self._get_required_dates()
        self._fill_dates(jobs)
