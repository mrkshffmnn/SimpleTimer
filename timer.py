import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import time

class TimerApp(ctk.CTk):

    COLOR_SCHEME = {
        "DARKER_GREY": "#2E2E2E",
        "DARK_GREY": "#404040",
        "LIGHT_GREY": "#D3D3D3",
        "BLUE": "#0078D7",
        "ORANGE": "#ff8c00",
        "RED": "#ff0000",
        "WHITE": "#ffffff"
    }

    def __init__(self):
        super().__init__()

        self.title('Simple Timer App')
        self.geometry('500x160')

        # Initialize customtkinter
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.main_frame = ctk.CTkFrame(master=self, fg_color=self.COLOR_SCHEME["DARKER_GREY"])
        self.main_frame.pack(fill="both", expand=True)  # Make sure it fills the whole window

        self.standard_frame = ctk.CTkFrame(master=self.main_frame, fg_color=self.COLOR_SCHEME["DARK_GREY"])
        self.standard_frame.pack(pady=5)

        # Creating a frame for predefined minutes and start button
        self.quick_select_frame = ctk.CTkFrame(master=self.main_frame, fg_color=self.COLOR_SCHEME["DARK_GREY"])
        self.quick_select_frame.pack(pady=5)

        self.minute_input = ctk.CTkEntry(master=self.standard_frame, width=120, placeholder_text="Enter minutes here")
        self.minute_input.grid(row=0, column=0, padx=4, sticky="ew")

        self.start_button = ctk.CTkButton(master=self.standard_frame, text="Start", command=self.start_timer, width=32, height=32)
        self.start_button.grid(row=0, column=1, padx=4)

        self.quick_minutes = [15, 20, 30, 45, 60]
        for i, mins in enumerate(self.quick_minutes):
            btn = ctk.CTkButton(master=self.quick_select_frame, text=f"{mins} min", width=32, height=32,
                                command=lambda m=mins: self.start_timer(m))
            btn.grid(row=0, column=i, padx=4, pady=4, sticky="ew")


        self.timer_frame = ctk.CTkFrame(master=self.main_frame, fg_color=self.COLOR_SCHEME["DARK_GREY"])
        self.timer_label = ctk.CTkLabel(master=self.timer_frame, text="", width=120)
        self.timer_label.pack(side=tk.LEFT, padx=(20, 10))

        self.pause_button = ctk.CTkButton(master=self.timer_frame, text="Pause")
        self.pause_button.pack(side=tk.LEFT)
        self.pause_button.configure(command=self.pause_resume_timer) 


        self.progress_bar = ctk.CTkProgressBar(master=self.main_frame, width=300)
        self.progress_bar.set(0)

        self.remaining_time = 0
        self.is_running = False
        self.is_paused = False
        self.timer_thread = None
        self.blinking = False
        self.blink_id = None

        self.bind('<Return>', lambda event: self.start_timer())
        self.bind('<Escape>', lambda event: self.stop_timer())

    def display_time(self, seconds):
        minutes = seconds // 60
        seconds %= 60
        self.timer_label.configure(text=f"{minutes:02}:{seconds:02}")

    def update_timer(self):
        while self.is_running:
            time.sleep(1)
            if self.is_paused:
                continue
            self.remaining_time -= 1
            self.display_time(self.remaining_time)
            self.update_progress_bar_color()
            progress = self.remaining_time / self.total_seconds
            self.progress_bar.set(progress)
            if self.remaining_time <= 0:
                self.is_running = False
                self.blink_background()
                break

    def start_timer(self, minutes=None):
        if minutes is None:
            try:
                minutes = int(self.minute_input.get())
            except ValueError:
                messagebox.showerror("Error", "Please enter a positive integer for minutes.")
                return
            
        if minutes <= 0:
            messagebox.showerror("Error", "Please enter a positive integer for minutes.")
            return
        
        self.total_seconds = minutes * 60
        self.remaining_time = self.total_seconds
        self.is_running = True
        self.display_time(self.remaining_time)
        
        self.quick_select_frame.pack_forget()
        self.standard_frame.pack_forget()
        self.timer_frame.pack(pady=20)
        self.pause_button.pack(side=tk.LEFT)
        self.progress_bar.pack(pady=(0, 20))
        self.progress_bar.set(1)

        self.timer_thread = threading.Thread(target=self.update_timer)
        self.timer_thread.start()

    def stop_timer(self):
        self.is_running = False
        self.is_paused = False
        if self.blink_id:
            self.after_cancel(self.blink_id)
            self.blink_id = None
    
        self.main_frame.configure(fg_color=self.COLOR_SCHEME["DARKER_GREY"])
        self.timer_frame.configure(fg_color=self.COLOR_SCHEME["DARK_GREY"])  # Reset to original bg
        self.standard_frame.pack(pady=12)
        self.quick_select_frame.pack(pady=12)
        self.timer_frame.pack_forget()
        self.pause_button.pack_forget()
        self.progress_bar.pack_forget()
        if self.timer_thread:
            self.timer_thread.join(0.1)
            self.timer_thread = None

    def pause_resume_timer(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_button.configure(text="Resume")
        else:
            self.pause_button.configure(text="Pause")

    def update_progress_bar_color(self):
        proportion = self.remaining_time / self.total_seconds
        if proportion > 0.10:
            color = self.COLOR_SCHEME['BLUE']
        elif proportion > 0.05:
            color = self.COLOR_SCHEME['ORANGE']
        else:
            color = self.COLOR_SCHEME['RED']
        # Update progress bar with the new color
        self.progress_bar.configure(progress_color=color)

    def blink_background(self, blink_times=20, on_time=400, off_time=400):
        self.blinking = True

        def _blink():
            nonlocal blink_times
            if blink_times > 0:
                new_color = self.COLOR_SCHEME["LIGHT_GREY"] if blink_times % 2 == 0 else self.COLOR_SCHEME["DARK_GREY"]
                #wrong
                self.timer_frame.configure(fg_color=new_color)  # Change the main_frame color
                blink_times -= 1
                self.after(on_time if blink_times % 2 == 0 else off_time, _blink)
            else:
                self.main_frame.configure(fg_color=self.COLOR_SCHEME["LIGHT_GREY"])  # Set the main_frame color to light grey permanently
                self.blinking = False

        self.blink_id = self.after(0, _blink)

if __name__ == "__main__":
    app = TimerApp()
    app.mainloop()