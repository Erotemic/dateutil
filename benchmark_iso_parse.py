from line_profiler import profile

# profile.enable()
# profile.show_config['details'] = True
# profile.show_config['summarize'] = True


def random_time(rng):
    import datetime as datetime_mod
    from datetime import datetime as datetime_cls
    min_ts = datetime_cls(1, 1, 2, 0, 0).timestamp()
    max_ts = datetime_cls.max.timestamp()
    ts = rng.randint(int(min_ts), int(max_ts))
    tz = datetime_mod.timezone.utc
    time = datetime_cls.fromtimestamp(ts, tz=tz)
    return time


def random_time_strings(num_timestamps, rng):
    for _ in range(num_timestamps):
        time = random_time(rng)
        yield time.isoformat()


@profile
def main():
    from dateutil import parser as date_parser
    import timerit
    import random

    rng = random.Random(0)

    num_per_iter = 100
    ti = timerit.Timerit(1000, bestof=10, verbose=3)

    # Benchmark the original get_token code
    date_parser._parser._timelex.get_token = date_parser._timelex.get_token_original
    for timer in ti.reset('original'):
        timestrs = list(random_time_strings(num_per_iter, rng))
        with timer:
            for timestr in timestrs:
                date_parser.parse(timestr)

    # Benchmark the alternative get_token code
    date_parser._parser._timelex.get_token = date_parser._timelex.get_token_alternative
    for timer in ti.reset('alternative'):
        timestrs = list(random_time_strings(num_per_iter, rng))
        with timer:
            for timestr in timestrs:
                date_parser.parse(timestr)

    from timerit.relative import Relative
    percent_faster = Relative.percent_faster(ti.measures['min']['alternative'], ti.measures['min']['original'])
    print(f'min(percent_faster)={percent_faster}%')
    percent_faster = Relative.percent_faster(ti.measures['mean']['alternative'], ti.measures['mean']['original'])
    print(f'mean(percent_faster)={percent_faster}%')

if __name__ == '__main__':
    """
    CommandLine:
        LINE_PROFILE=1 python benchmark_iso_parse.py
        LINE_PROFILE=0 python benchmark_iso_parse.py
    """
    main()
