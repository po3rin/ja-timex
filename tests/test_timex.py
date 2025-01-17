import pendulum
import pytest

from ja_timex.tag import TIMEX
from ja_timex.timex import TimexParser


@pytest.fixture(scope="module")
def p():
    return TimexParser()


@pytest.fixture(scope="module")
def p_ref():
    return TimexParser(reference=pendulum.datetime(2021, 7, 18, tz="Asia/Tokyo"))


def test_abstime(p):
    timexes = p.parse("2021年7月18日")
    assert len(timexes) == 1
    assert type(timexes[0]) == TIMEX
    assert timexes[0].value == "2021-07-18"

    timexes = p.parse("2021回目の7月18日")
    assert len(timexes) == 1
    assert type(timexes[0]) == TIMEX
    assert timexes[0].value == "XXXX-07-18"


def test_abstime_partial_pattern_of_number_expression(p):
    # 部分的な表現はなるべく取得しない

    timexes = p.parse("13/13は1です")
    assert len(timexes) == 1
    # 3/13を取得しないが、13/1は取得されてしまう
    # 「今月8日」といった直後に続く数字があるため


def test_tid_is_modified_in_parsing(p):
    timexes = p.parse("彼は2008年4月から週に3回ジョギングを1時間行ってきた")

    assert timexes[0].tid == "t0"
    assert timexes[1].tid == "t1"
    assert timexes[2].tid == "t2"


def test_ignore_number_normalize(p):
    # 一を1と変換しない。可読性のために、reltimeのPatternでも漢数字で扱う
    timexes = p.parse("一昨年と一昨日は言うのに一昨月とは言わないのは何故か")

    assert len(timexes) == 2
    assert timexes[0].value == "P2Y"
    assert timexes[1].value == "P2D"

    timexes = p.parse("一昨昨日と一昨々日")
    assert len(timexes) == 2
    assert timexes[0].value == "P3D"
    assert timexes[1].value == "P3D"


def test_every_year_and_month(p):
    timexes = p.parse("毎年6月から8月にかけて")

    assert len(timexes) == 3
    assert timexes[0].value == "P1Y"
    assert timexes[0].type == "SET"
    assert timexes[1].value == "XXXX-06-XX"
    assert timexes[1].type == "DATE"
    assert timexes[2].value == "XXXX-08-XX"
    assert timexes[2].type == "DATE"


def test_morning_evening(p):
    timexes = TimexParser().parse("朝9時スタートです。")
    assert len(timexes) == 1
    assert timexes[0].value == "T09-XX-XX"
    assert timexes[0].type == "TIME"
    assert timexes[0].text == "朝9時"

    timexes = TimexParser().parse("今夜9時スタートです。")
    assert len(timexes) == 1
    assert timexes[0].value == "T21-XX-XX"
    assert timexes[0].type == "TIME"
    assert timexes[0].text == "今夜9時"


def test_reference_datetime_without_reference(p):
    timexes = p.parse("2021年7月18日")
    assert timexes[0].reference is None


def test_reference_datetime(p_ref):
    # すべての時間情報表現にreference datetimeが付与される
    timexes = p_ref.parse("2021年7月18日")
    assert timexes[0].type == "DATE"
    assert timexes[0].reference == pendulum.datetime(2021, 7, 18, tz="Asia/Tokyo")

    timexes = p_ref.parse("12時59分")
    assert timexes[0].type == "TIME"
    assert timexes[0].reference == pendulum.datetime(2021, 7, 18, tz="Asia/Tokyo")

    timexes = p_ref.parse("1時間前")
    assert timexes[0].type == "DURATION"
    assert timexes[0].reference == pendulum.datetime(2021, 7, 18, tz="Asia/Tokyo")

    timexes = p_ref.parse("週1回")
    assert timexes[0].type == "SET"
    assert timexes[0].reference == pendulum.datetime(2021, 7, 18, tz="Asia/Tokyo")


