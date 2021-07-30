import pytest

from ja_timex.tagger.abstime_tagger import AbstimeTagger


@pytest.fixture(scope="module")
def t():
    return AbstimeTagger()


def test_normal_date(t):
    assert t.parse("2021年7月18日").value == "2021-07-18"
    assert t.parse("2021/7/18").value == "2021-07-18"
    assert t.parse("2021-7-18").value == "2021-07-18"
    assert t.parse("2021.7.18").value == "2021-07-18"
    assert t.parse("2021・7・18").value == "2021-07-18"
    assert t.parse("2021,7,18").value == "2021-07-18"

    assert t.parse("2021年7月").value == "2021-07-XX"
    assert t.parse("7月18日").value == "XXXX-07-18"
    assert t.parse("2021年").value == "2021-XX-XX"
    assert t.parse("7月").value == "XXXX-07-XX"
    assert t.parse("18日").value == "XXXX-XX-18"

    assert t.parse("2021年/7月/18日").value == "2021-07-18"
    assert t.parse("2021/7").value == "2021-07-XX"
    assert t.parse("7/18").value == "XXXX-07-18"
    assert t.parse("2021年/7月").value == "2021-07-XX"
    assert t.parse("2021/7月").value == "2021-07-XX"
    assert t.parse("2021年/7").value == "2021-07-XX"


def test_normal_date_multiple_detected(t):
    # 年/月か月/日かが判定できなく、複数取得されるパターン
    # 基本的には月/日を優先する
    assert t.parse("7/8").value == "XXXX-07-08"
    assert t.parse("12/10").value == "XXXX-12-10"  # 2012年10月とも取れる
    assert t.parse("09/12").value == "XXXX-09-12"  # 2009年12月とも取れる

    # 月が取る値の範囲外の場合は年になる
    assert t.parse("2021/07").value == "2021-07-XX"
    assert t.parse("13/8").value == "0013-08-XX"  # :TODO どこかで2013に変換したい


def test_normal_date_seireki(t):
    assert t.parse("西暦2021年").value == "2021-XX-XX"
    assert t.parse("西暦2021年7月").value == "2021-07-XX"
    assert t.parse("西暦2021/7/18").value == "2021-07-18"
    assert t.parse("西暦2021/7").value == "2021-07-XX"


def test_normal_date_wareki(t):
    assert t.parse("令和3年").value == "2021-XX-XX"
    assert t.parse("令和03年").value == "2021-XX-XX"
    assert t.parse("令和3年7月18日").value == "2021-07-18"

    # 平成33年は存在しないが、元号が変わる前の未来の日付の表記などに存在する
    assert t.parse("平成33年").value == "2021-XX-XX"

    # 元年
    assert t.parse("令和元年").value == "2019-XX-XX"
    assert t.parse("令和1年").value == "2019-XX-XX"
    assert t.parse("平成元年").value == "1989-XX-XX"
    assert t.parse("平成1年").value == "1989-XX-XX"

    # 英字表記
    assert t.parse("R3年7月18日").value == "2021-07-18"
    assert t.parse("Ｒ3/7/18").value == "2021-07-18"

    # その他の元号
    assert t.parse("平成31年").value == "2019-XX-XX"
    assert t.parse("昭和64年").value == "1989-XX-XX"
    assert t.parse("大正15年").value == "1926-XX-XX"
    assert t.parse("明治45年").value == "1912-XX-XX"
    assert t.parse("大化1年").value == "0645-XX-XX"

    # 存在しない元号と年
    assert t.parse("歯姫3年") is None
    assert t.parse("飛鳥時代3年") is None
    assert t.parse("令和0年") is None
    assert t.parse("令和00年") is None
    assert t.parse("令和-3年") is None


def test_normal_date_invalid(t):
    # 2013年13月とも13月13日とも言えない場合
    assert t.parse("13/13") is None


def test_weekday(t):
    assert t.parse("月曜日").value == "XXXX-WXX-1"
    assert t.parse("火曜日").value == "XXXX-WXX-2"
    assert t.parse("水曜日").value == "XXXX-WXX-3"
    assert t.parse("木曜日").value == "XXXX-WXX-4"
    assert t.parse("金曜日").value == "XXXX-WXX-5"
    assert t.parse("土曜日").value == "XXXX-WXX-6"
    assert t.parse("日曜日").value == "XXXX-WXX-7"

    assert t.parse("月").value == "XXXX-WXX-1"
    assert t.parse("月曜").value == "XXXX-WXX-1"
    assert t.parse("(月曜日)").value == "XXXX-WXX-1"
    assert t.parse("(月)").value == "XXXX-WXX-1"


def test_season(t):
    assert t.parse("春").value == "XXXX-SP"
    assert t.parse("夏").value == "XXXX-SU"
    assert t.parse("秋").value == "XXXX-FA"
    assert t.parse("冬").value == "XXXX-WI"

    assert t.parse("2021春").value == "2021-SP"
    assert t.parse("2021年春").value == "2021-SP"
    assert t.parse("2021/春").value == "2021-SP"

    # def test_quarter(t):
    assert t.parse("Q1").value == "XXXX-Q1"
    assert t.parse("Q2").value == "XXXX-Q2"
    assert t.parse("Q3").value == "XXXX-Q3"
    assert t.parse("Q4").value == "XXXX-Q4"
    assert t.parse("Q1").value == "XXXX-Q1"
    assert t.parse("第1四半期").value == "XXXX-Q1"

    assert t.parse("Q5") is None
    assert t.parse("10Q") is None
    assert t.parse("Q1Q") is None
    assert t.parse("第1四半") is None
    assert t.parse("1四半期") is None


