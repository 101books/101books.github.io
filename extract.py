#!/usr/bin/env python3

import base64
import sys
import json
import re
from typing import Callable
from dataclasses import dataclass, field, replace as evolve

@dataclass
class SGF:
  initial_whites: list[str]
  initial_blacks: list[str]
  moves: list[str]

  height: int = field(init=False)
  width: int = field(init=False)

  def __post_init__(self):
    for moves in [self.initial_whites, self.initial_blacks, self.moves]:
      for m in moves:
        assert isinstance(m, str)
        assert(len(m) == 2)
        assert ord('a') <= ord(m[0]), m[0]
        assert ord(m[0]) <= ord('s'), m[0]
    initial_stones = self.initial_blacks + self.initial_whites
    self.height = max((19 - ord(m[1]) + ord('a') for m in initial_stones), default=0)
    self.width = max((1 + ord(m[0]) - ord('a') for m in initial_stones), default=0)

  def __add__(self, other: "SGF") -> "SGF":
    return SGF(
      initial_whites=self.initial_whites + other.initial_whites,
      initial_blacks=self.initial_blacks + other.initial_blacks,
      moves=self.moves + other.moves,
    )

  def map(self, transformation: Callable[[str], str]) -> "SGF":
    return SGF(
      initial_whites=list(map(transformation, self.initial_whites)),
      initial_blacks=list(map(transformation, self.initial_blacks)),
      moves=list(map(transformation, self.moves)),
    )

  def rotate(self) -> "SGF":
    return self.hflip().sflip()

  def hflip(self) -> "SGF":
    return self.map(lambda x: f"{chr(ord('a') + ord('s') - ord(x[0]))}{x[1]}")

  def sflip(self) -> "SGF":
    return self.map(lambda x: f"{x[1]}{x[0]}")

  def to_sgf(self) -> str:
    ab = "".join(f"[{m}]" for m in self.initial_blacks)
    aw = "".join(f"[{m}]" for m in self.initial_whites)
    moves = "".join(
      f";{'B' if i%2==0 else 'W'}[{m}]"
      for i, m in enumerate(self.moves)
    )
    return f"(;\nAB{ab}\nAW{aw}\n{moves})"

  def to_gnos(self, height_cutoff: int = 11) -> str:
    goban = [
        list("<(((((((((((((((((>"),
        list(r"[+++++++++++++++++]"),
        list(r"[+++++++++++++++++]"),
        list(r"[++*+++++*+++++*++]"),
        list(r"[+++++++++++++++++]"),
        list(r"[+++++++++++++++++]"),
        list(r"[+++++++++++++++++]"),
        list(r"[+++++++++++++++++]"),
        list(r"[+++++++++++++++++]"),
        list(r"[++*+++++*+++++*++]"),
        list(r"[+++++++++++++++++]"),
        list(r"[+++++++++++++++++]"),
        list(r"[+++++++++++++++++]"),
        list(r"[+++++++++++++++++]"),
        list(r"[+++++++++++++++++]"),
        list(r"[++*+++++*+++++*++]"),
        list(r"[+++++++++++++++++]"),
        list(r"[+++++++++++++++++]"),
        list(r",))))))))))))))))).")
    ]

    to_coord = lambda x: (ord(x[0]) - ord("a"), ord(x[1]) - ord("a"))
    for move in self.initial_blacks:
      col, row = to_coord(move)
      goban[row][col] = "@"
    for move in self.initial_whites:
      col, row = to_coord(move)
      goban[row][col] = "!"

    char91 = lambda c: "\\char91" if c == "[" else c
    result = "{\\gnos%\n"
    goban = goban[-height_cutoff:]
    for row in goban:
      row_str = "".join(map(char91, row))
      result += "\\line{" + row_str + "}\n"
    result += "}%"

    return result

  @staticmethod
  def from_base64(b64: str, black_first: bool) -> "SGF":
    for key in ["101222", "101333"]:
      n = base64.b64decode(b64).decode("utf-8")
      r = 0
      i = []
      for o in range(len(n)):
          i.append(chr(ord(n[o]) ^ ord(key[r])))
          r = (r + 1) % len(key)
      try:
        match eval("".join(i)):
          case [bs, ws] if black_first:
            return SGF(initial_whites=ws, initial_blacks=bs, moves=[])
          case [ws, bs]:
            return SGF(initial_whites=ws, initial_blacks=bs, moves=[])
          case _:
            assert(False)
      except Exception:
        continue
    raise ValueError()

  @staticmethod
  def from_sgf(input: str) -> "SGF":
    ab_pattern = r"AB(\[[a-z]{2}\])+"
    aw_pattern = r"AW(\[[a-z]{2}\])+"
    moves_pattern = r";[BW]\[([a-z]{2})\]"

    ab_match = re.search(ab_pattern, input)
    aw_match = re.search(aw_pattern, input)
    ab_list = re.findall(r"\[([a-z]{2})\]", ab_match.group(0)) if ab_match else []
    aw_list = re.findall(r"\[([a-z]{2})\]", aw_match.group(0)) if aw_match else []
    moves_list = re.findall(moves_pattern, input)
    return SGF(initial_whites=aw_list, initial_blacks=ab_list, moves=moves_list)

def to_goban_coordinate(move: str) -> str:
    cols = list("ABCDEFGHJKLMNOPQRST")
    col = cols[ord(move[0]) - ord('a')]
    row = 19 - ord(move[1]) + ord('a')
    return f"{col}{row}"

def main(path: str) -> None:
  assert(path.endswith(".json"))
  with open(path) as file:
    input_json = json.load(file)

  best_answer = max(input_json["answers"], key=lambda x: (x["ty"] == 1, x["st"] == 2, x["ok_count"]), default={"pts": []})
  best_answer_moves = [x["p"] for x in best_answer["pts"]]

  theproblem = SGF.from_base64(input_json["c"], input_json["blackfirst"])
  if input_json["xv"] % 3 != 0:
    theproblem = theproblem.sflip()
  theproblem = evolve(theproblem, moves=best_answer_moves)
  permutations = [
    p := theproblem,
    (p := p.rotate()),
    (p := p.rotate()),
    (p := p.rotate()),
    (p := p.sflip()),
    (p := p.rotate()),
    (p := p.rotate()),
    (p := p.rotate()),
  ]
  # the 3rd key component is a tie breaker
  theproblem = min(permutations, key=lambda x: (x.height, x.width, sorted(x.initial_blacks)))
  solution_moves = " ".join(map(to_goban_coordinate, theproblem.moves[:14]))

  stem = path.removesuffix(".json")
  with open(f"{stem}.sgf", "w") as file:
    file.write(theproblem.to_sgf() + "\n")
  with open(f"{stem}.gnos", "w") as file:
    file.write(theproblem.to_gnos() + "\n")
  with open(f"{stem}.solution", "w") as file:
    file.write(solution_moves + "\n")

if __name__ == "__main__":
  main(sys.argv[1])