def test_reference_datetime_default_year(p):
    reference_past = pendulum.datetime(2010, 7, 18, tz="Asia/Tokyo")

    timexes = TimexParser(reference=reference_past).parse("2021年12月30日")
    assert timexes[0].to_datetime() == pendulum.datetime(2021, 12, 30, tz="Asia/Tokyo")

    # 年を補完
    timexes = TimexParser(reference=reference_past).parse("12月30日")
    assert timexes[0].to_datetime() == pendulum.datetime(2010, 12, 30, tz="Asia/Tokyo")

    # 年を補完
    timexes = TimexParser(reference=reference_past).parse("12月")
    assert timexes[0].to_datetime() == pendulum.datetime(2010, 12, 1, tz="Asia/Tokyo")

    # 年と月を補完
    timexes = TimexParser(reference=reference_past).parse("30日")
    assert timexes[0].to_datetime() == pendulum.datetime(2010, 7, 30, tz="Asia/Tokyo")

    # 2021年でもreferenceのmonth/dayとは限らないので、補完しない
    timexes = TimexParser(reference=reference_past).parse("2021年")
    assert timexes[0].to_datetime() == pendulum.datetime(2021, 1, 1, tz="Asia/Tokyo")

    timexes = TimexParser(reference=reference_past).parse("12時59分")
    assert timexes[0].to_datetime() == pendulum.datetime(2010, 7, 18, 12, 59, tz="Asia/Tokyo")


def test_reference_datetime_time(p_ref):
    timexes = p_ref.parse("12時59分1秒")
    assert timexes[0].to_datetime() == pendulum.datetime(2021, 7, 18, 12, 59, 1, tz="Asia/Tokyo")

    timexes = p_ref.parse("12時59分")
    assert timexes[0].to_datetime() == pendulum.datetime(2021, 7, 18, 12, 59, 0, tz="Asia/Tokyo")

    timexes = p_ref.parse("23時")
    assert timexes[0].to_datetime() == pendulum.datetime(2021, 7, 18, 23, 0, 0, tz="Asia/Tokyo")

    # 翌日の0時,1時
    timexes = p_ref.parse("24時")
    assert timexes[0].to_datetime() == pendulum.datetime(2021, 7, 19, 0, 0, 0, tz="Asia/Tokyo")

    timexes = p_ref.parse("25時")
    assert timexes[0].to_datetime() == pendulum.datetime(2021, 7, 19, 1, 0, 0, tz="Asia/Tokyo")


def test_reference_datetime_duration(p_ref):
    timexes = p_ref.parse("1秒後")
    assert timexes[0].to_datetime() == pendulum.datetime(2021, 7, 18, 0, 0, 1, tz="Asia/Tokyo")
    timexes = p_ref.parse("1分後")
    assert timexes[0].to_datetime() == pendulum.datetime(2021, 7, 18, 0, 1, 0, tz="Asia/Tokyo")
    timexes = p_ref.parse("1時間後")
    assert timexes[0].to_datetime() == pendulum.datetime(2021, 7, 18, 1, 0, 0, tz="Asia/Tokyo")
    timexes = p_ref.parse("1日後")
    assert timexes[0].to_datetime() == pendulum.datetime(2021, 7, 19, 0, 0, 0, tz="Asia/Tokyo")
    timexes = p_ref.parse("2ヶ月後")
    assert timexes[0].to_datetime() == pendulum.datetime(2021, 9, 18, 0, 0, 0, tz="Asia/Tokyo")
    timexes = p_ref.parse("10年後")
    assert timexes[0].to_datetime() == pendulum.datetime(2031, 7, 18, 0, 0, 0, tz="Asia/Tokyo")

    timexes = p_ref.parse("1秒前")
    assert timexes[0].to_datetime() == pendulum.datetime(2021, 7, 17, 23, 59, 59, tz="Asia/Tokyo")
    timexes = p_ref.parse("1分前")
    assert timexes[0].to_datetime() == pendulum.datetime(2021, 7, 17, 23, 59, 0, tz="Asia/Tokyo")
    timexes = p_ref.parse("1時間前")
    assert timexes[0].to_datetime() == pendulum.datetime(2021, 7, 17, 23, 0, 0, tz="Asia/Tokyo")
    timexes = p_ref.parse("1日前")
    assert timexes[0].to_datetime() == pendulum.datetime(2021, 7, 17, 0, 0, 0, tz="Asia/Tokyo")
    timexes = p_ref.parse("2ヶ月前")
    assert timexes[0].to_datetime() == pendulum.datetime(2021, 5, 18, 0, 0, 0, tz="Asia/Tokyo")
    timexes = p_ref.parse("10年前")
    assert timexes[0].to_datetime() == pendulum.datetime(2011, 7, 18, 0, 0, 0, tz="Asia/Tokyo")
