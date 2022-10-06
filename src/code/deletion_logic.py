import datetime

from typing import Iterator


class DeleteManager:

  def __init__(self, rules: dict[datetime.timedelta, int]) -> None:
    self._rules = rules

  def _required_intervals(
      self, now: datetime.datetime
  ) -> list[tuple[datetime.datetime, datetime.datetime]]:
    result: list[tuple[datetime.datetime, datetime.datetime]] = []
    for width, count in self._rules.items():
      for index in range(count):
        result.append((now - (index + 1) * width, now - index * width))
    return result

  def get_deletes(
      self, now: datetime.datetime, records: list[tuple[datetime.datetime, str]]
  ) -> Iterator[tuple[datetime.datetime, str]]:
    # We want at least one per each interval.
    intervals = self._required_intervals(now)

    prev_time = None

    for time, fname in records:

      # Ensure ascending order.
      if prev_time is not None and prev_time > time:
        raise ValueError(f'Records not in order, {prev_time}, {time}')
      else:
        prev_time = time

      # Ensure times are in past.
      if now < time:
        raise ValueError(f'Record time is in the future, {time} > {now}')

      keep = False
      remaining_intervals: list[tuple[datetime.datetime,
                                      datetime.datetime]] = []
      for interval in intervals:
        if interval[0] < time <= interval[1]:
          keep = True
        else:
          remaining_intervals.append(interval)
      intervals = remaining_intervals
      if keep:
        continue
      yield time, fname
