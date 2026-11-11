#!/usr/bin/env python3

import base64
import glob
import os
import sys
import json
import re
from typing import Callable, Any
from dataclasses import dataclass, field, replace as evolve
from pathlib import Path

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
                assert len(m) == 2
                assert ord("a") <= ord(m[0]), m[0]
                assert ord(m[0]) <= ord("s"), m[0]
        initial_stones = self.initial_blacks + self.initial_whites
        self.height = max((19 - ord(m[1]) + ord("a") for m in initial_stones), default=0)
        self.width = max((1 + ord(m[0]) - ord("a") for m in initial_stones), default=0)

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
        moves = "".join(f";{'B' if i%2==0 else 'W'}[{m}]" for i, m in enumerate(self.moves))
        return f"(;\nAB{ab}\nAW{aw}\n{moves})"

    def to_gnos(self, height_cutoff: int = 11, solution: bool = False,
                eliminated: bool = False) -> str:
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
            list(r",)))))))))))))))))."),
        ]

        to_coord = lambda x: (ord(x[0]) - ord("a"), ord(x[1]) - ord("a"))
        for move in self.initial_blacks:
            col, row = to_coord(move)
            goban[row][col] = "@"
        for move in self.initial_whites:
            col, row = to_coord(move)
            goban[row][col] = "!"

        # Keep the first stone shown at each intersection, even if it is
        # captured later. Subsequent moves there refer back to its number.
        numbered = {}
        initial_labels = {}
        annotations = []
        def labeled_stone(label, black):
            base = "@" if black else "!"
            color = "white" if black else "black"
            return ("{" + base + r"\llap{\makebox[12pt]{"
                    r"\raisebox{3pt}{\normalfont\footnotesize"
                    rf"\color{{{color}}}{label}" + "}}}}")

        def stone(number):
            return labeled_stone(number, number % 2 == 1)

        # An eliminated problem has no solution to show, so its diagram is
        # the plain problem board; the marker lives next to the number.
        if solution and not eliminated:
            for number, move in enumerate(self.moves[:14], 1):
                col, row = to_coord(move)
                if move in numbered:
                    annotations.append([stone(number), r"\gnosEmptyLbl{\normalfont in}", stone(numbered[move])])
                elif move in self.initial_blacks or move in self.initial_whites:
                    if move not in initial_labels:
                        initial_labels[move] = len(initial_labels) + 1
                    label = initial_labels[move]
                    letter = chr(ord('A') + label - 1)
                    letter_stone = labeled_stone(letter, move in self.initial_blacks)
                    annotations.append([stone(number), r"\gnosEmptyLbl{\normalfont in}", letter_stone])
                    goban[row][col] = letter_stone
                else:
                    numbered[move] = number
                    goban[row][col] = stone(number)

        def place_annotations(width):
            board = [row.copy() for row in goban]
            occupied = {to_coord(move) for move in
                        self.initial_blacks + self.initial_whites + self.moves[:14]}
            top = max(0, 19 - height_cutoff)
            columns = range(width - 3, -1, -1)

            def clear(col, row):
                return all((x, row) not in occupied for x in range(col, col + 3))

            # Align the three-cell annotations at the top right of the goban.
            # Crowded positions use the rightmost free run on successive rows
            # rather than overwriting any problem or solution stone.
            slots = []
            for col in columns:
                if all(clear(col, row) for row in range(top, top + len(annotations))):
                    slots = [(col, row) for row in range(top, top + len(annotations))]
                    break
            if not slots:
                for row in range(top, 19):
                    for col in columns:
                        if clear(col, row):
                            slots.append((col, row))
                            break
            if len(slots) < len(annotations):
                raise ValueError("No empty goban space for solution annotations")
            for (col, row), annotation in zip(slots, annotations):
                board[row][col:col + 3] = annotation
            return board
        if solution and annotations:
            narrow = place_annotations(12)
            wide = place_annotations(19)
        char91 = lambda c: "\\char91" if c == "[" else c
        result = "{\\gnos\\gnosIntWd=12pt%\n" if solution else "{\\gnos%\n"
        for row_number in range(max(0, 19 - height_cutoff), 19):
            separator = r"\allowbreak" if solution else ""
            row = separator.join(map(char91, goban[row_number]))
            if solution and annotations:
                # Mixed stone fonts and text need explicit cell breakpoints
                # for the original \truncate-based renderer.
                small = r"\allowbreak".join(map(char91, narrow[row_number]))
                large = r"\allowbreak".join(map(char91, wide[row_number]))
                row = (small if small == large else
                       r"\ifdim\diagramwidth>150pt " + large + r"\else " + small + r"\fi")
            result += "\\line{" + row + "}\n"
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
                        assert False
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


def process_one(path: str) -> None:
    assert path.endswith(".json")
    with open(path) as file:
        input_json = json.load(file)

    def best_answer_key(x: dict[str, Any]) -> tuple:
        return (
            x["ty"] == 1,
            x["st"] == 2,
            x["ok_count"],
            -x["error_count"],
            -x["bad_count"],
            str(x),  # tie breaker
        )

    best_answer = max(input_json["answers"], key=best_answer_key, default={"pts": []})
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
    # last key component is a tie breaker
    theproblem = min(permutations, key=lambda x: (x.height, x.width, sorted(x.initial_blacks)))

    stem = path.removesuffix(".json")
    eliminated = input_json["status"] == 1
    with open(f"{stem}.sgf", "w") as file:
        file.write(theproblem.to_sgf() + "\n")
    with open(f"{stem}.gnos", "w") as file:
        file.write(theproblem.to_gnos(eliminated=eliminated) + "\n")
    # An eliminated problem gets no solution overlay; its diagram only
    # carries a note that the renderer prints next to the problem number.
    note = "\\solutionnote{eliminated}%\n" if eliminated else ""
    with open(f"{stem}.solution", "w") as file:
        file.write(note + theproblem.to_gnos(solution=True, eliminated=eliminated) + "\n")


def main(paths: list[str]) -> None:
    for path in paths:
        process_one(path)


if __name__ == "__main__":
    main(sys.argv[1:])
