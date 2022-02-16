import numpy as np
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
import re

training_intensities = ['e', 'm', 't', 'i', 'r']

races = ['1 mile', '1.5k', '3k', '2 mile', '5k',
         '10k', '15k', '1/2 marathon', 'marathon']

base_distances = ['miles', 'kilometers', 'meters']

distances = {
    'e': 1.0,
    'm': 1.0,
    't': 1.0,
    'i': 1.0,
    'r': 1.0,
    'meters': 0.001,
    'kilometers': 1.0,
    'miles': 1.60934,
    '1 mile': 1.60934,
    '1.5k': 1.5,
    '3k': 3.0,
    '2 mile': 3.21869,
    '5k': 5.0,
    '10k': 10.0,
    '15k': 15.0,
    '1/2 marathon': 21.0975,
    'marathon': 42.195,
}

pace_coefs = {
    'e':
        np.array([4949.27103996282, 35.90981260691225, -1471.4577840422419,
        -10780.124357908137, -0.20469289084241282, 0.0005847523343618377]),
    'm':
        np.array([5769.83766356983, 49.293532532288424, -1810.3895026597256,
        -12851.045985015659, -0.291126234807642, 0.0008304956752454018]),
    't':
        np.array([223.6265478238622, -5.763413154957469, 19.099113274553744,
        6742.587058504519, 0.05418680896355041, -0.0002009103554740932]),
    'i':
        np.array([-1397.1455774707638, -20.7582565066043, 538.6711541187304,
        12633.618023527979, 0.14848775051980745, -0.0004883293344164485]),
    'r':
        np.array([10660.490550384873, 130.77354304136978, -3692.965990299492,
        -27355.696889999857, -0.9608418286816445, 0.003311943788503413]),
    '1.5k':  
        np.array([-1024.5822352717075, -10.731044795236159, 353.2650183281407,
        13005.840167602588, 0.06171966948983876, -0.0001562261014669275]),
    '1 mile':
        np.array([576.7753448412576, 3.3192456503761933, -156.34952340276442,
        6420.044874165655, -0.020670725644730936, 7.408644617612481e-05]),
    '3k':
        np.array([1499.2430457131895, 6.767824096643538, -404.92262747303425,
        1607.0419570247086, -0.02374668119369172, 3.4554979492895654e-05]),
    '2 mile':
        np.array([-1045.0013023631577, -14.640786068658485, 396.2141979621974,
        12469.405383898818, 0.09920956538251247, -0.0003080573083593663]),
    '5k':
        np.array([437.6518586459911, 0.4941894100173703, -91.52385224172308,
        6835.359275121465, -0.0015546250007074658, 1.4531197450651234e-05]),
    '10k':
        np.array([1485.7044109851745, 9.090936250940503, -420.81173038190957,
        2829.640433497747, -0.047615054284755765, 0.00012889765116597118]),
    '15k':
        np.array([5324.864916618287, 42.969983444853156, -1642.127218950582,
        -12899.002436731642, -0.25137909439659367, 0.0007276965582150297]),
    '1/2 marathon':
        np.array([1276.183264850465, 4.319297166627139, -326.60317176899537,
        3415.9304672035796, -0.008655923707888036, -9.751162735938124e-06]),
    'marathon':
        np.array([1075.634255870165, 2.9638403435363587, -260.1835184112333,
        4138.276684781273, -0.007771151460666648, 1.250212534387174e-05])
}

def format_time(td: datetime.timedelta, strip: bool=True):
    td = datetime.timedelta(seconds=td.seconds).__str__()
    return re.search(pattern=r'[1-9].*', string=td).group() if strip else td


class Model:
    def __init__(self):
        self.vdot_min = 30
        self.vdot_max = 85

    def check_valid_vdot(self, vdot):
        if not isinstance(vdot, int):
            raise TypeError('VDOT needs to be an int')
        if not self.vdot_min <= vdot <= self.vdot_max:
            raise ValueError((
                f'VDOT {vdot} outside acceptable range of '
                f'{self.vdot_min} to {self.vdot_max}'
            ))
        else:
            return True

    @staticmethod
    def get_pace_from_vdot_and_intensity(vdot, intensity):
        X = np.array([1, vdot, np.log(vdot), 1/vdot, vdot**2, vdot**3])
        w = pace_coefs[intensity]
        seconds = np.round(X @ w,)
        return datetime.timedelta(seconds=seconds)

    @staticmethod
    def get_time_from_vdot_and_race(vdot, race):
        pace = Model.get_pace_from_vdot_and_intensity(vdot, race)
        distance = distances[race]
        return pace * distance

    @staticmethod
    def calculate_pace(time: datetime.timedelta, distance: float) -> datetime.timedelta:
        return time / distance

    @staticmethod
    def calculate_time(distance: float, pace: datetime.timedelta) -> datetime.timedelta:
        return distance * pace

    @staticmethod
    def calculate_distance(time: datetime.timedelta, pace: datetime.timedelta) -> float:
        return np.round(time / pace, 5)

    @staticmethod
    def convert_pace_km_to_miles(pace: datetime.timedelta) -> datetime.timedelta:
        return pace * 1.609344

    @staticmethod
    def convert_pace_miles_to_km(pace: datetime.timedelta) -> datetime.timedelta:
        return pace / 1.609344

    @staticmethod
    def convert_distance_km_to_miles(pace: datetime.timedelta) -> datetime.timedelta:
        return pace / 1.609344

    @staticmethod
    def convert_distance_miles_to_km(pace: datetime.timedelta) -> datetime.timedelta:
        return pace * 1.609344


