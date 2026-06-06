import jdatetime

PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

WEEKDAYS_FA = [
    "شنبه", "یک\u200cشنبه", "دوشنبه", "سه\u200cشنبه",
    "چهارشنبه", "پنج\u200cشنبه", "جمعه",
]

MONTHS_FA = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
]

MONTHS_HIJRI_AR = [
    "محرم", "صفر", "ربیع\u200cالاول", "ربیع\u200cالثانی",
    "جمادی\u200cالاول", "جمادی\u200cالثانی", "رجب", "شعبان",
    "رمضان", "شوال", "ذی\u200cالقعده", "ذی\u200cالحجه",
]


def to_persian_digits(text: str | int) -> str:
    """Convert Western digits (0-9) to Persian/Arabic-Indic digits (۰-۹)."""
    if isinstance(text, int):
        text = str(text)
    return text.translate(PERSIAN_DIGITS)


def is_iran_weekend(j_date: jdatetime.date) -> bool:
    """Return True if Friday (Jomeh), the weekend in Iran.

    jdatetime.weekday() mapping:
        0=Sat, 1=Sun, 2=Mon, 3=Tue, 4=Wed, 5=Thu, 6=Fri
    """
    return j_date.weekday() == 6
