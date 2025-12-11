from collections import defaultdict
import requests
import csv
from datetime import datetime, date, timedelta


class Users:
    def __init__(self, users: list[str]) -> None:
        self.users: list[User] = []
        self.count: int = 0
        for user in users:
            try:
                user_obj = User(user["username"], user["fullname"])
            except Exception as e:
                print(f"Error adding user {user['username']}: {e}")
                continue
            print(f"{user['fullname']} added")
            self.count += 1
            self.users.append(user_obj)

    @classmethod
    def from_csv(cls, file_path: str) -> "Users":
        """
        This method creates a Users object from a CSV file
        CSV file should have two columns:id, username, fullname

        args:
            file_path(str): path to the CSV file
        returns:
            Users: Users object
        """
        users = []
        with open(file_path, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                users.append({"username": row["username"], "fullname": row["fullname"]})
        return cls(users)

    def add_kata_ids_by_file(self, file_path: str = "input/kata_ids.csv") -> None:
        """
        This method adds kata ids from a CSV file
        CSV file should have one column: kata_id

        args:
            file_path(str): path to the CSV file
        returns:
            kata_ids(list[str]): list of kata ids
        """
        kata_names = []
        kata_ids = []
        with open(file_path, mode="r") as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                kata_names.append(row[0])
                kata_ids.append(row[1])

        self.names = kata_names
        self.kata_ids = kata_ids

    def add_user(self, username):
        """
        This method adds a new user to the list of users

        args:
            username(str): username
        returns:
            total(int): total number of users
        """
        user = User(username)
        self.users.append(user)
        return len(self.users)

    def get_total_daily(self):
        """
        This method returns the total number of completed for all users by daily

        user = {
            "username": "",
            "name": "",
            "total_completed": 0,
        }
        """
        result = []
        for user in self.users:
            user = {
                "name": user.fullname,
                "username": user.username,
                "daily_completed": user.get_daily(),
            }
            result.append(user)
        result = sorted(result, key=lambda x: x["total_completed"], reverse=True)
        return result

    def get_total_weekly(self):
        """
        This method returns the total number of completed for all users by weekly

        user = {
            "username": "",
            "name": "",
            "total_completed": 0,
        }
        """
        result = []
        for user in self.users:
            user = {
                "name": user.fullname,
                "username": user.username,
                "weekly_completed": user.get_weekly(),
            }
            result.append(user)
        result = sorted(result, key=lambda x: x["total_completed"], reverse=True)
        return result

    def get_total_date(self, date_type):
        """
        This method returns the total number of completed for all users by date type (daily, weekly, monthly)
        """
        result = []
        for user in self.users:
            if date_type == "daily":
                completed = user.get_daily()
            elif date_type == "weekly":
                completed = user.get_weekly()
            elif date_type == "monthly":
                completed = user.get_monthly()
            else:
                raise ValueError(
                    "Invalid date type. Must be 'daily', 'weekly', or 'monthly'."
                )

            user_data = {
                "name": user.fullname,
                "username": user.username,
                f"{date_type}_completed": completed,
            }
            result.append(user_data)
        result = sorted(result, key=lambda x: x[f"{date_type}_completed"], reverse=True)
        return result

    def get_total_completed(self):
        """
        This method returns the total number of completed for all users

        returns:
            result(list[dict]): total number of completed for all users
        """
        user = {
            "username": "",
            "total_completed": 0,
            "name": "",
        }
        result = []
        for user_obj in self.users:
            user_dict = {
                "username": user_obj.username,
                "total_completed": user_obj.get_total(),
                "name": user_obj.fullname,
            }
            result.append(user_dict)
        result = sorted(result, key=lambda x: x["total_completed"], reverse=True)
        return result

    def get_total_daily_completed_histogram(self):
        """
        This method returns the total number of completed for all users by daily histogram

        returns:
            result(list[dict]): total number of completed for all users by daily histogram
        """
        result = []
        for user in self.users:
            histogram = user.daily_completed_task_histogram()
            user_data = {
                "username": user.username,
                "daily_histogram": histogram,
            }
            result.append(user_data)
        return result

    def export_solved_katas_count_to_csv(
        self, from_date: str = None, file_path: str = "output/codewars_katas.csv"
    ) -> str:
        """
        This method exports the count of solved katas for all users to a CSV file.
        
        If kata_ids have been loaded (via add_kata_ids_by_file), the method exports:
        - A detailed breakdown showing which specific katas each user solved
        - Columns include: id, Username, Solved Katas count, and individual kata URLs
        - Users are sorted by total solved katas in descending order
        
        If no kata_ids are loaded, the method exports:
        - Basic count of completed katas for each user since the specified date
        - Columns include: id, Username, Solved Katas count
        - Users are sorted by completed katas count in descending order

        args:
            from_date (str): Start date for filtering completed katas in "YYYY-MM-DD" format
            file_path (str, optional): Path to the output CSV file. Defaults to "output/codewars_katas.csv"
            
        returns:
            str: "OK" on success
            
        Note:
            - The method uses kata_ids attribute if available (set via add_kata_ids_by_file)
            - CSV includes hyperlinks to kata URLs when kata_ids are loaded
            - Users are automatically sorted by their performance
        """
        if not hasattr(self, "kata_ids"):
            print("No kata IDs loaded, exporting basic completed katas count.")
            with open(file_path, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["id", "Username", "Solved Katas"])
                
                self.users.sort(
                    key=lambda u: u.get_completed_by_date(date_str=from_date),
                    reverse=True,
                )
                
                for id, user in enumerate(self.users):
                    writer.writerow([id + 1, user.fullname, user.get_completed_by_date(date_str=from_date)])
            return "OK"
        print("Exporting detailed solved katas count with kata IDs.")
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                ["id", "Username", "Solved Katas"] + self.get_kata_ids_as_urls()
            )
            # Sort users by number of solved katas in descending order
            self.users.sort(
                key=lambda u: u.count_solved_katas_by_given_ids(self.kata_ids, from_date=from_date),
                reverse=True,
            )
            for id, user in enumerate(self.users):
                my_list = user.count_solved_katas_by_given_ids_list(
                    self.kata_ids, from_date=from_date
                )
                writer.writerow([id + 1, user.fullname, sum(my_list)] + my_list)
        return "OK"

    def get_kata_ids_as_urls(self) -> list[str]:
        """
        This method converts the kata IDs to their corresponding URLs.

        returns:
            list[str]: list of kata URLs
        """
        base_url = "https://www.codewars.com/kata/"
        kata_urls = [
            f'=HYPERLINK("{base_url}{kata_id}"; "{name}")'
            for name, kata_id in zip(self.names, self.kata_ids)
        ]
        return kata_urls

    def export_total_completed_to_csv(
        self, file_path: str = "output/codewars_total.csv"
    ) -> str:
        """
        This method exports the total number of completed for all users to a csv file
        """

        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["id", "Username", "Completed Tasks"])
            for id, user in enumerate(self.users):
                writer.writerow([id + 1, user.username, user.get_total()])
        return "OK"

    def export_total_daily_completed_histogram_to_csv(
        self, file_path: str = "output/codewars_daily_histogram.csv"
    ) -> str:
        """
        This method exports the total number of completed for all users by daily histogram to a csv file
        """

        all_data = {}
        for user in self.users:
            histogram = User(user.username).daily_completed_task_histogram()
            for day, count in histogram.items():
                if day not in all_data:
                    all_data[day] = {}
                all_data[day][user.username] = count

        # Write combined data
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Date"] + [user.username for user in self.users])
            for day in sorted(all_data.keys()):
                row = [day] + [
                    all_data[day].get(user.username, 0) for user in self.users
                ]
                writer.writerow(row)
        return "OK"


