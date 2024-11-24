import tkinter as tk  
from tkinter import messagebox, ttk
from tkinter import filedialog  
import database  
import csv  
import re 
from datetime import datetime
from ttkbootstrap.dialogs import Messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from ttkbootstrap import Style


class AccidentManagementApp:
    def __init__(self, root):
        self.style = Style(theme='superhero')
        self.root = root
        self.root.title("Система управління ДТП")
        self.root.geometry("900x700")

        # Конфігурація стилів
        self.style.configure('primary.TButton', font=('Helvetica', 10), padding=5)

        # Підключення до бази даних
        self._conn = database.create_connection("accident.db")
        database.create_tables(self._conn)

        # Панель з вкладками
        self._tab_control = ttk.Notebook(self.root, style='primary.TNotebook')
        self._accident_tab = ttk.Frame(self._tab_control, padding=10)
        self._participant_tab = ttk.Frame(self._tab_control, padding=10)
        self._vehicle_tab = ttk.Frame(self._tab_control, padding=10)
        self._view_tab = ttk.Frame(self._tab_control, padding=10)

        self._tab_control.add(self._accident_tab, text='ДТП')
        self._tab_control.add(self._participant_tab, text='Учасники')
        self._tab_control.add(self._vehicle_tab, text='Транспортні засоби')
        self._tab_control.add(self._view_tab, text='Перегляд даних')

        # Додаємо панель вкладок до вікна
        self._tab_control.pack(expand=1, fill="both")
    

        # Викликаємо методи створення вкладок
        self.create_accident_tab()
        self.create_participant_tab()
        self.create_vehicle_tab()
        self.create_view_tab()

        
    def create_accident_tab(self):
        # Create a canvas and a frame for the form inside the canvas
        canvas = tk.Canvas(self._accident_tab)
        form_frame = ttk.Frame(canvas)

        # Scrollbar for the canvas
        v_scrollbar = ttk.Scrollbar(self._accident_tab, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=v_scrollbar.set)

        # Place the canvas and scrollbar in the Accident tab
        canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")

        # Configure grid weights for expandable canvas
        self._accident_tab.grid_rowconfigure(0, weight=1)
        self._accident_tab.grid_columnconfigure(0, weight=1)

        # Create a window inside the canvas to hold the form_frame
        canvas.create_window((0, 0), window=form_frame, anchor="nw")

        # Fields for the accident form
        fields = [
            ("Дата ДТП (ДД.ММ.РРРР):", "date"),
            ("Час доби:", "time_of_day", ["Вибрати...", "День", "Ніч", "Сутінки"]),
            ("Місце ДТП:", "location"),
            ("Опис:", "description"),
            ("Кількість учасників:", "participants_count"),
            ("Умови погоди:", "weather_condition", ["Вибрати...", "Сонячно", "Дощ", "Сніг", "Туман", "Інше"]),
            ("Освітлення:", "lighting_condition", ["Вибрати...", "Добре", "Недостатнє", "Темно"]),
            ("Стан дороги:", "road_condition", ["Вибрати...", "Сухо", "Волого", "Ожеледь", "Пошкоджено"]),
            ("Тип транспортного засобу:", "vehicle_type", ["Вибрати...", "Легковий", "Вантажний", "Мотоцикл", "Велосипед", "Інше"]),
            ("Тип дороги:", "road_type", ["Вибрати...", "Автострада", "Місцева дорога", "Внутрішній проїзд"]),
            ("Покриття дороги:", "road_surface", ["Вибрати...", "Асфальт", "Бетон", "Бруківка", "Грунт"]),
            ("Обмеження швидкості:", "speed_limit", ["Вибрати...", "20 км/г", "40 км/г", "60 км/г", "80 км/г", "100 км/г", "120 км/г"]),
            ("Тяжкість:", "severity", ["Вибрати...", "Легка", "Середня", "Важка"]),
            ("Опис пошкодження майна:", "property_damage_description"),
            ("Оцінка збитків:", "estimated_damage"),
            ("Час прибуття екстрених служб:", "emergency_response_time"),
            ("Номер поліцейського протоколу:", "police_report"),
            ("Номер страхового випадку:", "insurance_case_number"),
            ("Статус розслідування:", "investigation_status", ["Вибрати...", "Триває", "Завершено", "Призупинено"])
        ]

        # Populate the form frame with labels and entries/dropdowns
        for i, field in enumerate(fields):
            label = ttk.Label(form_frame, text=field[0], style='header.TLabel')
            label.grid(row=i, column=0, sticky="e", padx=5, pady=2)

            if len(field) == 3:  # Drop-down field
                var = tk.StringVar(form_frame)
                var.set(field[2][0])  # Default value
                dropdown = ttk.OptionMenu(form_frame, var, *field[2])
                dropdown.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
                setattr(self, f"_{field[1]}_var", var)
            else:  # Regular entry field
                entry = ttk.Entry(form_frame, width=30)
                entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
                setattr(self, f"_{field[1]}_entry", entry)

        # Add "Add Accident" button at the bottom of the form
        add_button = ttk.Button(form_frame, text="Додати ДТП", style='primary.TButton', command=self.add_accident)
        add_button.grid(row=len(fields), column=0, columnspan=2, pady=10)

        # Update scroll region after the form frame is populated
        form_frame.update_idletasks()  # Ensure frame is fully rendered
        canvas.config(scrollregion=canvas.bbox("all"))

        # Bind mouse wheel scrolling
        def _on_mouse_wheel(event):
            canvas.yview_scroll(-1 * (event.delta // 120), "units")

        canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

    def create_participant_tab(self):
        # Similar layout adjustments for participant inputs
        fields = [
            ("Ім'я учасника:", "name"),
            ("Роль:", "role", ["Вибрати...", "Водій", "Пасажир", "Пішохід", "Свідок"]),
            ("Травми:", "injuries"),
            ("Тяжкість травм:", "injury_severity", ["Вибрати...", "Легкі", "Середні", "Важкі"]),
            ("Госпіталізований:", "hospitalized", ["Вибрати...", "Так", "Ні"]),
            ("Вік:", "age"),
            ("Стать:", "gender", ["Вибрати...", "Чоловіча", "Жіноча"]),
            ("Номер водійського посвідчення:", "driver_license_number"),
            ("Статус посвідчення:", "license_status", ["Вибрати...", "Чинне", "Призупинене", "Анульоване"]),
            ("Категорія посвідчення:", "license_category", ["Вибрати...", "A", "B", "C", "D", "BE", "CE", "DE"]),
            ("Номер страхового полісу:", "insurance_policy_number"),
            ("Результат тесту на алкоголь:", "alcohol_test_result", ["Вибрати...", "Негативний", "Позитивний"]),
            ("Результат тесту на наркотики:", "drug_test_result", ["Вибрати...","Негативний", "Позитивний"]),
            ("Показання:", "statement"),
            ("ID ДТП:", "accident_id")
        ]

        for i, field in enumerate(fields):
            label = ttk.Label(self._participant_tab, text=field[0], style='header.TLabel')
            label.grid(row=i, column=0, sticky="e", padx=5, pady=2)

            if len(field) == 3:  # Dropdown
                var = tk.StringVar(self._participant_tab)
                var.set(field[2][0])
                dropdown = ttk.OptionMenu(self._participant_tab, var, *field[2])
                dropdown.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
                setattr(self, f"_{field[1]}_var", var)
            else:
                entry = ttk.Entry(self._participant_tab, width=30)
                entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
                setattr(self, f"_{field[1]}_entry", entry)

        # Add Participant Button
        add_button = ttk.Button(self._participant_tab, text="Додати учасника", style='primary.TButton', command=self.add_participant)
        add_button.grid(row=len(fields), column=0, columnspan=2, pady=10)

    def create_vehicle_tab(self):
        fields = [
            ("Тип транспортного засобу:", "vehicle_type", ["Вибрати...", "Легковий", "Вантажний", "Мотоцикл", "Велосипед", "Інше"]),
            ("Марка:", "make"),
            ("Модель:", "model"),
            ("Рік випуску:", "year"),
            ("Колір:", "color"),
            ("Номерний знак:", "plate_number"),
            ("VIN номер:", "vin_number"),
            ("Дата тех. огляду:", "technical_inspection_date"),
            ("Номер страхового полісу:", "insurance_policy_number"),
            ("Опис пошкоджень:", "damage_description"),
            ("Потребує евакуації:", "towing_required", ["Вибрати...", "Так", "Ні"]),
            ("Компанія евакуатор:", "towing_company"),
            ("ID ДТП:", "accident_id")
        ]

        for i, field in enumerate(fields):
            label = ttk.Label(self._vehicle_tab, text=field[0], style='header.TLabel')
            label.grid(row=i, column=0, sticky="e", padx=5, pady=2)

            if len(field) == 3:  # Drop-down for specific fields
                var = tk.StringVar(self._vehicle_tab)
                var.set(field[2][0])  # Set default value
                dropdown = ttk.OptionMenu(self._vehicle_tab, var, *field[2])
                dropdown.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
                setattr(self, f"_{field[1]}_var", var)
            else:  # Regular entry field for text input
                entry = ttk.Entry(self._vehicle_tab, width=30)
                entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
                setattr(self, f"_{field[1]}_entry", entry)

        # Add Vehicle Button with consistent styling
        add_vehicle_button = ttk.Button(self._vehicle_tab, text="Додати транспортний засіб", style='primary.TButton', command=self.add_vehicle)
        add_vehicle_button.grid(row=len(fields), column=0, columnspan=2, pady=10)


    def create_view_tab(self):
        # Define columns
        columns = (
            'ID', 'Дата', 'Час доби', 'Місце', 'Опис', 'Кількість учасників',
            'Умови погоди', 'Умови освітлення', 'Стан дороги',
            'Тип дороги', 'Покриття дороги', 'Обмеження швидкості', 'Тяжкість',
            'Опис пошкоджень майна', 'Оціночна сума збитків', 'Час прибуття служб',
            'Номер поліц. протоколу', 'Номер страхової справи', 'Статус розслідування'
        )
        
        # Treeview for displaying accident data
        self._accidents_tree = ttk.Treeview(self._view_tab, columns=columns, show='headings', height=15)

        # Configure columns and headings
        column_widths = {
            'ID': 50, 'Дата': 100, 'Час доби': 80, 'Місце': 150, 'Опис': 200,
            'Кількість учасників': 120, 'Умови погоди': 100, 'Умови освітлення': 120,
            'Стан дороги': 100, 'Тип дороги': 100, 'Покриття дороги': 120,
            'Обмеження швидкості': 130, 'Тяжкість': 80, 'Опис пошкоджень майна': 200,
            'Оціночна сума збитків': 130, 'Час прибуття служб': 120,
            'Номер поліц. протоколу': 130, 'Номер страхової справи': 130, 'Статус розслідування': 130
        }
        
        for col in columns:
            self._accidents_tree.heading(col, text=col)
            self._accidents_tree.column(col, width=column_widths[col])

        # Scrollbars for Treeview
        y_scrollbar = ttk.Scrollbar(self._view_tab, orient="vertical", command=self._accidents_tree.yview)
        x_scrollbar = ttk.Scrollbar(self._view_tab, orient="horizontal", command=self._accidents_tree.xview)
        self._accidents_tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)

        # Layout for Treeview and scrollbars
        self._accidents_tree.grid(row=0, column=0, sticky="nsew")
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        x_scrollbar.grid(row=1, column=0, sticky="ew")

        # Configure grid to make Treeview expandable
        self._view_tab.grid_rowconfigure(0, weight=1)
        self._view_tab.grid_columnconfigure(0, weight=1)

        # Frame for action buttons
        button_frame = ttk.Frame(self._view_tab, padding=5)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        # Action buttons
        self._participants_button = ttk.Button(button_frame, text="Показати учасників", style="primary.TButton", command=self.show_participants)
        self._participants_button.pack(side=tk.LEFT, padx=5)

        self._delete_accident_button = ttk.Button(button_frame, text="Видалити ДТП", style="danger.TButton", command=self.delete_accident)
        self._delete_accident_button.pack(side=tk.LEFT, padx=5)

        self._refresh_button = ttk.Button(button_frame, text="Оновити", style="success.TButton", command=self.load_accidents)
        self._refresh_button.pack(side=tk.LEFT, padx=5)

        self._export_button = ttk.Button(button_frame, text="Експортувати в CSV", style="info.TButton", command=self.export_data)
        self._export_button.pack(side=tk.LEFT, padx=5)

        # Filter Frame for date filtering
        filter_frame = ttk.Frame(self._view_tab, padding=5)
        filter_frame.grid(row=3, column=0, columnspan=2, pady=10)

        filter_label = ttk.Label(filter_frame, text="Фільтр за датою (ДД.ММ.РРРР):", style="header.TLabel")
        filter_label.pack(side=tk.LEFT, padx=5)
        
        self._filter_entry = ttk.Entry(filter_frame, width=20)
        self._filter_entry.pack(side=tk.LEFT, padx=5)

        self._filter_button = ttk.Button(filter_frame, text="Застосувати фільтр", style="primary.TButton", command=self.filter_accidents)
        self._filter_button.pack(side=tk.LEFT, padx=5)

        # Load initial accident data
        self.load_accidents()


    def add_accident(self):
        try:
            data = {
                'date': self._date_entry.get(),
                'time_of_day': self._time_of_day_var.get(),
                'location': self._location_entry.get(),
                'description': self._description_entry.get(),
                'participants_count': self._participants_count_entry.get(),
                'weather_condition': self._weather_condition_var.get(),
                'lighting_condition': self._lighting_condition_var.get(),
                'road_condition': self._road_condition_var.get(),
                'vehicle_type': self._vehicle_type_var.get(),
                'road_type': self._road_type_var.get(),
                'road_surface': self._road_surface_var.get(),
                'speed_limit': self._speed_limit_var.get(),
                'severity': self._severity_var.get(),
                'property_damage_description': self._property_damage_description_entry.get(),
                'estimated_damage': self._estimated_damage_entry.get(),
                'emergency_response_time': self._emergency_response_time_entry.get(),
                'police_report': self._police_report_entry.get(),
                'insurance_case_number': self._insurance_case_number_entry.get(),
                'investigation_status': self._investigation_status_var.get()
            }

            if self.validate_accident_input(data):
                database.insert_accident(self._conn, **data)
                self.load_accidents()
                self.clear_accident_fields()
                messagebox.showinfo("Успіх", "ДТП успішно додано до бази даних.")
            else:
                messagebox.showerror("Помилка", "Будь ласка, перевірте правильність введених даних.")
        except Exception as e:
            messagebox.showerror("Помилка", f"Виникла помилка при додаванні ДТП: {str(e)}")

    def validate_accident_input(self, data):
        # Перевірка обов'язкових полів
        required_fields = ['date', 'location', 'participants_count']
        for field in required_fields:
            if not data[field]:
                return False

        # Перевірка формату дати
        if not re.match(r'\d{2}\.\d{2}\.\d{4}', data['date']):
            return False

        # Перевірка кількості учасників
        if not data['participants_count'].isdigit() or int(data['participants_count']) < 1:
            return False

        # Перевірка часу доби
        if data['time_of_day'] not in ['День', 'Ніч', 'Сутінки']:
            return False

        # Перевірка тяжкості
        if data['severity'] not in ['Легка', 'Середня', 'Важка']:
            return False

        return True

    def add_participant(self):
        try:
            # Зібрати дані з форми
            data = {
                'name': self._name_entry.get(),
                'role': self._role_var.get(),
                'injuries': self._injuries_entry.get(),
                'injury_severity': self._injury_severity_var.get(),
                'hospitalized': self._hospitalized_var.get(),
                'age': self._age_entry.get(),
                'gender': self._gender_var.get(),
                'driver_license_number': self._driver_license_number_entry.get(),
                'license_status': self._license_status_var.get(),
                'license_category': self._license_category_var.get(),
                'insurance_policy_number': self._insurance_policy_number_entry.get(),
                'alcohol_test_result': self._alcohol_test_result_var.get(),
                'drug_test_result': self._drug_test_result_var.get(),
                'statement': self._statement_entry.get(),
                'accident_id': self._accident_id_entry.get()
            }

            # Перед валідацією перевірте наявність ID ДТП
            if not self.check_accident_exists(data['accident_id']):
                messagebox.showerror("Помилка", "Вказаного ID ДТП не існує.")
                return

            # Перевірка вхідних даних
            if self.validate_participant_input(data):
                database.insert_participant(self._conn, **data)
                self.clear_participant_fields()
                messagebox.showinfo("Успіх", "Учасника успішно додано.")
            else:
                messagebox.showerror("Помилка", "Будь ласка, перевірте правильність введених даних.")
        except ValueError as e:
            messagebox.showerror("Помилка", f"Помилка у введених даних: {str(e)}")
        except Exception as e:
            messagebox.showerror("Помилка", f"Виникла помилка при додаванні учасника: {str(e)}")

    def check_accident_exists(self, accident_id):
        # Додайте метод перевірки наявності ID ДТП в базі
        try:
            accident = database.get_accident_by_id(self._conn, accident_id)
            return accident is not None
        except Exception:
            return False

    def validate_participant_input(self, data):
        required_fields = ['name', 'role', 'age', 'accident_id']

        # Перевірка обов'язкових полів
        for field in required_fields:
            if not data[field]:
                print(f"Поле '{field}' порожнє")
                return False

        # Перевірка віку
        try:
            age = int(data['age'])
            if age < 0 or age > 150:
                print("Вік має бути в діапазоні від 0 до 150 років.")
                return False
        except ValueError:
            print("Вік повинен бути числом.")
            return False

        # Перевірка ID ДТП
        if not data['accident_id'].isdigit():
            print("ID ДТП повинен бути числовим.")
            return False

        # Перевірка ролі
        valid_roles = ['Водій', 'Пасажир', 'Пішохід']
        if data['role'] not in valid_roles:
            print(f"Невірна роль. Доступні значення: {', '.join(valid_roles)}")
            return False

        # Перевірка статі
        valid_genders = ['Чоловіча', 'Жіноча']
        if data['gender'] and data['gender'] not in valid_genders:
            print(f"Невірна стать. Доступні значення: {', '.join(valid_genders)}")
            return False

        # Перевірка госпіталізації
        valid_hospitalized = ['Так', 'Ні']
        if data['hospitalized'] and data['hospitalized'] not in valid_hospitalized:
            print(f"Невірне значення для госпіталізації. Доступні значення: {', '.join(valid_hospitalized)}")
            return False

        # Перевірка страхового полісу (якщо вказаний)
        if data['insurance_policy_number'] and not data['insurance_policy_number'].isdigit():
            print("Номер страхового полісу повинен бути числовим.")
            return False

        return True

    def add_vehicle(self):
        try:
            data = {
                'vehicle_type': self._vehicle_type_var.get(),
                'make': self._make_entry.get(),
                'model': self._model_entry.get(),
                'year': self._year_entry.get(),
                'color': self._color_entry.get(),
                'plate_number': self._plate_number_entry.get(),
                'vin_number': self._vin_number_entry.get(),
                'technical_inspection_date': self._technical_inspection_date_entry.get(),
                'insurance_policy_number': self._insurance_policy_number_entry.get(),
                'damage_description': self._damage_description_entry.get(),
                'towing_required': self._towing_required_var.get(),
                'towing_company': self._towing_company_entry.get(),
                'accident_id': self._accident_id_entry.get()
            }

            if self.validate_vehicle_input(data):
                database.insert_vehicle(self._conn, **data)
                self.clear_vehicle_fields()
                messagebox.showinfo("Успіх", "Транспортний засіб успішно додано.")
            else:
                messagebox.showerror("Помилка", "Будь ласка, перевірте правильність введених даних.")
        except Exception as e:
            messagebox.showerror("Помилка", f"Виникла помилка при додаванні транспортного засобу: {str(e)}")

    def validate_vehicle_input(self, data):
        # Перевірка обов'язкових полів
        required_fields = ['vehicle_type', 'make', 'model', 'year', 'accident_id']
        for field in required_fields:
            if not data[field]:
                print(f"Поле {field} порожнє")  
                return False

        # Перевірка року
        try:
            year = int(data['year'])
            current_year = datetime.now().year
            if year < 1900 or year > current_year:
                return False
        except ValueError:
            return False

        # Перевірка ID ДТП
        if not data['accident_id'].isdigit():
            return False

        return True

    def clear_accident_fields(self):
        for field in dir(self):
            if field.endswith('_entry'):
                getattr(self, field).delete(0, tk.END)
            elif field.endswith('_var'):
                getattr(self, field).set('')

    def clear_participant_fields(self):
        for field in dir(self):
            if field.endswith('_entry'):
                getattr(self, field).delete(0, tk.END)
            elif field.endswith('_var'):
                getattr(self, field).set('')

    def clear_vehicle_fields(self):
        for field in dir(self):
            if field.endswith('_entry'):
                getattr(self, field).delete(0, tk.END)
            elif field.endswith('_var'):
                getattr(self, field).set('')

    def load_accidents(self):
            for row in self._accidents_tree.get_children():
                self._accidents_tree.delete(row)

            accidents = database.get_accidents(self._conn)
            for accident in accidents:
                self._accidents_tree.insert('', tk.END, values=accident)

    def on_accident_select(self, event):
        selected_item = self._accidents_tree.selection()
        if selected_item:
            accident = self._accidents_tree.item(selected_item, 'values')
            self._edit_date_entry.delete(0, tk.END)
            self._edit_date_entry.insert(0, accident[1])
            self._edit_location_entry.delete(0, tk.END)
            self._edit_location_entry.insert(0, accident[2])
            self._edit_description_entry.delete(0, tk.END)
            self._edit_description_entry.insert(0, accident[3])
            self._edit_participants_count_entry.delete(0, tk.END)
            self._edit_participants_count_entry.insert(0, accident[4])
            self._edit_weather_condition_entry.delete(0, tk.END)
            self._edit_weather_condition_entry.insert(0, accident[5])
            self._edit_vehicle_type_entry.delete(0, tk.END)
            self._edit_vehicle_type_entry.insert(0, accident[6])

    def clear_edit_fields(self):
        self._edit_date_entry.delete(0, tk.END)
        self._edit_location_entry.delete(0, tk.END)
        self._edit_description_entry.delete(0, tk.END)
        self._edit_participants_count_entry.delete(0, tk.END)
        self._edit_weather_condition_entry.delete(0, tk.END)
        self._edit_vehicle_type_entry.delete(0, tk.END)

    def delete_accident(self):
        selected_item = self._accidents_tree.selection()
        if selected_item:
            accident_id = self._accidents_tree.item(selected_item, 'values')[0]
            database.delete_accident(self._conn, accident_id)
            self.load_accidents()

    def show_participants(self):
        selected_item = self._accidents_tree.selection()
        if selected_item:
            accident_id = self._accidents_tree.item(selected_item, 'values')[0]
            participants = database.get_participants_by_accident_id(self._conn, accident_id)

            participants_info = ""
            for participant in participants:
                participants_info += f"Ім'я: {participant[1]}, Роль: {participant[2]}, Травми: {participant[3]}\n"

            if participants_info:
                messagebox.showinfo("Учасники ДТП", participants_info)
            else:
                messagebox.showinfo("Учасники ДТП", "Учасників не знайдено.")

    def filter_accidents(self):
        date_filter = self._filter_entry.get()
        if re.match(r'\d{2}\.\d{2}\.\d{4}', date_filter):
            filtered_accidents = database.get_accidents_by_date(self._conn, date_filter)
            for row in self._accidents_tree.get_children():
                self._accidents_tree.delete(row)

            for accident in filtered_accidents:
                self._accidents_tree.insert('', tk.END, values=accident)
        else:
            messagebox.showerror("Помилка", "Невірний формат дати.")

    def export_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, 'w', newline='', encoding='utf-8', errors='replace') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['ID', 'Дата', 'Місце', 'Опис', 'Кількість учасників', 'Умови погоди', 'Тип ТЗ'])
                accidents = database.get_accidents(self._conn)
                writer.writerows(accidents)
                
if __name__ == "__main__":
    root = tk.Tk()
    app = AccidentManagementApp(root)
    root.mainloop()
