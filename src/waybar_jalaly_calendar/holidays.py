import jdatetime
from hijridate import Gregorian as HijriGregorian

JALALI_HOLIDAYS: dict[tuple[int, int], str] = {
    (1, 1): "نوروز",
    (1, 2): "نوروز",
    (1, 3): "نوروز",
    (1, 4): "نوروز",
    (1, 12): "جمهوری اسلامی",
    (1, 13): "سیزده\u200cبدر",
    (3, 14): "رحلت امام خمینی",
    (3, 15): "قیام ۱۵ خرداد",
    (11, 22): "پیروزی انقلاب",
    (12, 29): "ملی\u200cشدن نفت",
}

HIJRI_HOLIDAYS: dict[tuple[int, int], str] = {
    (1, 9): "تاسوعا",
    (1, 10): "عاشورا",
    (2, 20): "اربعین",
    (2, 28): "رحلت پیامبر",
    (2, 30): "شهادت امام رضا",
    (7, 27): "مبعث",
    (8, 15): "ولادت امام مهدی",
    (9, 1): "ماه رمضان",
    (10, 1): "عید فطر",
    (10, 2): "تعطیل عید فطر",
    (12, 10): "عید قربان",
    (12, 18): "عید غدیر",
}


def get_jalali_holidays(j_date: jdatetime.date) -> list[str]:
    return [
        name
        for (m, d), name in JALALI_HOLIDAYS.items()
        if m == j_date.month and d == j_date.day
    ]


def get_hijri_holidays(j_date: jdatetime.date) -> list[str]:
    g = j_date.togregorian()
    h = HijriGregorian(g.year, g.month, g.day).to_hijri()
    return [
        name
        for (m, d), name in HIJRI_HOLIDAYS.items()
        if m == h.month and d == h.day
    ]


def days_to_nowruz(j_today: jdatetime.date) -> int:
    next_year = j_today.year
    nowruz = jdatetime.date(next_year, 1, 1)
    if j_today > nowruz:
        nowruz = jdatetime.date(next_year + 1, 1, 1)
    return (nowruz - j_today).days


def get_all_holidays(j_date: jdatetime.date) -> list[str]:
    return get_jalali_holidays(j_date) + get_hijri_holidays(j_date)
