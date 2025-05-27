import tkinter as tk
from tkinter import ttk, messagebox
import random
from PIL import Image, ImageTk
import datetime
import math
import matplotlib.pyplot as plt                                                                                 #type: ignore
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg                                                 #type: ignore

class Station:
    def __init__(self, name, coordinates):
        self.__name = name
        self.__coordinates = coordinates
        self.__waiting_passengers = []
        self.__departed_passengers = 0

    def get_name(self):
        return self.__name

    def get_coordinates(self):
        return self.__coordinates

    def add_passenger(self, passenger):
        self.__waiting_passengers.append(passenger)

    def remove_passenger(self, passenger):
        if passenger in self.__waiting_passengers:
            self.__waiting_passengers.remove(passenger)
            self.__departed_passengers += 1

    def get_passengers(self):
        return self.__waiting_passengers

    def get_passenger_count(self):
        return len(self.__waiting_passengers)

    def get_total_departed(self):
        return self.__departed_passengers

class Wagon:
    def __init__(self, number):
        self.__number = number

    def get_number(self):
        return self.__number

class ServiceWagon(Wagon):
    def __init__(self, number, service_type):
        super().__init__(number)
        self.__service_type = service_type

    def get_service_type(self):
        return self.__service_type

class PassengerWagon(Wagon):
    def __init__(self, number, seats, price_per_km, wagon_type, options=None):
        super().__init__(number)
        self.__seats = seats
        self.__price_per_km = price_per_km
        self.__wagon_type = wagon_type
        self.__passengers = []
        self.__options = options or []

    def get_wagon_type(self):
        return self.__wagon_type

    def add_passenger(self, passenger):
        if len(self.__passengers) < self.__seats:
            self.__passengers.append(passenger)
            return True
        return False

    def get_passenger_count(self):
        return len(self.__passengers)

    def is_full(self):
        return len(self.__passengers) >= self.__seats

    def get_options(self):
        return self.__options

    def get_price_per_km(self):
        return self.__price_per_km

    def get_seats(self):
        return self.__seats

class SeatedWagon(PassengerWagon):
    def __init__(self, number, seats, price_per_km, options=None):
        super().__init__(number, seats, price_per_km, "Сидячий", options)

class PlatskartWagon(PassengerWagon):
    def __init__(self, number, seats, price_per_km, options=None):
        super().__init__(number, seats, price_per_km, "Плацкарт", options)

class CoupeWagon(PassengerWagon):
    def __init__(self, number, seats, price_per_km, bed_option_price=100, options=None):
        super().__init__(number, seats, price_per_km, "Купе", options)
        self.__bed_option_price = bed_option_price

    def get_bed_price(self):
        return self.__bed_option_price

class Line:
    def __init__(self, start_station, end_station, direction):
        self.__start_station = start_station
        self.__end_station = end_station
        self.__direction = direction

    def get_start_station(self):
        return self.__start_station

    def get_end_station(self):
        return self.__end_station

    def get_direction(self):
        return self.__direction

