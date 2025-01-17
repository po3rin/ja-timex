import re

from ja_timex.pattern.place import Pattern, Place
from ja_timex.tag import TIMEX


def parse_p(re_match: re.Match, pattern: Pattern) -> TIMEX:
    args = re_match.groupdict()
    span = re_match.span()

    if args.get("half_suffix"):
        value_suffix = ".5"
    else:
        value_suffix = ""

    # 日付を表す持続時間表現の場合
    value = "P"
    if "year" in args:
        value += args["year"] + value_suffix + "Y"
    if "month" in args:
        value += args["month"] + value_suffix + "M"
    if "week" in args:
        value += args["week"] + value_suffix + "W"
    if "day" in args:
        value += args["day"] + value_suffix + "D"

    return TIMEX(
        type="DURATION",
        value=value,
        text=re_match.group(),
        parsed=args,
        span=span,
        pattern=pattern,
    )


def parse_pt(re_match: re.Match, pattern: Pattern) -> TIMEX:
    args = re_match.groupdict()
    span = re_match.span()

    # 時間を表す持続時間表現の場合

    if args.get("half_suffix"):
        value_suffix = ".5"
    else:
        value_suffix = ""

    value = "PT"
    if "hour" in args:
        value += args["hour"] + value_suffix + "H"
    if "minute" in args:
        value += args["minute"] + value_suffix + "M"
    if "second" in args:
        value += args["second"] + value_suffix + "S"
    if "second_with_ms" in args:
        if "秒" in args["second_with_ms"]:
            value += args["second_with_ms"].replace("秒", ".") + "S"
        else:
            value += args["second_with_ms"] + value_suffix + "S"

    return TIMEX(
        type="DURATION",
        value=value,
        text=re_match.group(),
        parsed=args,
        span=span,
        pattern=pattern,
    )


p = Place()

patterns = []


patterns += [
    # P
    Pattern(
        re_pattern=f"{p.year}年(間)?",
        parse_func=parse_p,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.month}[ヶ|か|カ|ケ|箇]?月(間)?",
        parse_func=parse_p,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.week}週(間)?",
        parse_func=parse_p,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.day}日(間)?",
        parse_func=parse_p,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.year}年{p.month}[ヶ|か|カ|ケ|箇]月(間)?",
        parse_func=parse_p,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.year}年{p.month}[ヶ|か|カ|ケ|箇]月{p.day}日(間)?",
        parse_func=parse_p,
        option={},
    ),
    # PT
    Pattern(
        re_pattern=f"{p.hour}時間",
        parse_func=parse_pt,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.minute}分(間)?",
        parse_func=parse_pt,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.second}秒(間)?",
        parse_func=parse_pt,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.second_with_ms}",
        parse_func=parse_pt,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.hour}時間{p.minute}分(間)?",
        parse_func=parse_pt,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.hour}時間{p.minute}分{p.second}秒(間)?",
        parse_func=parse_pt,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.minute}分{p.second}秒(間)?",
        parse_func=parse_pt,
        option={},
    ),
]

patterns += [
    # P
    Pattern(
        re_pattern=f"{p.year}年{p.half_suffix}",
        parse_func=parse_p,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.month}[ヶ|か|カ|ケ|箇]?月{p.half_suffix}",
        parse_func=parse_p,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.week}週(間)?{p.half_suffix}",
        parse_func=parse_p,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.day}日{p.half_suffix}",
        parse_func=parse_p,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.hour}時間{p.half_suffix}",
        parse_func=parse_pt,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.minute}分{p.half_suffix}",
        parse_func=parse_pt,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.second}秒{p.half_suffix}",
        parse_func=parse_pt,
        option={},
    ),
]