def test_fiscal_year(t):
    assert t.parse("2021年度").value == "FY2021"

    # 西暦で2,3桁年度は表現しない
    assert t.parse("132年度") is None
    assert t.parse("32年度") is None


# def test_fiscal_year_wareki(t):
#     assert t.parse("令和3年度").value == "FYR03"


def test_ac_century(t):
    assert t.parse("1世紀").value == "00XX"  # 西暦1年から西暦100年
    assert t.parse("9世紀").value == "08XX"  # 西暦801年から西暦900年
    assert t.parse("11世紀").value == "10XX"  # 西暦1001年から西暦1100年
    assert t.parse("21世紀").value == "20XX"  # 西暦2001年から西暦2100年


def test_bc_year(t):
    assert t.parse("紀元前1年").value == "BC0001"
    assert t.parse("紀元前202年").value == "BC0202"
    assert t.parse("紀元前2000年").value == "BC2000"


def test_bc_century(t):
    assert t.parse("紀元前1世紀").value == "BC00XX"
    assert t.parse("紀元前2世紀").value == "BC01XX"
    assert t.parse("紀元前21世紀").value == "BC20XX"


def test_time(t):
    assert t.parse("23時59分59秒").value == "T23-59-59"
    assert t.parse("23時59分").value == "T23-59-XX"
    assert t.parse("59分59秒").value == "TXX-59-59"
    assert t.parse("23時").value == "T23-XX-XX"
    assert t.parse("59分").value == "TXX-59-XX"
    assert t.parse("59秒").value == "TXX-XX-59"

    assert t.parse("00時00分00秒").value == "T00-00-00"
    assert t.parse("0時0分0秒").value == "T00-00-00"

    assert t.parse("23時59秒") is None
    assert t.parse("23.5時59秒") is None

    assert t.parse("23:59:59").value == "T23-59-59"
    # HH:MMとMM:SSが考えられるパターンでは前者を優先する
    assert t.parse("23:59").value == "T23-59-XX"
    assert t.parse("59:59").value == "TXX-59-59"  # 24時を大幅に超えてMM:SSだと考えられる場合

    # 正確には時間の範囲は[0,24]だが、深夜から翌日に掛けて25以上の値を取る場合がある
    # 日付表現を伴わない場合もあるので、＠valueや@valueFromSurfaceでは日付の正規化は行わない
    assert t.parse("25時30分").value == "T25-30-XX"
    assert t.parse("29時").value == "T29-XX-XX"
    # 時刻表現として30時以上はないものとする
    assert t.parse("30時") is None


def test_time_ampm(t):
    # 変換の正しさ
    assert t.parse("12:10AM").value == "T00-10-XX"
    assert t.parse("1:10AM").value == "T01-10-XX"
    assert t.parse("11:10AM").value == "T11-10-XX"
    assert t.parse("12:10PM").value == "T12-10-XX"
    assert t.parse("1:10PM").value == "T13-10-XX"
    assert t.parse("11:10PM").value == "T23-10-XX"

    # 対応するprefix/suffixの正しさ
    assert t.parse("午前12時10分").value == "T00-10-XX"
    assert t.parse("午後11時10分").value == "T23-10-XX"
    assert t.parse("AM12時10分").value == "T00-10-XX"
    assert t.parse("PM11時10分").value == "T23-10-XX"
    assert t.parse("am12時10分").value == "T00-10-XX"
    assert t.parse("pm11時10分").value == "T23-10-XX"
    assert t.parse("12:10AM").value == "T00-10-XX"
    assert t.parse("11:10PM").value == "T23-10-XX"
    assert t.parse("12:10 AM").value == "T00-10-XX"
    assert t.parse("11:10 PM").value == "T23-10-XX"

    # 時間のみ
    assert t.parse("午前12時").value == "T00-XX-XX"
    assert t.parse("午後11時").value == "T23-XX-XX"

    # 本来は午前午後/AMPMの12 Hour Clockの記載で0時は存在しないが、慣例として24 Hour Clockでの0時に割り当てる
    assert t.parse("午前0時").value == "T00-XX-XX"
    assert t.parse("00:10 AM").value == "T00-10-XX"


def test_timex_type(t):
    assert t.parse("2021年7月18日").type == "DATE"
    assert t.parse("月曜日").type == "DATE"
    assert t.parse("春").type == "DATE"
    assert t.parse("Q1").type == "DATE"
    assert t.parse("2021年度").type == "DATE"
    assert t.parse("1世紀").type == "DATE"
    assert t.parse("紀元前1年").type == "DATE"
    assert t.parse("紀元前1世紀").type == "DATE"
    assert t.parse("1時2分3秒").type == "TIME"
