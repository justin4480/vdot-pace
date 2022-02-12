import numpy as np
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
import re

paces = {
    'e': 1.0,
    'm': 1.0,
    't': 1.0,
    'i': 1.0,
    'r': 1.0,
}

distances = {
    'meters': 0.001,
    'kilometers': 1.0,
    'miles': 1.60934,
}

races = {
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

pace_distance_and_weights = {
    'e': {
        'distance': 1.0,
        'weights': np.array([4949.27103996282, 35.90981260691225,
                            -1471.4577840422419, -10780.124357908137,
                            -0.20469289084241282, 0.0005847523343618377])},
    'm': {
        'distance': 1.0,
        'weights': np.array([5769.83766356983, 49.293532532288424,
                            -1810.3895026597256, -12851.045985015659,
                            -0.291126234807642, 0.0008304956752454018])},
    't': {
        'distance': 1.0,
        'weights': np.array([223.6265478238622, -5.763413154957469,
                            19.099113274553744, 6742.587058504519,
                            0.05418680896355041, -0.0002009103554740932])},
    'i': {
        'distance': 1.0,
        'weights': np.array([-1397.1455774707638, -20.7582565066043,
                            538.6711541187304, 12633.618023527979,
                            0.14848775051980745, -0.0004883293344164485])},
    'r': {
        'distance': 1.0,
        'weights': np.array([10660.490550384873, 130.77354304136978,
                            -3692.965990299492, -27355.696889999857,
                            -0.9608418286816445, 0.003311943788503413])},
    '1.5k': {
        'distance': 1.5,
        'weights': np.array([1182.085091699069, 6.367170440963579,
                            -322.778681874542, 7865.746434686376,
                            -0.03397766949704373, 0.00011018322157951843])},
    '1 mile': {
        'distance': 1.60934,
        'weights': np.array([2052.1357862906307, 12.837570671730337,
                            -589.4470042830931, 5178.5201067205235,
                            -0.06521400319947102, 0.00017038837722793687])},
    '3k': {
        'distance': 3.0,
        'weights': np.array([5579.688245963416, 32.668431971728005,
                            -1583.8426434415262, 1017.5046612753332,
                            -0.15706875781688723, 0.0003850029693239776])},
    '2 mile': {
        'distance': 3.21869,
        'weights': np.array([833.4078760596344, -11.445597212321871,
                            -49.24448692423541, 22360.06173224382,
                            0.11415994058425183, -0.0004261276107087042])},
    '5k': {
        'distance': 5.0,
        'weights': np.array([6928.740310588318, 37.654693906805804,
                            -1910.27798719494, 12948.72196202415,
                            -0.18413594536234612, 0.0004763364065638598])},
    '10k': {
        'distance': 10.0,
        'weights': np.array([11045.008738808692, 48.69849842830903,
                            -2919.2894591605072, 42237.01880476229,
                            -0.18713464363791843, 0.0003564040634955745])},
    '15k': {
        'distance': 15.0,
        'weights': np.array([22128.546722378185, 113.31445391803007,
                            -6060.291277969021, 41959.21146722964,
                            -0.5017832685670811, 0.0011604066030486138])},
    '1/2 marathon': {
        'distance': 21.0975,
        'weights': np.array([36453.132974194465, 190.89491161314612,
                            -10044.062274881275, 35179.734779269216,
                            -0.8700911886656826, 0.0020931669969286304])},
    'marathon': {
        'distance': 42.195,
        'weights': np.array([60636.22986513261, 246.74130046555726,
                            -15730.318846607715, 109197.36142110199,
                            -0.9739181072484939, 0.002111978999892017])},
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
    
    # def check_valid_intensity(self, intensity):
    #     if intensity not in self.lr_pace.keys():
    #         raise ValueError((
    #             f'intensity should be one of '
    #             f'{self.lr_pace.keys()}'
    #         ))
    #     else:
    #         return True

    # def check_valid_km_mi(self, km_mi):
    #     if km_mi not in ['km', 'mi']:
    #         raise ValueError('km_mi should be km or mi')
    #     else:
    #         return True

    @staticmethod
    def get_time_from_vdot_and_race(vdot, race):
        X = np.array([1, vdot, np.log(vdot), 1/vdot, vdot**2, vdot**3])
        w = pace_distance_and_weights[race]['weights']
        seconds = np.round(X @ w,)
        return datetime.timedelta(seconds=seconds)

    @staticmethod
    def get_pace_from_vdot_and_instensity(vdot, intensity):
        X = np.array([1, vdot, np.log(vdot), 1/vdot, vdot**2, vdot**3])
        w = pace_distance_and_weights[intensity]['weights']
        seconds = np.round(X @ w,)
        return datetime.timedelta(seconds=seconds)

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
        options = {'padx': 10, 'pady': 10}

        # km_mi label
        self.km_mi_label = ttk.Label(self, text='Km / Mile')
        self.km_mi_label.grid(row=0, column=0, sticky=tk.W, **options)

        # vdot entry
        self.km_mi = tk.StringVar()
        self.km_mi.set('mi')
        self.km = tk.Radiobutton(self, text='Km',
                                 variable=self.km_mi, value='km')
        self.mi = tk.Radiobutton(self, text='Mile',
                                 variable=self.km_mi, value='mi')
        self.km.grid(row=1, column=0, sticky=tk.W, padx=options['padx'])
        self.mi.grid(row=2, column=0, sticky=tk.W, padx=options['padx'])

        # vdot label
        self.vdot_label = ttk.Label(self, text='VDOT')
        self.vdot_label.grid(row=3, column=0, sticky=tk.W, **options)

        # vdot entry
        self.vdot = tk.StringVar()
        self.vdot_entry = ttk.Entry(self, textvariable=self.vdot)
        self.vdot_entry.grid(row=4, column=0, sticky=tk.W, padx=options['padx'])
        self.vdot_entry.focus()

        # get button
        self.refresh_button = ttk.Button(self, text='Refresh')
        self.refresh_button['command'] = self.refresh_button_clicked
        self.refresh_button.grid(row=5, column=0, sticky=tk.W, **options)

        # pace table
        columns = ['vdot'] + list(paces.keys())
        self.pace_tree = ttk.Treeview(self, columns=columns, show='headings', height=5)
        for column in columns:
            self.pace_tree.column(f"{column}", anchor=tk.CENTER, stretch=tk.NO, width=110)
            self.pace_tree.heading(f"{column}", text=f"{column}")
        self.pace_tree.grid(row=6, columnspan=3, sticky=tk.W, **options)

        # race table
        columns = ['vdot'] + list(races.keys())
        self.race_tree = ttk.Treeview(self, columns=columns, show='headings', height=5)
        for column in columns:
            self.race_tree.column(f"{column}", anchor=tk.CENTER, stretch=tk.NO, width=110)
            self.race_tree.heading(f"{column}", text=f"{column}")
        self.race_tree.grid(row=7, columnspan=3, sticky=tk.W, **options)

        # add padding to the frame and show it
        self.grid(padx=10, pady=10, sticky=tk.NSEW)
        
        # set the controller
        self.controller = None

    def set_controller(self, controller):
        self.controller = controller

    def refresh_button_clicked(self):
        if self.controller:
            self.controller.validate_vdot(int(self.vdot.get()))
            self.controller.get_pace(int(self.vdot.get()), self.km_mi.get())
            self.controller.get_race(int(self.vdot.get()), self.km_mi.get())

    def print_pace_to_table(self, records, users_vdot):
        self.pace_tree.delete(*self.pace_tree.get_children())
        for vdot, times in records.items():
            values = [vdot] + [format_time(time) for time in times.values()]
            self.pace_tree.insert('', tk.END, values=values, iid=vdot)
        self.pace_tree.selection_set(users_vdot)

    def print_race_to_table(self, records, users_vdot):
        self.race_tree.delete(*self.race_tree.get_children())
        for vdot, times in records.items():
            values = [vdot] + [format_time(time) for time in times.values()]
            self.race_tree.insert('', tk.END, values=values, iid=vdot)
        self.race_tree.selection_set(users_vdot)

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

    def get_pace(self, vdot, km_mi):
        """
        returns dictionary of paces for all avalible intensities over a range of vdots
        """
        # get pace from Model
        results = {}
        for v in range(vdot-2, vdot+3):
            try:
                results[v] = {pace: self.model.get_pace_from_vdot_and_instensity(v, pace) for pace in paces}
            except:
                continue
        # output to View
        self.view.print_pace_to_table(results, vdot)


    def get_race(self, vdot, km_mi):            
        # get race from Model
        results = {}
        for v in range(vdot-2, vdot+3):
            try:
                results[v] = {race: self.model.get_time_from_vdot_and_race(v, race) for race in races}
            except:
                continue
        # output to View
        self.view.print_race_to_table(results, vdot)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('VDOT')
        self.geometry('1200x500')
        self.resizable(True, True)
        model = Model()
        view = View(self)
        controller = Controller(model, view)
        view.set_controller(controller)


if __name__ == "__main__":
    app = App()
    app.mainloop()
