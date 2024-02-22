import random
import time
from dataclasses import dataclass
from tkinter import Canvas, Tk
from typing import Optional


@dataclass
class Line:
    x1: int
    y1: int
    x2: int
    y2: int

    def draw(self, canvas: Canvas, fill_color: str) -> None:
        canvas.create_line(self.x1, self.y1, self.x2, self.y2, fill=fill_color, width=2)
        canvas.pack()


class Window:
    def __init__(self, width: int, height: int) -> None:
        self.__root = Tk()
        self.canvas = Canvas(width=width, height=height)
        self.canvas.pack()
        self.is_running = False

        self.__root.title("Maze Solver")
        self.__root.protocol("WM_DELETE_WINDOW", self.close)

    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()

    def wait_for_close(self):
        self.is_running = True
        while self.is_running:
            self.redraw()

    def close(self):
        self.is_running = False

    def draw_line(self, line: Line, fill_color: str):
        line.draw(self.canvas, fill_color)


@dataclass
class Cell:
    top_x: int
    top_y: int
    bottom_x: int
    bottom_y: int
    win: Window
    has_left_wall: bool = True
    has_right_wall: bool = True
    has_top_wall: bool = True
    has_bottom_wall: bool = True
    visited: bool = False

    def draw(self, color: str = "black"):
        bg = "#d9d9d9"
        # left
        line = Line(self.top_x, self.top_y, self.top_x, self.bottom_y)
        line.draw(self.win.canvas, fill_color=color if self.has_left_wall else bg)

        # right
        line = Line(self.bottom_x, self.top_y, self.bottom_x, self.bottom_y)
        line.draw(self.win.canvas, fill_color=color if self.has_right_wall else bg)

        # top
        line = Line(self.top_x, self.top_y, self.bottom_x, self.top_y)
        line.draw(self.win.canvas, fill_color=color if self.has_top_wall else bg)

        # bottom
        line = Line(self.top_x, self.bottom_y, self.bottom_x, self.bottom_y)
        line.draw(self.win.canvas, fill_color=color if self.has_bottom_wall else bg)

    def draw_move(self, to_cell, undo=False):
        this_x = (self.bottom_x + self.top_x) // 2
        this_y = (self.bottom_y + self.top_y) // 2
        other_x = (to_cell.bottom_x + to_cell.top_x) // 2
        other_y = (to_cell.bottom_y + to_cell.top_y) // 2
        line = Line(this_x, this_y, other_x, other_y)
        line.draw(self.win.canvas, fill_color="gray" if undo else "red")


@dataclass
class Maze:
    x1: int
    y1: int
    num_rows: int
    num_cols: int
    cell_size_x: int
    cell_size_y: int
    win: Window
    seed: Optional[int] = None

    def __post_init__(self):
        self._create_cells()

    def _create_cells(self):
        self._cells = []
        for i in range(self.num_rows):
            top_y = self.y1 + i * self.cell_size_y
            bottom_y = self.y1 + (i + 1) * self.cell_size_y

            this_row = []
            for j in range(self.num_cols):
                top_x = self.x1 + j * self.cell_size_x
                bottom_x = self.x1 + (j + 1) * self.cell_size_x

                cell = Cell(top_x, top_y, bottom_x, bottom_y, self.win)
                this_row.append(cell)

            self._cells.append(this_row)

        # create maze by breaking walls
        self._break_entrance_and_exit()
        self._break_walls_r(0, 0)
        self._reset_cells_visited()

    def _draw_cell(self, i, j):
        self._cells[i][j].draw()
        self._animate()

    def _animate(self):
        self.win.redraw()
        time.sleep(0.05)

    def _break_entrance_and_exit(self):
        # entrance at top of top left
        self._cells[0][0].has_top_wall = False

        # exit at bottom of bottom right
        self._cells[self.num_rows - 1][self.num_cols - 1].has_bottom_wall = False

    def _break_walls_r(self, i, j):
        self._cells[i][j].visited = True
        while True:
            to_visit = []
            neighbors = ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1))

            for test_i, test_j in neighbors:
                if test_i < 0 or test_j < 0:
                    continue
                if test_i >= self.num_rows or test_j >= self.num_cols:
                    continue

                if not self._cells[test_i][test_j].visited:
                    to_visit.append((test_i, test_j))

            if not to_visit:
                self._draw_cell(i, j)
                return

            new_i, new_j = random.choice(to_visit)

            # break down walls inbetween
            if new_j > j:
                self._cells[i][j].has_right_wall = False
                self._cells[new_i][new_j].has_left_wall = False
            elif new_j < j:
                self._cells[i][j].has_left_wall = False
                self._cells[new_i][new_j].has_right_wall = False
            elif new_i > i:
                self._cells[i][j].has_bottom_wall = False
                self._cells[new_i][new_j].has_top_wall = False
            elif new_i < i:
                self._cells[i][j].has_top_wall = False
                self._cells[new_i][new_j].has_bottom_wall = False

            self._break_walls_r(new_i, new_j)

    def _reset_cells_visited(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self._cells[i][j].visited = False

    def solve(self) -> bool:
        return self.solve_r(0, 0)

    def solve_r(self, i, j) -> bool:
        self._animate()
        this_cell = self._cells[i][j]
        this_cell.visited = True

        if i == self.num_rows - 1 and j == self.num_cols - 1:
            return True

        neighbors = (
            (i - 1, j, this_cell.has_top_wall),
            (i + 1, j, this_cell.has_bottom_wall),
            (i, j - 1, this_cell.has_left_wall),
            (i, j + 1, this_cell.has_right_wall),
        )
        for test_i, test_j, wall in neighbors:
            if test_i < 0 or test_j < 0:
                continue
            if test_i >= self.num_rows or test_j >= self.num_cols:
                continue

            next_cell = self._cells[test_i][test_j]
            if not next_cell.visited:
                if not wall:
                    this_cell.draw_move(next_cell)
                    if not self.solve_r(test_i, test_j):
                        this_cell.draw_move(next_cell, undo=True)
                    else:
                        return True
        return False


def main():
    win_width = 800
    win_height = 600
    win = Window(win_width, win_height)

    top_x = 5
    top_y = 5

    num_rows = 20
    num_cols = 30

    cell_width = (win_width - top_x) // num_cols
    cell_height = (win_height - top_y) // num_rows

    maze = Maze(top_x, top_y, num_rows, num_cols, cell_width, cell_height, win)
    maze.solve()
    win.wait_for_close()


if __name__ == "__main__":
    main()
