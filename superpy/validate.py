import datetime


def validate_date(date):
    try:
        datetime.date.fromisoformat(date)
    except ValueError:
        raise ValueError(
            f"Incorrect data format, {date} should be of the format YYYY-MM-DD"
        )


if __name__ == "__main__":
    print(validate_date("2023-04-20"))
