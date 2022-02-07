import numpy as np
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
import re


class Model:
    def __init__(self):
        self.linear_regression_stats = {
            'm': {'coef': np.array([5.20176045e-05, 5.60078308e-04]),
                  'intercept': -0.0011082739994069607},
            't': {'coef': np.array([5.15585827e-05, 5.76422687e-04]),
                  'intercept': -0.0009109768232632535},
            'i': {'coef': np.array([5.54231655e-05, 6.40550449e-04]),
                  'intercept': -0.0010179014592616746},
            'r': {'coef': np.array([8.02825088e-05, 1.38140603e-05]),
                   'intercept': 0.0005785616632812381},
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
        if intensity not in self.linear_regression_stats.keys():
            raise ValueError((
                f'intensity should be one of '
                f'{self.linear_regression_stats.keys()}'
            ))
        else:
            return True

    def check_valid_km_mi(self, km_mi):
        if km_mi not in ['km', 'mi']:
            raise ValueError('km_mi should be km or mi')
        else:
            return True

    def get_sec_per_km(self, vdot: int, intensity: str):
        coef, intercept = self.linear_regression_stats[intensity].values()
        X = np.array([vdot, np.log(vdot)])
        return 1 / (intercept + (X.dot(coef)))

    def get_min_per_distance(self, vdot: int, intensity: str, km_mi: str):
        self.check_valid_vdot(vdot)
        self.check_valid_intensity(intensity)
        self.check_valid_km_mi(km_mi)
        convert = 0.621371 if km_mi == 'mi' else 1
        seconds = np.round(self.get_sec_per_km(vdot, intensity) / convert, 0)
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
        self.get_pace_button = ttk.Button(self, text='Get pace')
        self.get_pace_button['command'] = self.get_pace_button_clicked
        self.get_pace_button.grid(row=4, column=0, sticky=tk.W, **options)

        # table
        columns = ('vdot', 'e_pace', 'm_pace', 't_pace', 'i_pace', 'r_pace')
        self.tree = ttk.Treeview(self, columns=columns,
                                 show='headings', height=5)
        self.tree.column("vdot", anchor=tk.CENTER, stretch=tk.NO, width=50)
        self.tree.column("e_pace", anchor=tk.CENTER, stretch=tk.NO, width=70)
        self.tree.column("m_pace", anchor=tk.CENTER, stretch=tk.NO, width=70)
        self.tree.column("t_pace", anchor=tk.CENTER, stretch=tk.NO, width=70)
        self.tree.column("i_pace", anchor=tk.CENTER, stretch=tk.NO, width=70)
        self.tree.column("r_pace", anchor=tk.CENTER, stretch=tk.NO, width=70)
        self.tree.heading('vdot', text='VDOT')
        self.tree.heading('e_pace', text='E pace')
        self.tree.heading('m_pace', text='M pace')
        self.tree.heading('t_pace', text='T pace')
        self.tree.heading('i_pace', text='I pace')
        self.tree.heading('r_pace', text='R pace')
        self.tree.grid(row=5, columnspan=3)

        # add padding to the frame and show it
        self.grid(padx=10, pady=10, sticky=tk.NSEW)
        
        # set the controller
        self.controller = None

    def set_controller(self, controller):
        self.controller = controller

    def get_pace_button_clicked(self):
        if self.controller:
            self.controller.get_pace(int(self.vdot.get()), self.km_mi.get())

    def print_pace_to_table(self, records, vdot):
        self.tree.delete(*self.tree.get_children())
        for record in records:
            self.tree.insert('', tk.END, values=record, iid=record[0])
        self.tree.selection_set(vdot)

    def show_error(self, message):
        showerror(title='Error', message=message)


class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def get_pace(self, vdot, km_mi):
        try:
            self.model.check_valid_vdot(vdot)
        except ValueError as error:
            self.view.show_error(error)
            
        # get pace from Model
        results = []
        for i in range(vdot-2, vdot+3):
            try:
                m_pace = self.model.get_min_per_distance(i, 'm', km_mi)
                t_pace = self.model.get_min_per_distance(i, 't', km_mi)
                i_pace = self.model.get_min_per_distance(i, 'i', km_mi)
                r_pace = self.model.get_min_per_distance(i, 'r', km_mi)
                results.append((i, '', m_pace, t_pace, i_pace, r_pace))
            except:
                continue
        # output to View
        self.view.print_pace_to_table(results, vdot)



class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('VDOT')
        self.geometry('500x300')
        self.resizable(True, True)
        model = Model()
        view = View(self)
        controller = Controller(model, view)
        view.set_controller(controller)


if __name__ == "__main__":
    app = App()
    app.mainloop()
