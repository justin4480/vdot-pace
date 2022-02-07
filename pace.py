import numpy as np
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
import re


class Model:
    def __init__(self):
        self.lr_pace = {
            'e_min': {'coef': np.array([4.74049146e-05, 3.83990983e-04]),
                      'intercept': -0.000496647540619251},
            'e_max': {'coef': np.array([4.12734268e-05, 2.91041757e-04]),
                      'intercept': -0.0002086181081857063},
            'm': {'coef': np.array([5.20176045e-05, 5.60078308e-04]),
                  'intercept': -0.0011082739994069607},
            't': {'coef': np.array([5.15585827e-05, 5.76422687e-04]),
                  'intercept': -0.0009109768232632535},
            'i': {'coef': np.array([5.54231655e-05, 6.40550449e-04]),
                  'intercept': -0.0010179014592616746},
            'r': {'coef': np.array([8.02825088e-05, 1.38140603e-05]),
                   'intercept': 0.0005785616632812381},
        }
        self.lr_race = {
            'm': {'coef': np.array([1.35264281e-06, 5.55779711e-06]),
                  'intercept': -1.9773170200901904e-06},
        }
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
    
    def check_valid_intensity(self, intensity):
        if intensity not in self.lr_pace.keys():
            raise ValueError((
                f'intensity should be one of '
                f'{self.lr_pace.keys()}'
            ))
        else:
            return True

    def check_valid_km_mi(self, km_mi):
        if km_mi not in ['km', 'mi']:
            raise ValueError('km_mi should be km or mi')
        else:
            return True

    def get_pace_raw(self, vdot: int, intensity: str):
        coef, intercept = self.lr_pace[intensity].values()
        X = np.array([vdot, np.log(vdot)])
        return 1 / (intercept + (X.dot(coef)))

    def get_pace_formatted(self, vdot: int, intensity: str, km_mi: str):
        self.check_valid_vdot(vdot)
        self.check_valid_intensity(intensity)
        self.check_valid_km_mi(km_mi)
        convert = 0.621371 if km_mi == 'mi' else 1
        seconds = np.round(self.get_pace_raw(vdot, intensity) / convert, 0)
        pace = datetime.timedelta(seconds=seconds).__str__()
        return re.search(r'[1-9].*', pace).group()

    def get_race_raw(self, vdot: int, intensity: str):
        coef, intercept = self.lr_race[intensity].values()
        X = np.array([vdot, np.log(vdot)])
        return 1 / (intercept + (X.dot(coef)))

    def get_race_formatted(self, vdot: int, intensity: str, km_mi: str):
        self.check_valid_vdot(vdot)
        self.check_valid_intensity(intensity)
        self.check_valid_km_mi(km_mi)
        convert = 0.621371 if km_mi == 'mi' else 1
        seconds = np.round(self.get_race_raw(vdot, intensity) / convert, 0)
        pace = datetime.timedelta(seconds=seconds).__str__()
        return re.search(r'[1-9].*', pace).group()


