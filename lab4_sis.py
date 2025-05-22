import tkinter as tk
from tkinter import messagebox
import numpy as np


class LinearProgrammingSolver:
    def __init__(self, root):
        self.root = root
        self.root.title("Графический метод решения ЗЛП - Вариант 6")

        # Параметры интерфейса
        self.canvas_width = 800
        self.canvas_height = 800
        self.margin = 80
        self.scale = 40
        self.grid_size = 10

        # Создание холста
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack()

        # Задачи из варианта 6
        self.problems = {
            "a": {
                "objective": "x₁ + 3x₂ → max",
                "constraints": [
                    (1, 2, 9, '<='),
                    (1, 4, 8, '<='),
                    (2, 1, 3, '>='),
                    (1, 0, 0, '>='),  # x₁ ≥ 0
                    (0, 1, 0, '>=')  # x₂ ≥ 0
                ],
                "obj_func": (1, 3),
                "type": "max"
            },
            "b": {
                "objective": "7x₁ + 14x₂ → min",
                "constraints": [
                    (1, 7, 14, '<='),
                    (3, 1, 16, '<='),
                    (1, 2, 2, '>='),
                    (1, 0, 0, '>='),
                    (0, 1, 0, '>=')
                ],
                "obj_func": (7, 14),
                "type": "min"
            },
            "d": {
                "objective": "2x₁ + 5x₂ → max",
                "constraints": [
                    (1, 2, 8, '>='),
                    (1, 1, 5, '>='),
                    (1, 3, 4, '>='),
                    (1, 0, 0, '>='),
                    (0, 1, 0, '>=')
                ],
                "obj_func": (2, 5),
                "type": "max"
            },
            "f": {
                "objective": "x₁ + 6x₂ → min",
                "constraints": [
                    (5, 2, 10, '<='),
                    (6, 1, 6, '<='),
                    (2, 1, 11, '>='),
                    (1, 0, 0, '>='),
                    (0, 1, 0, '>=')
                ],
                "obj_func": (1, 6),
                "type": "min"
            }
        }

        # Элементы управления
        self.setup_ui()
        self.current_problem = "a"
        self.draw_axes()

    def setup_ui(self):
        """Настройка интерфейса"""
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X)

        # Выбор задачи
        problem_frame = tk.LabelFrame(control_frame, text="Выберите задачу")
        problem_frame.pack(side=tk.LEFT, padx=5)

        self.problem_var = tk.StringVar(value="a")
        for key in self.problems:
            text = f"{key}) {self.problems[key]['objective']}"
            tk.Radiobutton(problem_frame, text=text, variable=self.problem_var,
                           value=key, command=self.update_problem).pack(anchor=tk.W)

        # Кнопка решения
        tk.Button(control_frame, text="Решить", command=self.solve_problem).pack(side=tk.LEFT, padx=10)

    def draw_axes(self):
        """Отрисовка осей координат"""
        self.canvas.delete("all")

        # Оси X и Y
        self.canvas.create_line(self.margin, self.canvas_height - self.margin,
                                self.canvas_width - self.margin, self.canvas_height - self.margin,
                                width=2, arrow=tk.LAST)
        self.canvas.create_line(self.margin, self.canvas_height - self.margin,
                                self.margin, self.margin, width=2, arrow=tk.LAST)

        # Сетка
        for i in range(0, self.grid_size + 1):
            x = self.margin + i * self.scale
            y = self.canvas_height - self.margin - i * self.scale
            self.canvas.create_line(x, self.canvas_height - self.margin, x, self.margin, dash=(2, 2), fill="gray")
            self.canvas.create_line(self.margin, y, self.canvas_width - self.margin, y, dash=(2, 2), fill="gray")
            self.canvas.create_text(x, self.canvas_height - self.margin + 10, text=str(i))
            self.canvas.create_text(self.margin - 10, y, text=str(i))

    def solve_problem(self):
        """Решение выбранной задачи"""
        problem = self.problems[self.current_problem]
        self.draw_axes()

        # Отрисовка ограничений
        for a, b, c, sign in problem["constraints"]:
            self.draw_constraint(a, b, c, sign)

        # Нахождение вершин ОДР
        vertices = self.find_vertices(problem["constraints"])

        if not vertices:
            messagebox.showinfo("Результат", "Область допустимых решений пуста!")
            return

        # Отрисовка ОДР
        self.draw_feasible_region(vertices)

        # Вычисление целевой функции
        if problem["type"] != "none":
            z_values = [problem["obj_func"][0] * x + problem["obj_func"][1] * y for x, y in vertices]

            if problem["type"] == "max":
                optimal_z = max(z_values)
                optimal_point = vertices[z_values.index(optimal_z)]
            else:
                optimal_z = min(z_values)
                optimal_point = vertices[z_values.index(optimal_z)]

            # Отрисовка оптимальной точки
            self.draw_point(optimal_point[0], optimal_point[1], "red")

            # Вывод результата
            result_text = f"Оптимальное значение: {optimal_z:.2f}\nв точке ({optimal_point[0]:.2f}, {optimal_point[1]:.2f})"
            self.canvas.create_text(self.canvas_width // 2, 30, text=result_text, font=('Arial', 10), fill="blue")

    def find_vertices(self, constraints):
        """Нахождение вершин ОДР"""
        vertices = []

        # Поиск пересечений всех пар ограничений
        for i in range(len(constraints)):
            for j in range(i + 1, len(constraints)):
                a1, b1, c1, _ = constraints[i]
                a2, b2, c2, _ = constraints[j]

                try:
                    A = np.array([[a1, b1], [a2, b2]])
                    B = np.array([c1, c2])
                    point = np.linalg.solve(A, B)

                    if point[0] >= 0 and point[1] >= 0 and self.check_constraints(point, constraints):
                        vertices.append((point[0], point[1]))
                except np.linalg.LinAlgError:
                    continue

        return vertices

    def check_constraints(self, point, constraints):
        """Проверка выполнения всех ограничений"""
        x, y = point
        for a, b, c, sign in constraints:
            value = a * x + b * y
            if sign == '<=' and value > c + 1e-6:
                return False
            elif sign == '>=' and value < c - 1e-6:
                return False
        return True

    def draw_constraint(self, a, b, c, sign):
        """Отрисовка линии ограничения с обработкой нулевых коэффициентов"""
        points = []

        # Точка пересечения с осью X (y=0)
        if a != 0:
            x = c / a
            if x >= 0:
                points.append((x, 0))

        # Точка пересечения с осью Y (x=0)
        if b != 0:
            y = c / b
            if y >= 0:
                points.append((0, y))

        # Если нашли две точки, рисуем линию
        if len(points) == 2:
            x1, y1 = points[0]
            x2, y2 = points[1]

            # Ограничиваем размером сетки
            if x1 > self.grid_size:
                x1 = self.grid_size
                y1 = (c - a * x1) / b if b != 0 else 0
            if y2 > self.grid_size:
                y2 = self.grid_size
                x2 = (c - b * y2) / a if a != 0 else 0

            # Переводим в координаты холста
            px1 = self.margin + x1 * self.scale
            py1 = self.canvas_height - self.margin - y1 * self.scale
            px2 = self.margin + x2 * self.scale
            py2 = self.canvas_height - self.margin - y2 * self.scale

            # Рисуем линию
            self.canvas.create_line(px1, py1, px2, py2, fill="blue", width=2)

            # Подпись
            label = f"{a}x₁ {'+' if b >= 0 else ''}{b}x₂ {sign} {c}"
            self.canvas.create_text((px1 + px2) / 2, (py1 + py2) / 2 - 15, text=label, fill="blue")
        elif len(points) == 1:
            # Обработка вертикальных/горизонтальных линий
            x, y = points[0]
            if a == 0:  # Горизонтальная линия
                px1 = self.margin
                py1 = self.canvas_height - self.margin - y * self.scale
                px2 = self.canvas_width - self.margin
                self.canvas.create_line(px1, py1, px2, py1, fill="blue", width=2)
            else:  # Вертикальная линия
                px1 = self.margin + x * self.scale
                py1 = self.margin
                py2 = self.canvas_height - self.margin
                self.canvas.create_line(px1, py1, px1, py2, fill="blue", width=2)

    def draw_feasible_region(self, vertices):
        """Отрисовка области допустимых решений"""
        pixel_vertices = []
        for x, y in vertices:
            px = self.margin + x * self.scale
            py = self.canvas_height - self.margin - y * self.scale
            pixel_vertices.extend([px, py])

        self.canvas.create_polygon(pixel_vertices, fill="gray", outline="black", stipple="gray50")

        for x, y in vertices:
            self.draw_point(x, y, "green")

    def draw_point(self, x, y, color):
        """Отрисовка точки"""
        px = self.margin + x * self.scale
        py = self.canvas_height - self.margin - y * self.scale
        self.canvas.create_oval(px - 4, py - 4, px + 4, py + 4, fill=color)
        self.canvas.create_text(px, py - 15, text=f"({x:.1f}, {y:.1f})", fill=color)

    def update_problem(self):
        """Обновление выбранной задачи"""
        self.current_problem = self.problem_var.get()
        self.draw_axes()


if __name__ == "__main__":
    root = tk.Tk()
    app = LinearProgrammingSolver(root)
    root.mainloop()
