import pytest

from ja_timex.tagger import ReltimeTagger


@pytest.fixture(scope="module")
def t():
    return ReltimeTagger()


def test_reltime_type(t):
    assert t.parse("1世紀前").type == "DURATION"
    assert t.parse("1年前").type == "DURATION"
    assert t.parse("1ヶ月前").type == "DURATION"
    assert t.parse("1日前").type == "DURATION"
    assert t.parse("1時間前").type == "DURATION"
    assert t.parse("1分前").type == "DURATION"
    assert t.parse("1秒前").type == "DURATION"


def test_year(t):
    assert t.parse("1年前").value == "P1Y"
    assert t.parse("1年くらい前").value == "P1Y"
    assert t.parse("1年ぐらい前").value == "P1Y"
    assert t.parse("1年ほど前").value == "P1Y"
    assert t.parse("1年ばかり前").value == "P1Y"
    assert t.parse("1年近くまえ").value == "P1Y"

    assert t.parse("100年前").value == "P100Y"


def test_year_mod_about_prefix_and_suffix(t):
    assert t.parse("1年前").mod == "BEFORE"
    assert t.parse("1年後").mod == "AFTER"
    assert t.parse("1年近く").mod == "APPROX"
    assert t.parse("1年前後").mod == "APPROX"
    assert t.parse("1年くらい").mod == "APPROX"
    assert t.parse("1年ばかり").mod == "APPROX"


def test_month_mod_about_prefix_and_suffix(t):
    assert t.parse("1ヶ月前").mod == "BEFORE"
    assert t.parse("1ヶ月後").mod == "AFTER"
    assert t.parse("1ヶ月近く").mod == "APPROX"
    assert t.parse("1ヶ月前後").mod == "APPROX"
    assert t.parse("1ヶ月くらい").mod == "APPROX"
    assert t.parse("1ヶ月ばかり").mod == "APPROX"


def test_day_mod_about_prefix_and_suffix(t):
    assert t.parse("1日前").mod == "BEFORE"
    assert t.parse("1日後").mod == "AFTER"
    assert t.parse("1日近く").mod == "APPROX"
    assert t.parse("1日前後").mod == "APPROX"
    assert t.parse("1日くらい").mod == "APPROX"
    assert t.parse("1日ばかり").mod == "APPROX"


def test_ac_century_mod_about_prefix_and_suffix(t):
    assert t.parse("1世紀前").mod == "BEFORE"
    assert t.parse("1世紀後").mod == "AFTER"
    assert t.parse("1世紀近く").mod == "APPROX"
    assert t.parse("1世紀前後").mod == "APPROX"
    assert t.parse("1世紀くらい").mod == "APPROX"
    assert t.parse("1世紀ばかり").mod == "APPROX"


def test_week_mod_about_prefix_and_suffix(t):
    assert t.parse("1週前").mod == "BEFORE"
    assert t.parse("1週後").mod == "AFTER"
    assert t.parse("1週近く").mod == "APPROX"
    assert t.parse("1週前後").mod == "APPROX"
    assert t.parse("1週くらい").mod == "APPROX"
    assert t.parse("1週ばかり").mod == "APPROX"

    assert t.parse("1週間前").mod == "BEFORE"


def test_hour_mod_about_prefix_and_suffix(t):
    assert t.parse("1時間前").mod == "BEFORE"
    assert t.parse("1時間後").mod == "AFTER"
    assert t.parse("1時間近く").mod == "APPROX"
    assert t.parse("1時間前後").mod == "APPROX"
    assert t.parse("1時間くらい").mod == "APPROX"
    assert t.parse("1時間ばかり").mod == "APPROX"


def test_minute_mod_about_prefix_and_suffix(t):
    assert t.parse("1分前").mod == "BEFORE"
    assert t.parse("1分後").mod == "AFTER"
    assert t.parse("1分近く").mod == "APPROX"
    assert t.parse("1分前後").mod == "APPROX"
    assert t.parse("1分くらい").mod == "APPROX"
    assert t.parse("1分ばかり").mod == "APPROX"


def test_second_mod_about_prefix_and_suffix(t):
    assert t.parse("1秒前").mod == "BEFORE"
    assert t.parse("1秒後").mod == "AFTER"
    assert t.parse("1秒近く").mod == "APPROX"
    assert t.parse("1秒前後").mod == "APPROX"
    assert t.parse("1秒くらい").mod == "APPROX"
    assert t.parse("1秒ばかり").mod == "APPROX"


def test_word_before_and_after(t):
    assert t.parse("昨日").value == "P1D"
    assert t.parse("昨日").mod == "BEFORE"
    assert t.parse("一昨日").value == "P2D"
    assert t.parse("一昨日").mod == "BEFORE"
    assert t.parse("一昨々日").value == "P3D"
    assert t.parse("一昨昨日").value == "P3D"
    assert t.parse("前日").value == "P1D"
    assert t.parse("先日").value == "P1D"

    assert t.parse("明日").value == "P1D"
    assert t.parse("明日").mod == "AFTER"
    assert t.parse("明後日").value == "P2D"
    assert t.parse("明後日").mod == "AFTER"
    assert t.parse("翌日").value == "P1D"
    assert t.parse("翌々日").value == "P2D"

    assert t.parse("来週").value == "P1W"
    assert t.parse("再来週").value == "P2W"
    assert t.parse("先週").value == "P1W"
    assert t.parse("先々週").value == "P2W"

    assert t.parse("来月").value == "P1M"
    assert t.parse("再来月").value == "P2M"
    assert t.parse("先月").value == "P1M"
    assert t.parse("先々月").value == "P2M"

    assert t.parse("来年").value == "P1Y"
    assert t.parse("再来年").value == "P2Y"
    assert t.parse("おととし").value == "P2Y"
    assert t.parse("一昨年").value == "P2Y"
    # 年に関しては「先」を用いない
    assert not t.parse("先年")
    assert not t.parse("先々年")


def test_word_now(t):
    # 今日か今週かで表現する幅が異なるので、valueの値としてP0{D,W,M,Y}を取ることは表層表現を表すために必要
    assert t.parse("今日").value == "P0D"
    assert t.parse("今日").mod == "NOW"

    assert t.parse("今週").value == "P0W"
    assert t.parse("今週").mod == "NOW"

    assert t.parse("今月").value == "P0M"
    assert t.parse("今月").mod == "NOW"

    assert t.parse("今年").value == "P0Y"
    assert t.parse("今年").mod == "NOW"