class View(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        # field options
        options = {'padx': 5, 'pady': 5}

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
        self.km.grid(row=1, column=0, sticky=tk.W, padx=20)
        self.mi.grid(row=2, column=0, sticky=tk.W, padx=20)

        # vdot label
        self.vdot_label = ttk.Label(self, text='VDOT')
        self.vdot_label.grid(row=3, column=0, sticky=tk.W, **options)

        # vdot entry
        self.vdot = tk.StringVar()
        self.vdot_entry = ttk.Entry(self, textvariable=self.vdot)
        self.vdot_entry.grid(row=3, column=1, **options)
        self.vdot_entry.focus()

        # get button
        self.refresh_button = ttk.Button(self, text='Get pace')
        self.refresh_button['command'] = self.refresh_button_clicked
        self.refresh_button.grid(row=4, column=0, sticky=tk.W, **options)

        # pace table
        columns = ('vdot', 'e_pace', 'm_pace', 't_pace', 'i_pace', 'r_pace')
        self.pace_tree = ttk.Treeview(self, columns=columns,
                                 show='headings', height=5)
        self.pace_tree.column("vdot", anchor=tk.CENTER, stretch=tk.NO, width=50)
        self.pace_tree.column("e_pace", anchor=tk.CENTER, stretch=tk.NO, width=90)
        self.pace_tree.column("m_pace", anchor=tk.CENTER, stretch=tk.NO, width=60)
        self.pace_tree.column("t_pace", anchor=tk.CENTER, stretch=tk.NO, width=60)
        self.pace_tree.column("i_pace", anchor=tk.CENTER, stretch=tk.NO, width=60)
        self.pace_tree.column("r_pace", anchor=tk.CENTER, stretch=tk.NO, width=60)
        self.pace_tree.heading('vdot', text='VDOT')
        self.pace_tree.heading('e_pace', text='E pace')
        self.pace_tree.heading('m_pace', text='M pace')
        self.pace_tree.heading('t_pace', text='T pace')
        self.pace_tree.heading('i_pace', text='I pace')
        self.pace_tree.heading('r_pace', text='R pace')
        self.pace_tree.grid(row=5, columnspan=3, sticky=tk.W)

        # race table
        columns = ('vdot', '10k_time', 'm_time')
        self.race_tree = ttk.Treeview(self, columns=columns,
                                 show='headings', height=5)
        self.race_tree.column("vdot", anchor=tk.CENTER, stretch=tk.NO, width=50)
        self.race_tree.column("10k_time", anchor=tk.CENTER, stretch=tk.NO, width=90)
        self.race_tree.column("m_time", anchor=tk.CENTER, stretch=tk.NO, width=60)
        self.race_tree.heading('vdot', text='VDOT')
        self.race_tree.heading('10k_time', text='10k time')
        self.race_tree.heading('m_time', text='M time')
        self.race_tree.grid(row=6, columnspan=3, sticky=tk.W)

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

    def print_pace_to_table(self, records, vdot):
        self.pace_tree.delete(*self.pace_tree.get_children())
        for record in records:
            self.pace_tree.insert('', tk.END, values=record, iid=record[0])
        self.pace_tree.selection_set(vdot)

    def print_race_to_table(self, records, vdot):
        self.race_tree.delete(*self.race_tree.get_children())
        for record in records:
            self.race_tree.insert('', tk.END, values=record, iid=record[0])
        self.race_tree.selection_set(vdot)

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
        # get pace from Model
        results = []
        for i in range(vdot-2, vdot+3):
            try:
                e_min_pace = self.model.get_pace_formatted(i, 'e_min', km_mi)
                e_max_pace = self.model.get_pace_formatted(i, 'e_max', km_mi)
                e_pace = e_min_pace + ' - ' + e_max_pace
                m_pace = self.model.get_pace_formatted(i, 'm', km_mi)
                t_pace = self.model.get_pace_formatted(i, 't', km_mi)
                i_pace = self.model.get_pace_formatted(i, 'i', km_mi)
                r_pace = self.model.get_pace_formatted(i, 'r', km_mi)
                results.append((i, e_pace, m_pace, t_pace, i_pace, r_pace))
            except:
                continue
        # output to View
        self.view.print_pace_to_table(results, vdot)


    def get_race(self, vdot, km_mi):            
        # get race from Model
        results = []
        for i in range(vdot-2, vdot+3):
            try:
                m_race = self.model.get_race_formatted(i, 'm', km_mi)
                results.append((i, '', m_race))
            except:
                continue
        # output to View
        self.view.print_race_to_table(results, vdot)



class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('VDOT')
        self.geometry('500x500')
        self.resizable(True, True)
        model = Model()
        view = View(self)
        controller = Controller(model, view)
        view.set_controller(controller)


if __name__ == "__main__":
    app = App()
    app.mainloop()
