# https://www.itieffe.com/de/elektronischer-Strom/Allgemeine-Hinweise-f%C3%BCr-Elektrokabel/
import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
import time
from typing import Union

class Label(ttk.Label):
    bg_color = "#18007a"
    fg_color = "white"
    
    def __init__(self, parent, *, text:str="", font_size:int = 10, **kwargs) -> None:
        super().__init__(parent, text=text, font=("Arial", font_size), background=self.bg_color, foreground=self.fg_color, **kwargs) 

class App(tk.Tk):
    #window_width = 800
    #window_height = 600
    bg_color = "#18007a"
    pack_settings = {"side": "top", "anchor": "w"}
    
    def __init__(self) -> None:
        super().__init__()
        
        self.setup()
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.columnconfigure(2, weight=1)
        
        self.name_var = tk.StringVar()
        self.create_entry()

        self.label.grid(row=0, column=1, **{'padx': 5, 'pady': 15})
        self.output_frame.grid(row=2, column=1, sticky="wens",columnspan=1, pady=15)
        
    def setup(self) -> None:
        self.set_geometry()
        self.title("Kabelanalyse")
        self.configure(bg=f"{self.bg_color}", padx=20, pady=20)
        self.label = Label(self, text='Kabelanalyse', font_size=25)
        
    def set_geometry(self) -> None:

        # get the screen dimension
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.window_width = int(screen_width * 3 / 4)
        self.window_height = int(screen_height * 3 / 4)

        # find the center point
        center_x = int(screen_width/2 - self.window_width / 2)
        center_y = int(screen_height/2 - self.window_height / 2)

        # set the position of the window to the center of the screen
        self.geometry(f'{self.window_width}x{self.window_height}+{center_x}+{center_y}')

    def create_entry(self) -> None:

        padding = {'padx': 5, 'pady': 5}
        # label
        Label(self, text='Kabel:', font_size=15).grid(row=1, column=0,sticky="e", **padding)

        # Entry
        name_entry = ttk.Entry(self, textvariable=self.name_var)
        name_entry.grid(column=1, row=1, sticky="we",**padding)
        name_entry.focus()

        # Button
        submit_button = ttk.Button(self, text='Submit', command=self.submit)
        submit_button.grid(column=2, row=1, sticky="w", **padding)
        
        # Output frame
        self.output_frame = tk.Frame(self, bg=self.bg_color)

    def get_new_string(self, header:str, old_string:str) -> str:
        new_string = f'{header.replace("_", " ").capitalize()}: {old_string.split(";")[1]}'
        return new_string
    
    # Returns true if the string consists of cei2027 norm
    def isCei2027(self, string: str) -> bool:
        if string[0].isalpha():
            if len(string) and (string[0] == "H" or string[0] == "N" or string[0] == "A"):
                return True
        return False

    
    def getBauform(self, string: str) -> Union[tuple[str, str], tuple[None, str]]:
        # If string[1] is alpha, then string[0] is for sure the bauform
        # "idx_val" is the index where the new strings starts
        if string[1].isalpha() or string[1] == '-':
            idx_val = 1
        else:
            idx_val = 2

        pd_series = self.df.index[self.df["bauform_des_kabels"].str.contains(f"{string[:idx_val]};", na=False)]
        
        if len(pd_series):
            idx = pd_series[0]
            value = self.df.at[idx, "bauform_des_kabels"]
            return (value, string[idx_val:])

        return (None, string) 
    
    def getIsolatorOderMantel(self, string: str) -> Union[tuple[str, str], tuple[None, str]]:
        # If string[1] is alpha, then string[0] is for sure the isolation
        # "idx_val" is the index where the new strings starts
        if string[1].isalpha() or string[1] == "-":
            idx_val = 1
        else:
            idx_val = 2

        pd_series = self.df.index[self.df["isolator"].str.contains(f"{string[:idx_val]};", na=False)]
        if len(pd_series):
            idx = pd_series[0]
            value = self.df.at[idx, "isolator"]
            return (value, string[idx_val:])

        return (None, string) 

    # If the value can vary in length, they can get passed as as list of lengths
    def getValues(self, string: str, list_lengths ,header: str) -> str:
        # Reverse because "FF" and "F" are different things
        for len_val in reversed(list_lengths):
            if len(string) >= len_val:
                pd_series = self.df.index[self.df[header].str.contains(f"{string[0:len_val]};", na=False)]
                if len(pd_series):
                    idx = pd_series[0]
                    value = self.df.at[idx, header]
                    Label(self.output_frame, text=f"{self.get_new_string(header , value)}", font_size=15).pack(**self.pack_settings)

                    return string[len_val:]
        return string
    
    def cei2027(self, new_string: str) -> None:
        self.df = pd.read_excel("cei2027.xlsx")

        Label(self.output_frame, text=f"CEI2027 Norm!", font_size=15).pack(**self.pack_settings)

        # Normen
        curr_col = "normen"
        new_string = self.getValues(new_string, [1,], curr_col)

        # Nennspannung
        curr_col = "nennspannung"
        new_string = self.getValues(new_string, [2,], curr_col)
        
        # Isolator
        curr_col = "isolator"
        
        isolierung, new_string = self.getIsolatorOderMantel(new_string)
        Label(self.output_frame, text=f"{self.get_new_string(curr_col ,isolierung)}", font_size=15).pack(**self.pack_settings)

        # Mantel
        curr_col = "mantel"
        mantel, new_string = self.getIsolatorOderMantel(new_string)
        if not mantel:
            mantel = isolierung
        Label(self.output_frame, text=f"{self.get_new_string(curr_col ,mantel)}", font_size=15).pack(self.pack_settings)

        # Bauform des Kabels
        curr_col = "bauform_des_kabels"
        bauform, new_string = self.getBauform(new_string)
        if bauform:
            Label(self.output_frame, text=f"{self.get_new_string(curr_col ,bauform)}", font_size=15).pack(**self.pack_settings)
        
        if new_string[0] == "-":
            new_string = new_string[1:]
        else:
            return
        
        curr_col = "flexibilitätsgrad_des_leiters"
        new_string = self.getValues(new_string, [1,], curr_col)

            

        querschnitt = None
        if len(new_string) == 1:
            aderzahl = new_string[0]
            new_string = ""
        elif len(new_string) >= 2 :
            if new_string[0] == " ":
                aderzahl = 1
                querschnitt = new_string[1:]
            elif not new_string[0].isalpha():
                    aderzahl = new_string[0] 
                    new_string = new_string[1:]
                    new_string = self.getValues(new_string, [1, ], "schutzleiter")
                    if len(new_string):
                        querschnitt = new_string

            else:
                aderzahl = 1 

        else:
            aderzahl = 1

        Label(self.output_frame, text=f"Aderzahl: {aderzahl}", font_size=15).pack(**self.pack_settings)
        if querschnitt:
            Label(self.output_frame, text=f"Querschnitt: {querschnitt}mm^2", font_size=15).pack(**self.pack_settings)
    
    def cei35011(self, new_string: str)->None:
        new_string = new_string.replace(" ", "")
        self.df = pd.read_excel("cei35011.xlsx")

        Label(self.output_frame, text=f"CEI35011 Norm!", font_size=15).pack(**self.pack_settings)
        
        if not new_string[0].isalpha():
            aderzahl = new_string[0]
            Label(self.output_frame, text=f"Aderzahl: {aderzahl}", font_size=15).pack(**self.pack_settings)
            
            new_string = new_string[1:]

            curr_col = "schutzleiter"
            new_string = self.getValues(new_string, [1, ], curr_col)
            index = 0 
            while not new_string[index].isalpha() or new_string[index] == ",":
                index += 1
            
            querschnitt = new_string[:index]
            new_string = new_string[index:]
            Label(self.output_frame, text=f"Querschnitt: {querschnitt}mm^2", font_size=15).pack(**self.pack_settings)

        curr_col = "flexibilitätsgrad_des_leiters"
        new_string = self.getValues(new_string, [1, 2] ,curr_col)

        curr_col = "isolierung"
        new_string = self.getValues(new_string, [1, 2] ,curr_col)

        curr_col = "kabelform"
        new_string = self.getValues(new_string, [1, ] ,curr_col)

        curr_col = "bildschirme"
        new_string = self.getValues(new_string, [1, 2] ,curr_col)

        curr_col = "anker"
        new_string = self.getValues(new_string, [1, ] ,curr_col)

        curr_col = "mantel"
        new_string = self.getValues(new_string, [1, 2] ,curr_col)

        if new_string[0] == "-":
            new_string = new_string[1:]

        Label(self.output_frame, text=f"Nennspannung: {new_string}", font_size=15).pack(**self.pack_settings)
        
        
    def submit(self) -> None:
        new_string = self.name_var.get()

        # Delete Frame and recreate it to also delete labels
        self.output_frame.destroy()
        self.output_frame = tk.Frame(self, bg=self.bg_color)
        self.output_frame.grid(row=2, column=1, sticky="wens",columnspan=1)

        # If Norm is cei2027 execute funtion cei2027, else cei35011 
        if self.isCei2027(new_string):
            self.cei2027(new_string)
        else:
            self.cei35011(new_string)






def main() -> None:
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