class User:
    """
    User class
    """

    def __init__(
        self,
        username: str,
        full_name: str = None,
        base_url: str = "https://www.codewars.com/api/v1/users/",
    ) -> None:
        self.username = username
        self.fullname = full_name

        self.base_url = base_url
        # Get user data from API and full URL that has username
        self.data, self.full_url = self.get_user_data()

        # Set fullname if not provided
        self.set_fullname()

        # Get all completed kata
        self.completed = self.get_all_completed()

    def count_solved_katas_by_given_ids(self, kata_ids: list[str], from_date: str = None) -> int:
        """
        Count number of solved katas by given ids
        args:
            kata_ids(list[str]): list of kata ids
        returns(int): number of solved katas
        """
        count = 0

        if from_date:
            date_obj = datetime.strptime(from_date, "%Y-%m-%d")
            back_days = (datetime.now() - date_obj).days
            cutoff_date = datetime.now() - timedelta(days=back_days)
        else:
            back_days = 0

        for kata_id in kata_ids:
            kata = self.get_kata_by_given_id(kata_id)
            if kata is not None and (
                back_days == 0
                or datetime.fromisoformat(kata["completedAt"]).replace(tzinfo=None)
                >= cutoff_date
            ):
                count += 1
        return count

    def count_solved_katas_by_given_ids_list(
        self, kata_ids: list[str], from_date: str
    ) -> list[int]:
        """
        Count number of solved katas by given ids

        args:
            kata_ids(list[str]): list of kata ids
        returns(list[int]): list of 1/0 for each kata id
        """
        result = []
        
        if from_date:
            date_obj = datetime.strptime(from_date, "%Y-%m-%d")
            back_days = (datetime.now() - date_obj).days
            cutoff_date = datetime.now() - timedelta(days=back_days)
        else:
            back_days = 0

        if back_days > 0:
            cutoff_date = datetime.now() - timedelta(days=back_days)

        for kata_id in kata_ids:
            kata = self.get_kata_by_given_id(kata_id)
            if kata is not None and (
                back_days == 0
                or datetime.fromisoformat(kata["completedAt"]).replace(tzinfo=None)
                >= cutoff_date
            ):
                result.append(1)
            else:
                result.append(0)
        return result

    def get_kata_by_given_id(self, kata_id: str) -> dict | None:
        """
        Get kata details by given id

        args:
            kata_id(str): kata id
        returns(dict | None): kata details or None if not found
        """
        data_problems = self.completed["data"]
        for item in data_problems:
            if item["id"] == kata_id:
                return item
        return None

    def get_user_data(self) -> tuple:
        """
        Get user data from the Codewars API.
        Args:
            username (str, optional): The Codewars username to retrieve data for. Defaults to None.
        Returns:
            tuple: A tuple containing:
                - dict: User data retrieved from the API
                - str: The full URL used for the request
        Raises:
            ValueError: If the username is not found (status code != 200)
        """
        full_url = f"{self.base_url}{self.username}"
        r = requests.get(url=full_url)
        if r.status_code != 200:
            raise ValueError(f"Username {self.username} not found")

        data = r.json()
        return data, full_url

    def get_all_completed(self) -> dict:
        """
        Get number of completed kata

        returns(int): number of completed kata
        """
        URL = f"{self.full_url}/code-challenges/completed"
        r = requests.get(url=URL)

        data = r.json()

        total_pages = data["totalPages"]

        for page in range(1, total_pages):
            URL_page = f"{self.full_url}/code-challenges/completed?page={page}"
            r_page = requests.get(url=URL_page)
            data_page = r_page.json()
            data["data"].extend(data_page["data"])

        return data

    def set_fullname(self) -> None:
        """
        Set fullname

        args:
            fullname(str): fullname
        """
        if self.fullname is None:
            fullname = self.data.get("name")
            self.fullname = fullname

    def get_total(self) -> int:
        """
        Get total number of completed kata

        returns(int): total number of completed kata
        """
        if self.check_username() == True:
            return self.data["codeChallenges"]["totalCompleted"]
        return False

    def get_completed_by_date(self, date_str: str) -> int:
        """
        Get number of completed kata by date

        args:
            date(str): date in format "year-month-day" (e.g., "2024-08-02")
        returns(int): number of completed kata
        """
        if not date_str:
            return self.get_total()
        date = datetime.strptime(date_str, "%Y-%m-%d")
        data_problems = self.completed["data"]
        count = 0
        for item in data_problems:
            date_old = datetime.fromisoformat(item["completedAt"])
            if date.date() <= date_old.date():
                count += 1
        return count

    def get_monthly(self) -> int:
        """
        Get number of completed kata last month

        returns(int): number of completed kata
        """
        now = datetime.now()
        now_second = now.timestamp()
        count = 0
        for item in self.completed["data"]:
            date_old = datetime.fromisoformat(item["completedAt"])
            date_old_second = date_old.timestamp()
            if abs(now_second - date_old_second) <= 30 * 24 * 3600:
                count += 1
        return count

    def get_daily(self) -> int:
        """
        Get number of completed kata last day

        returns(int): number of completed kata
        """
        today = date.today()

        count = 0
        data = self.completed["data"]
        for item in data:
            # 2024, 8, 2
            completed_at = datetime.fromisoformat(item["completedAt"])
            # Compare dates
            if today == completed_at.date():
                count += 1

        return count

    def get_weekly(self) -> int:
        """
        Get number of completed kata this week

        returns(int): number of completed kata
        """
        # Get current week date
        current_date = datetime.now().date()
        week_date = current_date - timedelta(days=datetime.now().weekday())

        data = self.completed["data"]
        total = 0  # Total number of completed kata in current week
        for item in data:
            completed_at = datetime.fromisoformat(item["completedAt"])
            # Check if completed date is in current week
            if week_date <= completed_at.date() <= current_date:
                total += 1

        return total

    def get_honor(self) -> int:
        """
        Total honor points earned by user

        returns(int): total honor points
        """
        return self.data.get("honor")

    def get_clan(self) -> str:
        """
        Get clan name

        returns(str): clan name
        """
        return self.data.get("clan")

    def get_leaderboard_position(self) -> int:
        """
        Get leaderboard position

        returns(int): leaderboard position
        """
        return self.data.get("leaderboardPosition")

    def get_skills(self) -> list:
        """
        Get list of user programming skills

        returns(list): list of porgramming languages
        """
        return self.data.get("skills")

    def daily_completed_task_histogram(self):
        """
        Given a list of task dictionaries (each having a 'completedAt' field),
        return a histogram of completed tasks grouped by day (YYYY-MM-DD) and
        by hour (0-23).

        :param data: list of dictionaries, each with at least a 'completedAt' field
                    in ISO 8601 format (e.g., '2025-01-08T06:09:32.508Z')
        :return: A dictionary where:
                - keys:   'YYYY-MM-DD' strings
                - values: a list of 24 integers [count_0, count_1, ... count_23]
        """
        # This dictionary will map day_string -> [24-hour histogram].
        # For example: histograms["2025-01-08"] = 0
        histograms = defaultdict(lambda: 0)

        for task in self.completed["data"]:
            completed_at_str = task.get("completedAt")
            if not completed_at_str:
                continue

            # Parse the completedAt string into a datetime object
            # Example "completedAt": "2025-01-08T06:09:32.508Z"
            completed_dt = datetime.fromisoformat(completed_at_str)
            # Create a day string in "YYYY-MM-DD" format
            day_str = completed_dt.date().isoformat()

            # Increase the count for that day
            histograms[day_str] += 1

            # Convert the defaultdict back to a regular dictionary
        histograms = dict(histograms)

        return histograms
