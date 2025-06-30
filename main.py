import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
import cv2
import numpy as np
from PIL import Image, ImageTk
import sys
def imread_unicode(file_path):
    with open(file_path, "rb") as f:
        data = np.frombuffer(f.read(), np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    return img

class ImageApp:
    def on_resize(self, event):
        if self.image is not None:
            self.show_image(self.image)

    def __init__(self, root):
        self.root = root
        self.root.title("Приложение для обработки изображений")
        if sys.platform.startswith("win"):
            self.root.state("zoomed")
        else:
            self.root.attributes('-zoomed', True)

        self.frame_buttons = tk.Frame(self.root)
        self.frame_buttons.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.canvas = tk.Canvas(self.root, width=600, height=400, bg="black")
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.root.bind("<Configure>", self.on_resize)

        self.image = None
        self.original_image = None

        btn_width = 25
        tk.Button(self.frame_buttons, text="Загрузить изображение", width=btn_width, command=self.load_image).pack(pady=5)
        tk.Button(self.frame_buttons, text="Сделать снимок с камеры", width=btn_width, command=self.capture_image).pack(pady=5)
        self.channel_var = tk.StringVar()
        self.channel_menu = ttk.Combobox(self.frame_buttons, textvariable=self.channel_var, state="readonly",
                                         values=["R (Красный)", "G (Зелёный)", "B (Синий)"])
        self.channel_menu.set("Выбрать канал")
        self.channel_menu.pack(pady=5)

        tk.Button(self.frame_buttons, text="Показать канал (R/G/B)", width=btn_width, command=self.show_channel_dialog).pack(pady=5)
        tk.Button(self.frame_buttons, text="Негатив изображения", width=btn_width, command=self.show_negative).pack(pady=5)
        tk.Button(self.frame_buttons, text="Усреднение изображения", width=btn_width, command=self.show_blur).pack(pady=5)
        tk.Button(self.frame_buttons, text="Нарисовать прямоугольник", width=btn_width, command=self.draw_rectangle).pack(pady=5)
        tk.Button(self.frame_buttons, text="Отменить изменения", width=btn_width, command=self.reset_image).pack(pady=5)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Изображения", "*.png;*.jpg;*.jpeg")])
        if file_path:
            img = imread_unicode(file_path)
            if img is None:
                messagebox.showerror("Ошибка", "Не удалось загрузить изображение. Проверьте файл и попробуйте снова.")
            else:
                self.original_image = img.copy()
                self.show_image(img)

    def capture_image(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Ошибка", "Не удалось подключиться к веб-камере.")
            return

        # Прокрутить несколько кадров для стабилизации
        for _ in range(5):
            ret, frame = cap.read()
            if not ret:
                cap.release()
                messagebox.showerror("Ошибка", "Не удалось получить изображение с камеры.")
                return

        cap.release()

        self.original_image = frame.copy()
        self.show_image(frame)

    def show_image(self, img):
        self.image = img
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width < 10 or canvas_height < 10:
            canvas_width, canvas_height = 600, 400
        img_pil = img_pil.resize((canvas_width, canvas_height))

        img_tk = ImageTk.PhotoImage(img_pil)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        self.canvas.image = img_tk

    def show_channel_dialog(self):
        if self.image is None:
            messagebox.showwarning("Внимание", "Сначала загрузите изображение или сделайте снимок.")
            return
        channel = self.channel_var.get()
        if channel not in ["R (Красный)", "G (Зелёный)", "B (Синий)"]:
            messagebox.showerror("Ошибка", "Сначала выберите канал из выпадающего списка.")
            return
        b, g, r = cv2.split(self.image)
        zero = np.zeros_like(b)
        if channel.startswith("R"):
            img_channel = cv2.merge([zero, zero, r])
        elif channel.startswith("G"):
            img_channel = cv2.merge([zero, g, zero])
        else:
            img_channel = cv2.merge([b, zero, zero])
        self.show_image(img_channel)

    def show_negative(self):
        if self.image is None:
            messagebox.showwarning("Внимание", "Сначала загрузите изображение или сделайте снимок.")
            return
        negative = cv2.bitwise_not(self.image)
        self.show_image(negative)

    def show_blur(self):
        if self.image is None:
            messagebox.showwarning("Внимание", "Сначала загрузите изображение или сделайте снимок.")
            return
        ksize = simpledialog.askinteger("Усреднение", "Введите размер ядра (нечётное число):", minvalue=1)
        if ksize is None:
            return
        if ksize % 2 == 0:
            messagebox.showerror("Ошибка", "Размер ядра должен быть нечётным числом.")
            return
        blurred = cv2.blur(self.image, (ksize, ksize))
        self.show_image(blurred)

    def draw_rectangle(self):
        if self.image is None:
            messagebox.showwarning("Внимание", "Сначала загрузите изображение или сделайте снимок.")
            return
        x1 = simpledialog.askinteger("Прямоугольник", "Введите X1:")
        y1 = simpledialog.askinteger("Прямоугольник", "Введите Y1:")
        x2 = simpledialog.askinteger("Прямоугольник", "Введите X2:")
        y2 = simpledialog.askinteger("Прямоугольник", "Введите Y2:")
        if None in (x1, y1, x2, y2):
            return
        img_copy = self.image.copy()
        cv2.rectangle(img_copy, (x1, y1), (x2, y2), (255, 0, 0), 2)
        self.show_image(img_copy)

    def reset_image(self):
        if self.original_image is not None:
            self.show_image(self.original_image.copy())
        else:
            messagebox.showinfo("Отмена", "Нет исходного изображения для восстановления.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageApp(root)
    root.mainloop()