class Train:
    def __init__(self, number, start_station, lines):
        self.__number = number
        self.__current_station = start_station
        self.__target_station = None
        self.__lines = lines
        self.__position = 0.0
        self.__current_line = None
        self.__wagons = []
        self.__is_waiting = False
        self.__passengers_processed = False

    def add_wagon(self, wagon):
        self.__wagons.append(wagon)

    def get_total_passengers(self):
        return sum(w.get_passenger_count() for w in self.__wagons if isinstance(w, PassengerWagon))

    def get_wagons(self):
        return self.__wagons

    def get_number(self):
        return self.__number

    def get_current_station(self):
        return self.__current_station

    def get_target_station(self):
        return self.__target_station

    def get_position(self):
        return self.__position

    def get_current_line(self):
        return self.__current_line

    def is_waiting(self):
        return self.__is_waiting

    def start_waiting(self):
        self.__is_waiting = True

    def end_waiting(self):
        self.__is_waiting = False
        self.choose_next_station()

    def choose_next_station(self):
        neighbors = []
        for line in self.__lines:
            if (line.get_start_station() == self.__current_station
                    and line.get_end_station() != self.__current_station):
                neighbors.append((line.get_end_station(), line))

        if neighbors:
            next_station, line = random.choice(neighbors)
            self.__current_line = line
            self.__target_station = next_station
            self.__position = 0.0
        else:
            self.__target_station = None
            self.__current_line = None
            self.__position = 0.0

    def move(self, step=0.01):
        if self.__is_waiting:
            return

        if self.__target_station is None:
            self.choose_next_station()
            return

        self.__position += step
        if self.__position >= 1.0:
            self.__current_station = self.__target_station
            self.__is_waiting = True
            self.__passengers_processed = False
            self.choose_next_station()
            self.__position = 0.0

    def process_passengers(self):
        self.__passengers_processed = True

    def needs_processing(self):
        return self.__is_waiting and not self.__passengers_processed

class Passenger:
    def __init__(self, destination, travel_date, preferences):
        self.__destination = destination
        self.__travel_date = travel_date
        self.__preferences = preferences
        self.__denied_reason = None

    def get_destination(self):
        return self.__destination

    def get_preferences(self):
        return self.__preferences

    def get_denied_reason(self):
        return self.__denied_reason

    def set_denied_reason(self, value):
        self.__denied_reason = value

class Ticket:
    def __init__(self, train, wagon, passenger, price, departure_station):
        self.__train = train
        self.__wagon = wagon
        self.__passenger = passenger
        self.__price = price
        self.__departure_station = departure_station

    def get_price(self):
        return self.__price

    def get_train(self):
        return self.__train

    def get_wagon(self):
        return self.__wagon

    def get_departure_station(self):
        return self.__departure_station

class Kassa:
    def __init__(self, trains):
        self.__trains = trains
        self.__sales_log = []
        self.__denied_count = 0

    def sell_ticket(self, passenger, current_station):
        suitable_trains = [
            t for t in self.__trains
            if t.get_current_station().get_name() == current_station.get_name()
               and t.get_target_station() is not None
               and t.get_target_station().get_name() == passenger.get_destination()
        ]

        if not suitable_trains:
            self.__denied_count += 1
            return None

        for train in suitable_trains:
            for wagon in train.get_wagons():
                if isinstance(wagon, PassengerWagon) and not wagon.is_full():
                    check, _ = self.__check_preferences(wagon, passenger.get_preferences())
                    if check:
                        if wagon.add_passenger(passenger):
                            distance = self.__calculate_distance(
                                train.get_current_station(),
                                train.get_target_station()
                            )
                            price = wagon.get_price_per_km() * distance

                            if isinstance(wagon, CoupeWagon) and passenger.get_preferences().get("постель"):
                                price += wagon.get_bed_price()
                            if "телевизор" in passenger.get_preferences().get('options', []):
                                price *= 1.1
                            if "телефон" in passenger.get_preferences().get('options', []):
                                price *= 1.05

                            ticket = Ticket(train, wagon, passenger, price, train.get_current_station())
                            self.__sales_log.append(ticket)
                            return ticket

        self.__denied_count += 1
        return None

    def __check_preferences(self, wagon, preferences):
        if 'type' in preferences:
            if preferences['type'].lower() != wagon.get_wagon_type().lower():
                return False, "Несоответствие типа вагона"

        missing_options = [opt for opt in preferences.get('options', [])
                           if opt not in wagon.get_options()]
        if missing_options:
            return False, "Отсутствует необходимое оборудование"

        return True, ""

    def __calculate_distance(self, s1, s2):
        x1, y1 = s1.get_coordinates()
        x2, y2 = s2.get_coordinates()
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def get_trains(self):
        return self.__trains

    def get_sales_log(self):
        return self.__sales_log

    def get_denied_requests(self):
        return self.__denied_count

    def get_wagon_load_stats(self):
        stats = {}
        for train in self.__trains:
            for wagon in train.get_wagons():
                if isinstance(wagon, PassengerWagon):
                    stats.setdefault(wagon.get_wagon_type(), [0, 0])
                    stats[wagon.get_wagon_type()][0] += wagon.get_passenger_count()
                    stats[wagon.get_wagon_type()][1] += wagon.get_seats()
        return stats

    def get_route_load_stats(self):
        stats = {}
        for train in self.__trains:
            if train.get_target_station():
                route = f"{train.get_current_station().get_name()} - {train.get_target_station().get_name()}"
                stats.setdefault(route, [0, 0])
                stats[route][0] += train.get_total_passengers()
                stats[route][1] += sum(w.get_seats() for w in train.get_wagons() if isinstance(w, PassengerWagon))
        return stats

    def get_revenue_stats(self):
        by_train = {}
        by_station = {}
        by_wtype = {}

        for ticket in self.__sales_log:
            tnum = ticket.get_train().get_number()
            st = ticket.get_departure_station().get_name()
            wagon_type = ticket.get_wagon().get_wagon_type()

            by_train[tnum] = by_train.get(tnum, 0) + ticket.get_price()
            by_station[st] = by_station.get(st, 0) + ticket.get_price()
            by_wtype[wagon_type] = by_wtype.get(wagon_type, 0) + ticket.get_price()

        train_nums = sorted(by_train.keys(), key=lambda x: int(x))
        by_train_ordered = {k: by_train[k] for k in train_nums}

        station_names = sorted(by_station.keys())
        by_station_ordered = {k: by_station[k] for k in station_names}

        return by_train_ordered, by_station_ordered, by_wtype

