import tkinter as tk
from calendar import monthrange, month_name
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import os

os.environ['TCL_LIBRARY'] = r'C:\Users\trist\AppData\Local\Programs\Python\Python313\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\trist\AppData\Local\Programs\Python\Python313\tcl\tk8.6'

cred = credentials.Certificate('Scheduler.json')  
firebase_admin.initialize_app(cred)
db = firestore.client()

class Calendar:
    def __init__(self, master):
        self.master = master
        self.year = datetime.now().year
        self.month = datetime.now().month
        self.cal_frame = tk.Frame(master, bg='#EDF2F4', bd=10, relief='groove')
        self.cal_frame.pack(fill='both', expand=True)
        self.trainings = {}
        self.create_header()
        self.create_calendar()
        self.update_clock()

    def create_header(self):
        header_frame = tk.Frame(self.cal_frame, bg='#EDF2F4')
        header_frame.pack(fill='x')

        title_label = tk.Label(header_frame, text="Training Schedule", font=('Inter', 24, 'bold'), bg='#EDF2F4', fg='#5438DC')
        title_label.pack(pady=10)

        search_frame = tk.Frame(header_frame, bg='#EDF2F4')
        search_frame.pack(pady=10)

        self.search_entry = tk.Entry(search_frame, width=30, font=('Helvetica', 12), bg='white')
        self.search_entry.pack(side=tk.LEFT, padx=5)

        search_button = tk.Button(search_frame, text="Search", font=('Helvetica', 12), command=self.search_function, bg='#8D99AE', fg='white', borderwidth=0, relief='flat')
        search_button.pack(side=tk.LEFT)

    def create_calendar(self):
        for widget in self.cal_frame.winfo_children():
            if widget != self.cal_frame.winfo_children()[0]:
                widget.destroy()

        self.clock_label = tk.Label(self.cal_frame, text=self.get_current_time(), font=('Helvetica', 14), bg='#EDF2F4', fg='#5438DC')
        self.clock_label.pack(pady=10)

        add_training_button = tk.Button(self.cal_frame, text="Add New Training Schedule", font=('Helvetica', 14), command=self.add_training_form, bg='#EF233C', fg='white', borderwidth=0, relief='flat')
        add_training_button.pack(fill='x', padx=10, pady=10)

        month_label = tk.Label(self.cal_frame, text=f"{month_name[self.month]} {self.year}", font=('Helvetica', 22, 'bold'), bg='#EDF2F4', fg='#5438DC')
        month_label.pack(pady=10)

        control_frame = tk.Frame(self.cal_frame, bg='#EDF2F4')
        control_frame.pack(fill='x')

        prev_button = tk.Button(control_frame, text='<', font=('Helvetica', 14), command=self.prev_month, bg='#8D99AE', fg='white', borderwidth=0, relief='flat')
        prev_button.pack(side='left', padx=10, pady=10)

        next_button = tk.Button(control_frame, text='>', font=('Helvetica', 14), command=self.next_month, bg='#8D99AE', fg='white', borderwidth=0, relief='flat')
        next_button.pack(side='right', padx=10, pady=10)

        grid_frame = tk.Frame(self.cal_frame, bg='#EDF2F4')
        grid_frame.pack(fill='both', expand=True)

        week_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(week_days):
            label = tk.Label(grid_frame, text=day, font=('Helvetica', 12), bg='#EDF2F4', fg='#5438DC')
            label.grid(row=0, column=i, padx=5, pady=5, sticky='nsew')

        num_days = monthrange(self.year, self.month)[1]
        for i in range(1, num_days + 1):
            day_button = tk.Button(grid_frame, text=str(i), font=('Helvetica', 12), width=5, command=lambda day=i: self.day_clicked(day), bg='#EF233C', fg='white', borderwidth=0, relief='flat')
            day_button.grid(row=(i - 1) // 7 + 1, column=(i - 1) % 7, padx=5, pady=5, sticky='nsew')

        for i in range(7):
            grid_frame.grid_columnconfigure(i, weight=1)
        for i in range(6):
            grid_frame.grid_rowconfigure(i, weight=1)

    def get_current_time(self):
        return datetime.now().strftime("%H:%M:%S")

    def update_clock(self):
        self.clock_label.config(text=self.get_current_time())
        self.master.after(1000, self.update_clock)

    def add_training_form(self):
        popup = tk.Toplevel(self.master)
        popup.title("Add New Training Schedule")
        popup.configure(bg='#EDF2F4')

        trainer_label = tk.Label(popup, text="Trainer:", font=('Helvetica', 12), bg='#EDF2F4', fg='#5438DC')
        trainer_label.pack(pady=10)

        self.trainer_entry = tk.Entry(popup, font=('Helvetica', 12), bg='white')
        self.trainer_entry.pack(fill='x', padx=10, pady=10)

        training_type_label = tk.Label(popup, text="Training Type:", font=('Helvetica', 12), bg='#EDF2F4', fg='#5438DC')
        training_type_label.pack(pady=10)

        self.training_type_entry = tk.Entry(popup, font=('Helvetica', 12), bg='white')
        self.training_type_entry.pack(fill='x', padx=10, pady=10)

        participants_label = tk.Label(popup, text="Participants:", font=('Helvetica', 12), bg='#EDF2F4', fg='#5438DC')
        participants_label.pack(pady=10)

        self.participants_text = tk.Text(popup, height=5, width=30, font=('Helvetica', 12), bg='white')
        self.participants_text.pack(pady=10)
        self.participants_text.insert('1.0', '- ')
        self.participants_text.bind('<Return>', self.add_bullet)

        time_label = tk.Label(popup, text="Time (HH:MM):", font=('Helvetica', 12), bg='#EDF2F4', fg='#5438DC')
        time_label.pack(pady=10)

        self.time_entry = tk.Entry(popup, font=('Helvetica', 12), bg='white')
        self.time_entry.pack(fill='x', padx=10, pady=10)

        add_button = tk.Button(popup, text="Select Dates", font=('Helvetica', 12), command=lambda: self.select_dates(popup))
        add_button.pack(pady=10)

    def add_bullet(self, event):
        cursor_position = self.participants_text.index(tk.INSERT)
        self.participants_text.insert(cursor_position, '\n- ')
        self.participants_text.mark_set(tk.INSERT, cursor_position + ' + 2 chars')
        return "break"

    def select_dates(self, popup):
        self.trainer = self.trainer_entry.get()
        self.training_type = self.training_type_entry.get()
        self.participants = self.participants_text.get('1.0', 'end-1c').split('\n- ')
        self.time = self.time_entry.get()

        popup.destroy()

        add_popup = tk.Toplevel(self.master)
        add_popup.title("Select Dates")
        add_popup.configure(bg='#EDF2F4')

        calendar_frame = tk.Frame(add_popup, bg='#EDF2F4')
        calendar_frame.pack(fill='both', expand=True)

        week_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(week_days):
            label = tk.Label(calendar_frame, text=day, font=('Helvetica', 12), bg='#EDF2F4', fg='#5438DC')
            label.grid(row=0, column=i, padx=5, pady=5, sticky='nsew')

        num_days = monthrange(self.year, self.month)[1]
        self.day_buttons = []
        self.selected_days = []

        for i in range(1, num_days + 1):
            day_button = tk.Button(calendar_frame, text=str(i), font=('Helvetica', 12), width=5, command=lambda day=i: self.add_day(day, add_popup), bg='#EF233C', fg='white', borderwidth=0, relief='flat')
            day_button.grid(row=(i - 1) // 7 + 1, column=(i - 1) % 7, padx=5, pady=5, sticky='nsew')
            self.day_buttons.append(day_button)

        add_button = tk.Button(add_popup, text="Add Training", font=('Helvetica', 12), command=lambda: self.add_training(add_popup))
        add_button.pack(pady=10)

    def add_day(self, day, popup):
        if day not in self.selected_days:
            self.selected_days.append(day)
            for button in self.day_buttons:
                if button['text'] == str(day):
                    button.config(bg='#8D99AE', fg='white')
        else:
            self.selected_days.remove(day)
            for button in self.day_buttons:
                if button['text'] == str(day):
                    button.config(bg='#EF233C', fg='white')

    def add_training(self, popup):
        for day in self.selected_days:
            training_data = {
                'trainer': self.trainer,
                'training_type': self.training_type,
                'participants': self.participants,
                'time': self.time,
                'date': f"{self.year}-{self.month:02d}-{day:02d}"
            }
            db.collection('trainings').add(training_data)
        popup.destroy()

    def search_function(self):
        search_query = self.search_entry.get()
        query = db.collection('trainings').where('trainer', '==', search_query).stream()

        results = []
        for doc in query:
            training = doc.to_dict()
            results.append(training)

        if results:
            self.display_search_results(results)
        else:
            print("No trainings found for this trainer.")

    def display_search_results(self, results):
        result_popup = tk.Toplevel(self.master)
        result_popup.title("Search Results")
        result_popup.configure(bg='#EDF2F4')

        header_label = tk.Label(result_popup, text="Search Results", font=('Helvetica', 18, 'bold'), bg='#EDF2F4', fg='#5438DC')
        header_label.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        canvas = tk.Canvas(result_popup, bg='#EDF2F4')
        scrollbar = tk.Scrollbar(result_popup, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#EDF2F4')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')

        canvas.grid(row=1, column=0, sticky='nsew')
        scrollbar.grid(row=1, column=1, sticky='ns')

        result_popup.grid_rowconfigure(1, weight=1)
        result_popup.grid_columnconfigure(0, weight=1)

        for i, result in enumerate(results):
            training_frame = tk.Frame(scrollable_frame, bg='white', highlightbackground='#007bff', highlightthickness=1, bd=2)
            training_frame.pack(fill='x', padx=10, pady=10)

            date_label = tk.Label(training_frame, text=f"Date: {result['date']}", font=('Helvetica', 12, 'bold'), bg='white', fg='#5438DC')
            date_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')

            time_label = tk.Label(training_frame, text=f"Time: {result['time']}", font=('Helvetica', 12), bg='white', fg='#333')
            time_label.grid(row=0, column=1, padx=10, pady=5, sticky='w')

            training_type_label = tk.Label(training_frame, text=f"Training Type: {result['training_type']}", font=('Helvetica', 12), bg='white', fg='#333')
            training_type_label.grid(row=1, column=0, padx=10, pady=5, sticky='w')

            trainer_label = tk.Label(training_frame, text=f"Trainer: {result['trainer']}", font=('Helvetica', 12), bg='white', fg='#333')
            trainer_label.grid(row=1, column=1, padx=10, pady=5, sticky='w')

            participants_label = tk.Label(training_frame, text="Participants:", font=('Helvetica', 12, 'bold'), bg='white', fg='#5438DC')
            participants_label.grid(row=2, column=0, padx=10, pady=5, sticky='w')

            participants_names = tk.Label(training_frame, text='\n'.join(f'- {name}' for name in result['participants']), font=('Helvetica', 12), bg='white', fg='#333', justify='left')
            participants_names.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky='w')

        canvas.configure(yscrollcommand=scrollbar.set)

        result_popup.grid_rowconfigure(0, weight=0)  
        result_popup.grid_rowconfigure(1, weight=1)  
        result_popup.grid_rowconfigure(2, weight=0)  
        result_popup.grid_columnconfigure(0, weight=1) 

    def day_clicked(self, day):
        selected_date = f"{self.year}-{self.month:02d}-{day:02d}"
        query = db.collection('trainings').where('date', '==', selected_date).stream()
        results = [doc.to_dict() for doc in query]

        self.zoom_frame = tk.Frame(self.cal_frame, bg='white', highlightbackground='#007bff', highlightthickness=1)
        self.zoom_frame.place(relx=0.5, rely=0.5, anchor='center')

        if results:
            grid_frame = tk.Frame(self.zoom_frame, bg='white')
            grid_frame.pack(fill='both', expand=True)

            for i, training in enumerate(results):
                sticky_note = tk.Frame(grid_frame, bg='white', highlightbackground='#007bff', highlightthickness=1)
                sticky_note.grid(row=i // 3, column=i % 3, padx=10, pady=10, sticky='nsew')

                training_type_label = tk.Label(sticky_note, text=f"Training Type: {training['training_type']}", font=('Helvetica', 12), bg='white')
                training_type_label.pack(pady=10)

                trainer_label = tk.Label(sticky_note, text=f"Trainer: {training['trainer']}", font=('Helvetica', 12), bg='white')
                trainer_label.pack(pady=10)

                time_label = tk.Label(sticky_note, text=f"Time: {training['time']}", font=('Helvetica', 12), bg='white')
                time_label.pack(pady=10)

                participants_label = tk.Label(sticky_note, text="Participants:", font=('Helvetica', 12), bg='white')
                participants_label.pack(pady=10)

                participants_names = tk.Label(sticky_note, text='\n'.join(f'- {name}' for name in training['participants']), font=('Helvetica', 12), bg='white')
                participants_names.pack(pady=10)

            for i in range((len(results) + 2) // 3):
                grid_frame.grid_rowconfigure(i, weight=1)
            for i in range(3):
                grid_frame.grid_columnconfigure(i, weight=1)
        else:
            no_trainings_label = tk.Label(self.zoom_frame, text="No trainings for this day.", font=('Helvetica', 12), bg='white')
            no_trainings_label.pack(pady=10)

        close_button = tk.Button(self.zoom_frame, text="Close", font=('Helvetica', 12), command=self.close_zoom)
        close_button.pack(pady=10)


    def close_zoom(self):
        self.zoom_frame.destroy()

    def prev_month(self):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self.create_calendar()

    def next_month(self):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.create_calendar()

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Training Schedule Management")
    root.geometry("600x700")
    app = Calendar(root)
    root.mainloop()
    
