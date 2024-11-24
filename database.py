import sqlite3


def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    return conn

def create_tables(conn):
    cursor = conn.cursor()
    
    # Create accidents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            time_of_day TEXT,
            location TEXT NOT NULL,
            description TEXT,
            participants_count INTEGER NOT NULL,
            weather_condition TEXT,
            lighting_condition TEXT,
            road_condition TEXT,
            vehicle_type TEXT,
            road_type TEXT,
            road_surface TEXT,
            speed_limit TEXT,
            severity TEXT,
            property_damage_description TEXT,
            estimated_damage TEXT,
            emergency_response_time TEXT,
            police_report TEXT,
            insurance_case_number TEXT,
            investigation_status TEXT,
            CONSTRAINT valid_severity CHECK (severity IN ('Легка', 'Середня', 'Важка')),
            CONSTRAINT valid_time CHECK (time_of_day IN ('День', 'Ніч', 'Сутінки'))
        )
    ''')
    
    # Create participants table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('Водій', 'Пасажир', 'Пішохід')),
            injuries TEXT,
            injury_severity TEXT,
            hospitalized TEXT CHECK (hospitalized IN ('Так', 'Ні')),
            age INTEGER CHECK (age >= 0 AND age <= 150),
            gender TEXT CHECK (gender IN ('Чоловіча', 'Жіноча')),
            driver_license_number TEXT,
            license_status TEXT,
            license_category TEXT,
            insurance_policy_number INTEGER,
            alcohol_test_result TEXT,
            drug_test_result TEXT,
            statement TEXT,
            accident_id INTEGER NOT NULL,
            FOREIGN KEY (accident_id) REFERENCES accidents (id) ON DELETE CASCADE
        )
    ''')

    
    # Create vehicles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_type TEXT NOT NULL,
            make TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER NOT NULL,
            color TEXT,
            plate_number TEXT,
            vin_number TEXT,
            technical_inspection_date DATE,
            insurance_policy_number TEXT,
            damage_description TEXT,
            towing_required BOOLEAN,
            towing_company TEXT,
            accident_id INTEGER,
            FOREIGN KEY (accident_id) REFERENCES accidents (id) ON DELETE SET NULL
        )
    ''')

    conn.commit()

def insert_accident(conn, date, time_of_day, location, description, participants_count,
                   weather_condition, lighting_condition, road_condition, vehicle_type,
                   road_type, road_surface, speed_limit, severity, property_damage_description,
                   estimated_damage, emergency_response_time, police_report,
                   insurance_case_number, investigation_status):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO accidents (
                date, time_of_day, location, description, participants_count,
                weather_condition, lighting_condition, road_condition, vehicle_type,
                road_type, road_surface, speed_limit, severity,
                property_damage_description, estimated_damage,
                emergency_response_time, police_report,
                insurance_case_number, investigation_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date, time_of_day, location, description, participants_count,
              weather_condition, lighting_condition, road_condition, vehicle_type,
              road_type, road_surface, speed_limit, severity,
              property_damage_description, estimated_damage,
              emergency_response_time, police_report,
              insurance_case_number, investigation_status))
        accident_id = cursor.lastrowid
        conn.commit()
        return accident_id
    except Exception as e:
        conn.rollback()
        raise Exception(f"Помилка при додаванні ДТП: {str(e)}")

def insert_participant(conn, name, role, injuries, injury_severity, hospitalized, age, gender,
                       driver_license_number, license_status, license_category, insurance_policy_number,
                       alcohol_test_result, drug_test_result, statement, accident_id):
    try:
        if not accident_id:
            raise ValueError("Поле 'accident_id' є обов'язковим.")
        cursor = conn.cursor()
        query = """
        INSERT INTO participants (name, role, injuries, injury_severity, hospitalized, age, gender,
                                  driver_license_number, license_status, license_category,
                                  insurance_policy_number, alcohol_test_result, drug_test_result,
                                  statement, accident_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (name, role, injuries, injury_severity, hospitalized, age, gender,
                               driver_license_number, license_status, license_category,
                               insurance_policy_number, alcohol_test_result, drug_test_result,
                               statement, accident_id))
        conn.commit()
    except Exception as e:
        print(f"Помилка при додаванні учасника: {e}")
        raise

def insert_vehicle(conn, vehicle_type, make, model, year, color,
                  plate_number, vin_number, technical_inspection_date,
                  insurance_policy_number, damage_description,
                  towing_required, towing_company, accident_id):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vehicles (
                vehicle_type, make, model, year, color,
                plate_number, vin_number, technical_inspection_date,
                insurance_policy_number, damage_description,
                towing_required, towing_company, accident_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (vehicle_type, make, model, year, color,
              plate_number, vin_number, technical_inspection_date,
              insurance_policy_number, damage_description,
              towing_required, towing_company, accident_id))
        vehicle_id = cursor.lastrowid
        conn.commit()
        return vehicle_id
    except Exception as e:
        conn.rollback()
        raise Exception(f"Помилка при додаванні транспортного засобу: {str(e)}")

def get_accidents(conn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM accidents 
        ORDER BY date DESC, id DESC
    ''')
    return cursor.fetchall()

def get_accidents_by_date(conn, date):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM accidents 
        WHERE date = ? 
        ORDER BY id DESC
    ''', (date,))
    return cursor.fetchall()

def get_participants_by_accident_id(conn, accident_id):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM participants 
        WHERE accident_id = ? 
        ORDER BY id ASC
    ''', (accident_id,))
    return cursor.fetchall()

def get_vehicles_by_accident_id(conn, accident_id):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM vehicles 
        WHERE accident_id = ? 
        ORDER BY id ASC
    ''', (accident_id,))
    return cursor.fetchall()

def update_accident(conn, accident_id, date, time_of_day, location, description,
                   participants_count, weather_condition, lighting_condition,
                   road_condition, vehicle_type, road_type, road_surface,
                   speed_limit, severity, property_damage_description,
                   estimated_damage, emergency_response_time,
                   police_report, insurance_case_number,
                   investigation_status):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE accidents
            SET date = ?, time_of_day = ?, location = ?, description = ?,
                participants_count = ?, weather_condition = ?, lighting_condition = ?,
                road_condition = ?, vehicle_type = ?, road_type = ?, road_surface = ?,
                speed_limit = ?, severity = ?, property_damage_description = ?,
                estimated_damage = ?, emergency_response_time = ?,
                police_report = ?, insurance_case_number = ?,
                investigation_status = ?
            WHERE id = ?
        ''', (date, time_of_day, location, description,
              participants_count, weather_condition, lighting_condition,
              road_condition, vehicle_type, road_type, road_surface,
              speed_limit, severity, property_damage_description,
              estimated_damage, emergency_response_time,
              police_report, insurance_case_number,
              investigation_status, accident_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise Exception(f"Помилка при оновленні ДТП: {str(e)}")

def delete_accident(conn, accident_id):
    try:
        cursor = conn.cursor()
        # Видаляємо пов'язані записи
        cursor.execute('DELETE FROM participants WHERE accident_id = ?', (accident_id,))
        cursor.execute('DELETE FROM vehicles WHERE accident_id = ?', (accident_id,))
        # Видаляємо саме ДТП
        cursor.execute('DELETE FROM accidents WHERE id = ?', (accident_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise Exception(f"Помилка при видаленні ДТП: {str(e)}")
    