class RailwayApp:
    def __init__(self, root, kassa, stations, lines):
        self.__kassa = kassa
        self.__stations = stations
        self.__lines = lines
        self.root = root
        self.root.title("Железнодорожная система")
        self.root.geometry("1400x900")

        self.__load_images()
        self.__setup_ui()
        self.__simulation_running = False
        self.__generation_running = False
        self.__simulation_speed = 1.0
        self.__current_time = datetime.datetime(2024, 1, 1, 8, 0)
        self.__start_passenger_generation()

    def __load_images(self):
        try:
            self.train_img = ImageTk.PhotoImage(Image.open("Image/train.png").resize((80, 40)))
            self.station_img = ImageTk.PhotoImage(Image.open("Image/station.png").resize((80, 80)))
        except FileNotFoundError as e:
            messagebox.showerror("Ошибка", f"Не найдены файлы изображений: {e}")
            self.root.destroy()

    def __setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        control_frame = ttk.Frame(main_frame, padding=10)
        control_frame.pack(fill=tk.X)

        ttk.Button(control_frame, text="▶ Старт", command=self.__start_simulation).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="⏸ Пауза", command=self.__stop_simulation).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="📊 Статистика", command=self.__show_stats_window).pack(side=tk.LEFT, padx=5)

        self.speed_scale = ttk.Scale(control_frame, from_=0.5, to=3.0, value=1.0,
                                     command=self.__update_simulation_speed)
        self.speed_scale.pack(side=tk.LEFT, padx=5)

        self.time_label = ttk.Label(control_frame, text="Время: 08:00", font=('Arial', 10, 'bold'))
        self.time_label.pack(side=tk.RIGHT, padx=10)

        self.canvas = tk.Canvas(main_frame, bg='#f0f0f0', width=1300, height=700)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.__draw_map()
        self.__update_trains()

        ttk.Label(main_frame, text="Нажмите на поезд для получения информации", font=('Arial', 8)).pack(side=tk.BOTTOM)

    def __draw_map(self):
        self.__station_coords = {}
        center_x, center_y = 650, 350
        radius = 280
        angles = [math.radians(90 + i * 60) for i in range(6)]

        for i, station in enumerate(self.__stations):
            x = center_x + radius * math.cos(angles[i])
            y = center_y + radius * math.sin(angles[i])
            self.__station_coords[station] = (x, y)
            self.canvas.create_image(x, y, image=self.station_img, tags="station")
            self.canvas.create_text(x, y + 50, text=station.get_name(), font=('Arial', 12, 'bold'))
            self.canvas.create_text(x, y + 70, text=f"Пассажиров: {station.get_passenger_count()}",
                                    font=('Arial', 9), tags=f"pass_{station.get_name()}")

        for line in self.__lines:
            x1, y1 = self.__station_coords[line.get_start_station()]
            x2, y2 = self.__station_coords[line.get_end_station()]
            arrow = tk.LAST if line.get_direction() == 'forward' else tk.FIRST
            self.canvas.create_line(x1, y1, x2, y2, arrow=arrow, width=3, fill="#555")

    def __update_trains(self):
        self.canvas.delete("train")
        trains_on_lines = {}
        for train in self.__kassa.get_trains():
            if train.get_current_line():
                line_id = id(train.get_current_line())
                trains_on_lines.setdefault(line_id, []).append(train)

        for train in self.__kassa.get_trains():
            if train.get_target_station() or train.is_waiting():
                start = self.__station_coords[train.get_current_station()]
                end = start if train.is_waiting() else self.__station_coords[train.get_target_station()]

                x = start[0] + (end[0] - start[0]) * train.get_position()
                y = start[1] + (end[1] - start[1]) * train.get_position()

                if train.get_current_line() and not train.is_waiting():
                    line_id = id(train.get_current_line())
                    index = trains_on_lines[line_id].index(train)
                    angle = math.atan2(end[1] - start[1], end[0] - start[0])
                    dx = -math.sin(angle) * 30 * index
                    dy = math.cos(angle) * 30 * index
                    x += dx
                    y += dy

                img = self.canvas.create_image(x, y, image=self.train_img,
                                               tags=("train", f"train_{train.get_number()}"))
                self.canvas.tag_bind(img, "<Button-1>", lambda e, t=train: self.__show_train_info(t))
                self.canvas.create_text(x, y - 30, text=f"Поезд {train.get_number()}",
                                        font=('Arial', 9, 'bold'), tags=("train", "train_text"))

        for station in self.__stations:
            self.canvas.itemconfig(f"pass_{station.get_name()}", text=f"Пассажиров: {station.get_passenger_count()}")

    def __show_train_info(self, train):
        info_window = tk.Toplevel(self.root)
        info_window.title(f"Информация о поезде {train.get_number()}")
        info_window.geometry("600x500")

        main_frame = ttk.Frame(info_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        route_frame = ttk.LabelFrame(main_frame, text="Маршрут", padding=10)
        route_frame.pack(fill=tk.X, pady=5)

        ttk.Label(route_frame, text=f"Текущая станция: {train.get_current_station().get_name()}").pack(anchor=tk.W)
        if train.get_target_station():
            ttk.Label(route_frame, text=f"Следующая станция: {train.get_target_station().get_name()}").pack(anchor=tk.W)
        else:
            ttk.Label(route_frame, text="Ожидание...").pack(anchor=tk.W)

        wagon_frame = ttk.LabelFrame(main_frame, text="Вагоны", padding=10)
        wagon_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        tree = ttk.Treeview(wagon_frame, columns=('type', 'number', 'passengers', 'options', 'price'),
                            show='headings', height=8)
        tree.heading('type', text='Тип')
        tree.heading('number', text='Номер')
        tree.heading('passengers', text='Пассажиры')
        tree.heading('options', text='Опции')
        tree.heading('price', text='Цена за км')

        for wagon in train.get_wagons():
            if isinstance(wagon, PassengerWagon):
                values = (
                    wagon.get_wagon_type(),
                    wagon.get_number(),
                    f"{wagon.get_passenger_count()}/{wagon.get_seats()}",
                    ', '.join(wagon.get_options()),
                    f"{wagon.get_price_per_km():.2f} руб"
                )
            else:
                values = (
                    "Служебный",
                    wagon.get_number(),
                    "-",
                    wagon.get_service_type(),
                    "-"
                )
            tree.insert('', 'end', values=values)

        tree.pack(fill=tk.BOTH, expand=True)
        ttk.Label(main_frame, text=f"Всего пассажиров: {train.get_total_passengers()}",
                  font=('Arial', 10, 'bold')).pack(pady=5)

    def __generate_passengers(self):
        if self.__generation_running:
            for station in self.__stations:
                for _ in range(random.randint(5, 10)):
                    destinations = [s for s in self.__stations if s != station]
                    if destinations:
                        dest = random.choice(destinations)
                        prefs = {
                            'type': random.choice(['сидячий', 'плацкарт', 'купе']),
                            'options': random.sample(['телевизор', 'телефон'], random.randint(0, 2))
                        }
                        if random.random() > 0.7:
                            prefs['постель'] = True
                        passenger = Passenger(dest.get_name(), self.__current_time.strftime("%Y-%m-%d"), prefs)
                        station.add_passenger(passenger)

            self.root.after(int(12000 // self.__simulation_speed), self.__generate_passengers)

    def __start_passenger_generation(self):
        if not self.__generation_running:
            self.__generation_running = True
            self.__generate_passengers()

    def __simulation_step(self):
        if self.__simulation_running:
            self.__current_time += datetime.timedelta(minutes=1)
            self.time_label.config(text=f"Время: {self.__current_time.strftime('%H:%M')}")

            for train in self.__kassa.get_trains():
                if train.needs_processing():
                    self.__handle_arrival(train)
                    train.process_passengers()

            for train in self.__kassa.get_trains():
                if not train.is_waiting():
                    train.move(0.01 * self.__simulation_speed)

            self.__update_trains()

        self.root.after(50, self.__simulation_step)

    def __handle_arrival(self, train):
        station = train.get_current_station()
        self.__process_passengers(train, station)
        self.root.after(1000, lambda: self.__end_waiting(train))

    def __end_waiting(self, train):
        train.end_waiting()
        self.__update_trains()

    def __process_passengers(self, train, station):
        passengers_to_remove = []
        target_station = train.get_target_station()
        if target_station is None:
            return

        for wagon in train.get_wagons():
            if isinstance(wagon, PassengerWagon):
                wagon._PassengerWagon__passengers = [
                    p for p in wagon._PassengerWagon__passengers
                    if p.get_destination() != target_station.get_name()
                ]

        passengers = [p for p in station.get_passengers()
                      if p.get_destination() == target_station.get_name()]

        for passenger in passengers:
            ticket = self.__kassa.sell_ticket(passenger, station)
            if ticket:
                passengers_to_remove.append(passenger)

        for p in passengers_to_remove:
            station.remove_passenger(p)

    def __start_simulation(self):
        if not self.__simulation_running:
            self.__simulation_running = True
            self.__start_passenger_generation()
            self.__simulation_step()

    def __stop_simulation(self):
        self.__simulation_running = False

    def __update_simulation_speed(self, value):
        self.__simulation_speed = float(value)

    def __show_stats_window(self):
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Статистика системы")
        stats_window.geometry("900x700")

        notebook = ttk.Notebook(stats_window)

        load_frame = ttk.Frame(notebook)
        self.__add_load_stats(load_frame)
        notebook.add(load_frame, text="Загруженность")

        finance_frame = ttk.Frame(notebook)
        self.__add_finance_stats(finance_frame)
        notebook.add(finance_frame, text="Финансы")

        denied_frame = ttk.Frame(notebook)
        self.__add_denied_stats(denied_frame)
        notebook.add(denied_frame, text="Отказы")

        station_frame = ttk.Frame(notebook)
        self.__add_station_stats(station_frame)
        notebook.add(station_frame, text="Станции")

        notebook.pack(fill=tk.BOTH, expand=True)

    def __add_load_stats(self, frame):
        wagon_stats = self.__kassa.get_wagon_load_stats()
        route_stats = self.__kassa.get_route_load_stats()

        ttk.Label(frame, text="Загруженность вагонов:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        for wagon_type, data in wagon_stats.items():
            percent = (data[0] / data[1]) * 100 if data[1] > 0 else 0
            ttk.Label(frame, text=f"{wagon_type}: {data[0]}/{data[1]} ({percent:.1f}%)").pack(anchor=tk.W)

        ttk.Label(frame, text="\nЗагруженность маршрутов:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        for route, data in route_stats.items():
            ttk.Label(frame, text=f"{route}: {data[0]}/{data[1]} пассажиров").pack(anchor=tk.W)

    def __add_finance_stats(self, frame):
        fig = plt.Figure(figsize=(10, 8), dpi=100)
        by_train, by_station, by_wtype = self.__kassa.get_revenue_stats()

        ax1 = fig.add_subplot(311)
        train_numbers = list(by_train.keys())
        train_values = [by_train[num] for num in train_numbers]
        bars1 = ax1.bar(train_numbers, train_values, color='#1f77b4')
        ax1.set_title('Выручка по поездам')
        ax1.bar_label(bars1, fmt='%.1f руб', label_type='edge', padding=-15, color='white', fontsize=8)
        plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')

        ax2 = fig.add_subplot(312)
        station_names = list(by_station.keys())
        station_values = [by_station[name] for name in station_names]
        bars2 = ax2.bar(station_names, station_values, color='#2ca02c')
        ax2.set_title('Выручка по станциям')
        ax2.bar_label(bars2, fmt='%.1f руб', label_type='edge', padding=-15, color='white', fontsize=8)
        plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')

        ax3 = fig.add_subplot(313)
        ax3.pie(by_wtype.values(), labels=by_wtype.keys(), autopct='%1.1f%%', colors=['#ff7f0e', '#d62728', '#9467bd'])
        ax3.set_title('Распределение выручки по типам вагонов')

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def __add_denied_stats(self, frame):
        denied = self.__kassa.get_denied_requests()
        ttk.Label(frame, text=f"Всего отказов: {denied}", font=("Arial", 12, "bold")).pack(anchor=tk.W)

    def __add_station_stats(self, frame):
        ttk.Label(frame, text="Статистика станций:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        for station in self.__stations:
            ttk.Label(frame, text=f"{station.get_name()}: Ожидает {station.get_passenger_count()}, "
                                  f"Отправлено {station.get_total_departed()}").pack(anchor=tk.W)

stations = [
    Station("Москва", (0, 0)),
    Station("Санкт-Петербург", (100, 0)),
    Station("Казань", (0, 100)),
    Station("Сочи", (100, 100)),
    Station("Владивосток", (50, 50)),
    Station("Екатеринбург", (150, 50))
]

lines = []
for s1 in stations:
    for s2 in stations:
        if s1 != s2:
            lines.append(Line(s1, s2, 'forward'))
            lines.append(Line(s2, s1, 'backward'))

trains = [
    Train("001", stations[0], lines),
    Train("002", stations[1], lines),
    Train("003", stations[2], lines),
    Train("004", stations[3], lines),
    Train("005", stations[4], lines)
]

for train in trains:
    train.add_wagon(SeatedWagon("W1", 50, 2.0, ["телевизор"]))
    train.add_wagon(PlatskartWagon("W2", 40, 1.8, ["телефон"]))
    train.add_wagon(CoupeWagon("W3", 30, 3.0, 150))
    train.add_wagon(ServiceWagon("S1", "ресторан"))

root = tk.Tk()
app = RailwayApp(root, Kassa(trains), stations, lines)
root.mainloop()