class View(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        # field options
        options = {'anchor': tk.W, 'padx': 10, 'pady': 10}
        options_tight = {'anchor': tk.W, 'padx': 10, 'pady': 2}

        # vdot label
        self.frame_vdot = ttk.Frame(self)
        self.frame_vdot.pack(**options_tight)
        self.vdot_label = ttk.Label(self.frame_vdot, text='VDOT:', width=8)
        self.vdot_label.pack(padx=10, side='left')
        self.vdot = tk.StringVar()
        self.vdot_entry = ttk.Entry(self.frame_vdot, textvariable=self.vdot, width=10)
        self.vdot_entry.pack(padx=10, side='left')
        self.vdot_entry.focus()

        # km / mi entry
        self.frame_km_mi = ttk.Frame(self)
        self.frame_km_mi.pack(**options_tight)
        self.vdot_label = ttk.Label(self.frame_km_mi, text='Km / Mile:', width=8)
        self.vdot_label.pack(padx=10, side='left')
        self.km_mi = tk.StringVar()
        optionlist = ['km', 'km', 'mi']
        self.km_mi_menu = ttk.OptionMenu(self.frame_km_mi, self.km_mi, *optionlist)
        self.km_mi_menu.pack(**options)

        # get button
        self.refresh_button = ttk.Button(self, text='Refresh')
        self.refresh_button['command'] = self.refresh_button_clicked
        self.refresh_button.pack(**options)

        # training intensity pace table
        columns = ['vdot'] + training_intensities
        self.training_intensity_pace_tree = ttk.Treeview(self, columns=columns, show='headings', height=5)
        for column in columns:
            self.training_intensity_pace_tree.column(f"{column}", anchor=tk.CENTER, stretch=tk.NO, width=110)
            self.training_intensity_pace_tree.heading(f"{column}", text=f"{column}")
        self.training_intensity_pace_tree.pack(**options)

        # race pace table
        columns = ['vdot'] + races
        self.race_pace_tree = ttk.Treeview(self, columns=columns, show='headings', height=5)
        for column in columns:
            self.race_pace_tree.column(f"{column}", anchor=tk.CENTER, stretch=tk.NO, width=110)
            self.race_pace_tree.heading(f"{column}", text=f"{column}")
        self.race_pace_tree.pack(**options)

        # race time table
        columns = ['vdot'] + races
        self.race_time_tree = ttk.Treeview(self, columns=columns, show='headings', height=5)
        for column in columns:
            self.race_time_tree.column(f"{column}", anchor=tk.CENTER, stretch=tk.NO, width=110)
            self.race_time_tree.heading(f"{column}", text=f"{column}")
        self.race_time_tree.pack(**options)

        # Pace Calculator | Time
        self.frame_time = ttk.Frame(self)
        self.frame_time.pack(**options_tight)
        self.time_label = ttk.Label(self.frame_time, text='Time', width=8)
        self.time_label.pack(padx=10, side='left')
        self.time_hour = tk.StringVar()
        self.time_hour = ttk.Entry(self.frame_time, textvariable=self.time_hour, width=5)
        self.time_hour.pack(padx=5, side='left')
        ttk.Label(self.frame_time, text=':').pack(padx=3, side='left')
        self.time_min = tk.StringVar()
        self.time_min = ttk.Entry(self.frame_time, textvariable=self.time_min, width=5)
        self.time_min.pack(padx=5, side='left')
        ttk.Label(self.frame_time, text=':').pack(padx=3, side='left')
        self.time_sec = tk.StringVar()
        self.time_sec = ttk.Entry(self.frame_time, textvariable=self.time_sec, width=5)
        self.time_sec.pack(padx=5, side='left')

        # Pace Calculator | Distance
        self.frame_distance = ttk.Frame(self)
        self.frame_distance.pack(**options_tight)
        self.distance_label = ttk.Label(self.frame_distance, text='Distance', width=8)
        self.distance_label.pack(padx=10, side='left')
        self.distance_units = tk.StringVar()
        self.distance_units = ttk.Entry(self.frame_distance, textvariable=self.distance_units, width=5)
        self.distance_units.pack(padx=5, side='left')
        self.distance_race = tk.StringVar()
        options = base_distances + races
        self.distance_race = ttk.OptionMenu(self.frame_distance, self.distance_race, options[0], *options)
        self.distance_race.pack(padx=5, side='left')

        # Pace Calculator | Pace
        self.frame_pace = ttk.Frame(self)
        self.frame_pace.pack(**options_tight)
        self.pace_label = ttk.Label(self.frame_pace, text='Pace', width=8)
        self.pace_label.pack(padx=10, side='left')
        self.pace_hour = tk.StringVar()
        self.pace_hour = ttk.Entry(self.frame_pace, textvariable=self.pace_hour, width=5)
        self.pace_hour.pack(padx=5, side='left')
        ttk.Label(self.frame_pace, text=':').pack(padx=3, side='left')
        self.pace_min = tk.StringVar()
        self.pace_min = ttk.Entry(self.frame_pace, textvariable=self.pace_min, width=5)
        self.pace_min.pack(padx=5, side='left')
        ttk.Label(self.frame_pace, text=':').pack(padx=3, side='left')
        self.pace_sec = tk.StringVar()
        self.pace_sec = ttk.Entry(self.frame_pace, textvariable=self.pace_sec, width=5)
        self.pace_sec.pack(padx=5, side='left')

        # add padding to the frame and show it
        # self.grid(padx=10, pady=10, sticky=tk.NSEW)
        self.pack(side=tk.LEFT)
        
        # set the controller
        self.controller = None

    def set_controller(self, controller):
        self.controller = controller

    def refresh_button_clicked(self):
        if self.controller:
            self.controller.validate_vdot(int(self.vdot.get()))
            self.controller.get_training_intensity_paces(int(self.vdot.get()), self.km_mi.get())
            self.controller.get_race_paces(int(self.vdot.get()), self.km_mi.get())
            self.controller.get_race_times(int(self.vdot.get()), self.km_mi.get())

    def print_training_intensity_paces_to_table(self, records, users_vdot):
        self.training_intensity_pace_tree.delete(*self.training_intensity_pace_tree.get_children())
        for vdot, times in records.items():
            values = [vdot] + [format_time(time) for time in times.values()]
            self.training_intensity_pace_tree.insert('', tk.END, values=values, iid=vdot)
        self.training_intensity_pace_tree.selection_set(users_vdot)

    def print_race_pace_to_table(self, records, users_vdot):
        self.race_pace_tree.delete(*self.race_pace_tree.get_children())
        for vdot, times in records.items():
            values = [vdot] + [format_time(time) for time in times.values()]
            self.race_pace_tree.insert('', tk.END, values=values, iid=vdot)
        self.race_pace_tree.selection_set(users_vdot)

    def print_race_time_to_table(self, records, users_vdot):
        self.race_time_tree.delete(*self.race_time_tree.get_children())
        for vdot, times in records.items():
            values = [vdot] + [format_time(time) for time in times.values()]
            self.race_time_tree.insert('', tk.END, values=values, iid=vdot)
        self.race_time_tree.selection_set(users_vdot)

    def show_error(self, message):
        showerror(title='Error', message=message)


class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def validate_vdot(self, vdot):
        try:
            self.model.check_valid_vdot(vdot)
        except ValueError as error:
            self.view.show_error(error)

    def get_training_intensity_paces(self, vdot, km_mi):
        """
        returns dictionary of paces for all avalible training_intensities over a range of vdots
        """
        # get training_intensities from Model
        results = {}
        for v in range(vdot-2, vdot+3):
            try:
                results[v] = {pace: self.model.get_pace_from_vdot_and_intensity(v, pace) for pace in training_intensities}
                if km_mi == 'mi':
                    results[v] = dict((k, Model.convert_pace_km_to_miles(v)) for k, v in results[v].items())
            except:
                continue
        # output to View
        self.view.print_training_intensity_paces_to_table(results, vdot)


    def get_race_paces(self, vdot, km_mi):            
        # get race from Model
        results = {}
        for v in range(vdot-2, vdot+3):
            try:
                results[v] = {race: self.model.get_pace_from_vdot_and_intensity(v, race) for race in races}
                if km_mi == 'mi':
                    results[v] = dict((k, Model.convert_pace_km_to_miles(v)) for k, v in results[v].items())
            except:
                continue
        # output to View
        self.view.print_race_pace_to_table(results, vdot)


    def get_race_times(self, vdot, km_mi):            
        # get race from Model
        results = {}
        for v in range(vdot-2, vdot+3):
            try:
                results[v] = {race: self.model.get_time_from_vdot_and_race(v, race) for race in races}
            except:
                continue
        # output to View
        self.view.print_race_time_to_table(results, vdot)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('VDOT')
        self.geometry('1200x700')
        self.resizable(True, True)
        model = Model()
        view = View(self)
        controller = Controller(model, view)
        view.set_controller(controller)


if __name__ == "__main__":
    app = App()
    app.mainloop()
