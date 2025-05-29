import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
from datetime import datetime, date
from tkcalendar import DateEntry
import re

class PrisonerManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Prisoner Management System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Database connection
        self.connection = None
        self.connect_to_database()
        
        # Create main interface
        self.create_main_interface()
        
    def connect_to_database(self):
        """Connect to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                database='pms',
                user='root',  # Change as needed
                password='Ali@1234'   # Change as needed
            )
            if self.connection.is_connected():
                print("Successfully connected to MySQL database")
        except Exception as e:
            messagebox.showerror("Database Error", f"Error connecting to database: {str(e)}")
            
    def create_main_interface(self):
        """Create the main interface with notebook tabs"""
        # Main title
        title_label = tk.Label(self.root, text="Prisoner Management System", 
                              font=('Arial', 20, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs for each table
        self.create_prisoner_tab()
        self.create_cell_tab()
        self.create_visitor_tab()
        self.create_staff_tab()
        self.create_incident_tab()
        self.create_medical_tab()
        
    def create_prisoner_tab(self):
        """Create Prisoner management tab"""
        prisoner_frame = ttk.Frame(self.notebook)
        self.notebook.add(prisoner_frame, text="Prisoners")
        
        # Create form frame
        form_frame = ttk.LabelFrame(prisoner_frame, text="Prisoner Information", padding=10)
        form_frame.pack(fill='x', padx=10, pady=5)
        
        # Form fields
        fields = [
            ("First Name:", "first_name"),
            ("Last Name:", "last_name"),
            ("Gender:", "gender"),
            ("Date of Birth:", "dob"),
            ("Date of Incarceration:", "incarceration_date"),
            ("Date of Release:", "release_date"),
            ("Crime Committed:", "crime"),
            ("Status:", "status"),
            ("Cell ID:", "cell_id")
        ]
        
        self.prisoner_entries = {}
        
        for i, (label, field) in enumerate(fields):
            row = i // 3
            col = (i % 3) * 2
            
            ttk.Label(form_frame, text=label).grid(row=row, column=col, sticky='w', padx=5, pady=5)
            
            if field == "gender":
                entry = ttk.Combobox(form_frame, values=["Male", "Female", "Other"], state="readonly")
            elif field == "status":
                entry = ttk.Combobox(form_frame, values=["Incarcerated", "Released", "Paroled"], state="readonly")
            elif "date" in field:
                entry = DateEntry(form_frame, width=12, background='darkblue',
                                foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
            elif field == "crime":
                entry = tk.Text(form_frame, height=3, width=20)
            else:
                entry = ttk.Entry(form_frame, width=20)
                
            entry.grid(row=row, column=col+1, padx=5, pady=5, sticky='w')
            self.prisoner_entries[field] = entry
        
        # Buttons frame
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=6, pady=10)
        
        ttk.Button(button_frame, text="Add Prisoner", 
                  command=self.add_prisoner).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Update Prisoner", 
                  command=self.update_prisoner).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Prisoner", 
                  command=self.delete_prisoner).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Form", 
                  command=self.clear_prisoner_form).pack(side='left', padx=5)
        
        # Treeview for displaying prisoners
        tree_frame = ttk.LabelFrame(prisoner_frame, text="Prisoners List", padding=10)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ("ID", "First Name", "Last Name", "Gender", "DOB", "Incarceration", 
                  "Release", "Crime", "Status", "Cell ID")
        
        self.prisoner_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        for col in columns:
            self.prisoner_tree.heading(col, text=col)
            self.prisoner_tree.column(col, width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.prisoner_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.prisoner_tree.xview)
        self.prisoner_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.prisoner_tree.pack(fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Bind double-click to load data
        self.prisoner_tree.bind('<Double-1>', self.load_prisoner_data)
        
        # Load initial data
        self.refresh_prisoner_list()
    
    def create_cell_tab(self):
        """Create Cell management tab"""
        cell_frame = ttk.Frame(self.notebook)
        self.notebook.add(cell_frame, text="Cells")
        
        # Form frame
        form_frame = ttk.LabelFrame(cell_frame, text="Cell Information", padding=10)
        form_frame.pack(fill='x', padx=10, pady=5)
        
        self.cell_entries = {}
        fields = [("Cell Number:", "cell_number"), ("Capacity:", "capacity"), 
                 ("Current Occupancy:", "current_occupancy"), ("Block Number:", "block_number")]
        
        for i, (label, field) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=0, column=i*2, sticky='w', padx=5, pady=5)
            entry = ttk.Entry(form_frame, width=15)
            entry.grid(row=0, column=i*2+1, padx=5, pady=5)
            self.cell_entries[field] = entry
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=1, column=0, columnspan=8, pady=10)
        
        ttk.Button(button_frame, text="Add Cell", command=self.add_cell).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Update Cell", command=self.update_cell).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Cell", command=self.delete_cell).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_cell_form).pack(side='left', padx=5)
        
        # Treeview
        tree_frame = ttk.LabelFrame(cell_frame, text="Cells List", padding=10)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ("ID", "Cell Number", "Capacity", "Current Occupancy", "Block Number")
        self.cell_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        for col in columns:
            self.cell_tree.heading(col, text=col)
            self.cell_tree.column(col, width=120)
        
        scrollbar_cell = ttk.Scrollbar(tree_frame, orient='vertical', command=self.cell_tree.yview)
        self.cell_tree.configure(yscrollcommand=scrollbar_cell.set)
        
        self.cell_tree.pack(fill='both', expand=True)
        scrollbar_cell.pack(side='right', fill='y')
        
        self.cell_tree.bind('<Double-1>', self.load_cell_data)
        self.refresh_cell_list()
    
    def create_visitor_tab(self):
        """Create Visitor management tab"""
        visitor_frame = ttk.Frame(self.notebook)
        self.notebook.add(visitor_frame, text="Visitors")
        
        # Form frame
        form_frame = ttk.LabelFrame(visitor_frame, text="Visitor Information", padding=10)
        form_frame.pack(fill='x', padx=10, pady=5)
        
        self.visitor_entries = {}
        
        # First row
        ttk.Label(form_frame, text="Prisoner ID:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.visitor_entries["prisoner_id"] = ttk.Entry(form_frame, width=15)
        self.visitor_entries["prisoner_id"].grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="First Name:").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.visitor_entries["first_name"] = ttk.Entry(form_frame, width=15)
        self.visitor_entries["first_name"].grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Last Name:").grid(row=0, column=4, sticky='w', padx=5, pady=5)
        self.visitor_entries["last_name"] = ttk.Entry(form_frame, width=15)
        self.visitor_entries["last_name"].grid(row=0, column=5, padx=5, pady=5)
        
        # Second row
        ttk.Label(form_frame, text="Relationship:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.visitor_entries["relationship"] = ttk.Entry(form_frame, width=15)
        self.visitor_entries["relationship"].grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Visit Date:").grid(row=1, column=2, sticky='w', padx=5, pady=5)
        self.visitor_entries["visit_date"] = DateEntry(form_frame, width=12, background='darkblue',
                                                      foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.visitor_entries["visit_date"].grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Visit Time:").grid(row=1, column=4, sticky='w', padx=5, pady=5)
        self.visitor_entries["visit_time"] = ttk.Entry(form_frame, width=15)
        self.visitor_entries["visit_time"].grid(row=1, column=5, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=2, column=0, columnspan=6, pady=10)
        
        ttk.Button(button_frame, text="Add Visitor", command=self.add_visitor).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Update Visitor", command=self.update_visitor).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Visitor", command=self.delete_visitor).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_visitor_form).pack(side='left', padx=5)
        
        # Treeview
        tree_frame = ttk.LabelFrame(visitor_frame, text="Visitors List", padding=10)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ("ID", "Prisoner ID", "First Name", "Last Name", "Relationship", "Visit Date", "Visit Time")
        self.visitor_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        for col in columns:
            self.visitor_tree.heading(col, text=col)
            self.visitor_tree.column(col, width=100)
        
        scrollbar_visitor = ttk.Scrollbar(tree_frame, orient='vertical', command=self.visitor_tree.yview)
        self.visitor_tree.configure(yscrollcommand=scrollbar_visitor.set)
        
        self.visitor_tree.pack(fill='both', expand=True)
        scrollbar_visitor.pack(side='right', fill='y')
        
        self.visitor_tree.bind('<Double-1>', self.load_visitor_data)
        self.refresh_visitor_list()
    
    def create_staff_tab(self):
        """Create Staff management tab"""
        staff_frame = ttk.Frame(self.notebook)
        self.notebook.add(staff_frame, text="Staff")
        
        # Form frame
        form_frame = ttk.LabelFrame(staff_frame, text="Staff Information", padding=10)
        form_frame.pack(fill='x', padx=10, pady=5)
        
        self.staff_entries = {}
        
        # First row
        ttk.Label(form_frame, text="First Name:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.staff_entries["first_name"] = ttk.Entry(form_frame, width=15)
        self.staff_entries["first_name"].grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Last Name:").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.staff_entries["last_name"] = ttk.Entry(form_frame, width=15)
        self.staff_entries["last_name"].grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Gender:").grid(row=0, column=4, sticky='w', padx=5, pady=5)
        self.staff_entries["gender"] = ttk.Combobox(form_frame, values=["Male", "Female", "Other"], 
                                                   state="readonly", width=12)
        self.staff_entries["gender"].grid(row=0, column=5, padx=5, pady=5)
        
        # Second row
        ttk.Label(form_frame, text="Date of Birth:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.staff_entries["dob"] = DateEntry(form_frame, width=12, background='darkblue',
                                             foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.staff_entries["dob"].grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Role:").grid(row=1, column=2, sticky='w', padx=5, pady=5)
        self.staff_entries["role"] = ttk.Entry(form_frame, width=15)
        self.staff_entries["role"].grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Salary:").grid(row=1, column=4, sticky='w', padx=5, pady=5)
        self.staff_entries["salary"] = ttk.Entry(form_frame, width=15)
        self.staff_entries["salary"].grid(row=1, column=5, padx=5, pady=5)
        
        # Third row
        ttk.Label(form_frame, text="Hire Date:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.staff_entries["hire_date"] = DateEntry(form_frame, width=12, background='darkblue',
                                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.staff_entries["hire_date"].grid(row=2, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=6, pady=10)
        
        ttk.Button(button_frame, text="Add Staff", command=self.add_staff).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Update Staff", command=self.update_staff).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Staff", command=self.delete_staff).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_staff_form).pack(side='left', padx=5)
        
        # Treeview
        tree_frame = ttk.LabelFrame(staff_frame, text="Staff List", padding=10)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ("ID", "First Name", "Last Name", "Gender", "DOB", "Role", "Salary", "Hire Date")
        self.staff_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        for col in columns:
            self.staff_tree.heading(col, text=col)
            self.staff_tree.column(col, width=100)
        
        scrollbar_staff = ttk.Scrollbar(tree_frame, orient='vertical', command=self.staff_tree.yview)
        self.staff_tree.configure(yscrollcommand=scrollbar_staff.set)
        
        self.staff_tree.pack(fill='both', expand=True)
        scrollbar_staff.pack(side='right', fill='y')
        
        self.staff_tree.bind('<Double-1>', self.load_staff_data)
        self.refresh_staff_list()
    
    def create_incident_tab(self):
        """Create Incident Report management tab"""
        incident_frame = ttk.Frame(self.notebook)
        self.notebook.add(incident_frame, text="Incident Reports")
        
        # Form frame
        form_frame = ttk.LabelFrame(incident_frame, text="Incident Information", padding=10)
        form_frame.pack(fill='x', padx=10, pady=5)
        
        self.incident_entries = {}
        
        # First row
        ttk.Label(form_frame, text="Prisoner ID:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.incident_entries["prisoner_id"] = ttk.Entry(form_frame, width=15)
        self.incident_entries["prisoner_id"].grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Staff ID:").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.incident_entries["staff_id"] = ttk.Entry(form_frame, width=15)
        self.incident_entries["staff_id"].grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Incident Date:").grid(row=0, column=4, sticky='w', padx=5, pady=5)
        self.incident_entries["incident_date"] = DateEntry(form_frame, width=12, background='darkblue',
                                                          foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.incident_entries["incident_date"].grid(row=0, column=5, padx=5, pady=5)
        
        # Second row
        ttk.Label(form_frame, text="Incident Description:").grid(row=1, column=0, sticky='nw', padx=5, pady=5)
        self.incident_entries["incident_description"] = tk.Text(form_frame, height=4, width=50)
        self.incident_entries["incident_description"].grid(row=1, column=1, columnspan=4, padx=5, pady=5, sticky='ew')
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=2, column=0, columnspan=6, pady=10)
        
        ttk.Button(button_frame, text="Add Incident", command=self.add_incident).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Update Incident", command=self.update_incident).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Incident", command=self.delete_incident).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_incident_form).pack(side='left', padx=5)
        
        # Treeview
        tree_frame = ttk.LabelFrame(incident_frame, text="Incident Reports List", padding=10)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ("ID", "Prisoner ID", "Staff ID", "Description", "Date")
        self.incident_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        for col in columns:
            self.incident_tree.heading(col, text=col)
            if col == "Description":
                self.incident_tree.column(col, width=300)
            else:
                self.incident_tree.column(col, width=100)
        
        scrollbar_incident = ttk.Scrollbar(tree_frame, orient='vertical', command=self.incident_tree.yview)
        self.incident_tree.configure(yscrollcommand=scrollbar_incident.set)
        
        self.incident_tree.pack(fill='both', expand=True)
        scrollbar_incident.pack(side='right', fill='y')
        
        self.incident_tree.bind('<Double-1>', self.load_incident_data)
        self.refresh_incident_list()
    
    def create_medical_tab(self):
        """Create Medical Record management tab"""
        medical_frame = ttk.Frame(self.notebook)
        self.notebook.add(medical_frame, text="Medical Records")
        
        # Form frame
        form_frame = ttk.LabelFrame(medical_frame, text="Medical Record Information", padding=10)
        form_frame.pack(fill='x', padx=10, pady=5)
        
        self.medical_entries = {}
        
        # First row
        ttk.Label(form_frame, text="Prisoner ID:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.medical_entries["prisoner_id"] = ttk.Entry(form_frame, width=15)
        self.medical_entries["prisoner_id"].grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Doctor ID:").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.medical_entries["doctor_id"] = ttk.Entry(form_frame, width=15)
        self.medical_entries["doctor_id"].grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Examination Date:").grid(row=0, column=4, sticky='w', padx=5, pady=5)
        self.medical_entries["examination_date"] = DateEntry(form_frame, width=12, background='darkblue',
                                                            foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.medical_entries["examination_date"].grid(row=0, column=5, padx=5, pady=5)
        
        # Second row
        ttk.Label(form_frame, text="Diagnosis:").grid(row=1, column=0, sticky='nw', padx=5, pady=5)
        self.medical_entries["diagnosis"] = tk.Text(form_frame, height=3, width=25)
        self.medical_entries["diagnosis"].grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky='ew')
        
        ttk.Label(form_frame, text="Treatment:").grid(row=1, column=3, sticky='nw', padx=5, pady=5)
        self.medical_entries["treatment"] = tk.Text(form_frame, height=3, width=25)
        self.medical_entries["treatment"].grid(row=1, column=4, columnspan=2, padx=5, pady=5, sticky='ew')
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=2, column=0, columnspan=6, pady=10)
        
        ttk.Button(button_frame, text="Add Medical Record", command=self.add_medical).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Update Medical Record", command=self.update_medical).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Medical Record", command=self.delete_medical).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_medical_form).pack(side='left', padx=5)
        
        # Treeview
        tree_frame = ttk.LabelFrame(medical_frame, text="Medical Records List", padding=10)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ("ID", "Prisoner ID", "Diagnosis", "Treatment", "Exam Date", "Doctor ID")
        self.medical_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        for col in columns:
            self.medical_tree.heading(col, text=col)
            if col in ["Diagnosis", "Treatment"]:
                self.medical_tree.column(col, width=200)
            else:
                self.medical_tree.column(col, width=100)
        
        scrollbar_medical = ttk.Scrollbar(tree_frame, orient='vertical', command=self.medical_tree.yview)
        self.medical_tree.configure(yscrollcommand=scrollbar_medical.set)
        
        self.medical_tree.pack(fill='both', expand=True)
        scrollbar_medical.pack(side='right', fill='y')
        
        self.medical_tree.bind('<Double-1>', self.load_medical_data)
        self.refresh_medical_list()
    
    # Prisoner CRUD Operations
    def add_prisoner(self):
        try:
            cursor = self.connection.cursor()
            
            # Get values from form
            values = []
            for field in ["first_name", "last_name", "gender", "dob", "incarceration_date", 
                         "release_date", "crime", "status", "cell_id"]:
                if field == "crime":
                    value = self.prisoner_entries[field].get("1.0", tk.END).strip()
                elif "date" in field:
                    value = self.prisoner_entries[field].get_date()
                else:
                    value = self.prisoner_entries[field].get()
                
                if field == "cell_id" and value == "":
                    value = None
                elif field == "release_date" and value == "":
                    value = None
                    
                values.append(value)
            
            query = """INSERT INTO Prisoner (first_name, last_name, gender, date_of_birth, 
                      date_of_incarceration, date_of_release, crime_committed, status, cell_id) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
            cursor.execute(query, values)
            self.connection.commit()
            
            messagebox.showinfo("Success", "Prisoner added successfully!")
            self.clear_prisoner_form()
            self.refresh_prisoner_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error adding prisoner: {str(e)}")
    
    def update_prisoner(self):
        selected_item = self.prisoner_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a prisoner to update")
            return
        
        try:
            cursor = self.connection.cursor()
            prisoner_id = self.prisoner_tree.item(selected_item)['values'][0]
            
            values = []
            for field in ["first_name", "last_name", "gender", "dob", "incarceration_date", 
                         "release_date", "crime", "status", "cell_id"]:
                if field == "crime":
                    value = self.prisoner_entries[field].get("1.0", tk.END).strip()
                elif "date" in field:
                    value = self.prisoner_entries[field].get_date()
                else:
                    value = self.prisoner_entries[field].get()
                
                if field == "cell_id" and value == "":
                    value = None
                elif field == "release_date" and value == "":
                    value = None
                    
                values.append(value)
            
            values.append(prisoner_id)
            query = """UPDATE Prisoner SET first_name=%s, last_name=%s, gender=%s, date_of_birth=%s, 
                      date_of_incarceration=%s, date_of_release=%s, crime_committed=%s, 
                      status=%s, cell_id=%s WHERE prisoner_id=%s"""
            
            cursor.execute(query, values)
            self.connection.commit()
            
            messagebox.showinfo("Success", "Prisoner updated successfully!")
            self.refresh_prisoner_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error updating prisoner: {str(e)}")
    
    def delete_prisoner(self):
        selected_item = self.prisoner_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a prisoner to delete")
            return
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this prisoner?"):
            return
        
        try:
            cursor = self.connection.cursor()
            prisoner_id = self.prisoner_tree.item(selected_item)['values'][0]
            
            query = "DELETE FROM Prisoner WHERE prisoner_id=%s"
            cursor.execute(query, (prisoner_id,))
            self.connection.commit()
            
            messagebox.showinfo("Success", "Prisoner deleted successfully!")
            self.clear_prisoner_form()
            self.refresh_prisoner_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting prisoner: {str(e)}")
    
    def load_prisoner_data(self, event):
        selected_item = self.prisoner_tree.selection()
        if not selected_item:
            return
        
        prisoner_data = self.prisoner_tree.item(selected_item)['values']
        
        # Clear form first
        self.clear_prisoner_form()
        
        # Set values in form
        self.prisoner_entries["first_name"].insert(0, prisoner_data[1])
        self.prisoner_entries["last_name"].insert(0, prisoner_data[2])
        self.prisoner_entries["gender"].set(prisoner_data[3])
        
        # Set date fields
        if prisoner_data[4]:
            self.prisoner_entries["dob"].set_date(datetime.strptime(prisoner_data[4], '%Y-%m-%d').date())
        if prisoner_data[5]:
            self.prisoner_entries["incarceration_date"].set_date(datetime.strptime(prisoner_data[5], '%Y-%m-%d').date())
        if prisoner_data[6]:
            self.prisoner_entries["release_date"].set_date(datetime.strptime(prisoner_data[6], '%Y-%m-%d').date())
        
        self.prisoner_entries["crime"].insert("1.0", prisoner_data[7])
        self.prisoner_entries["status"].set(prisoner_data[8])
        
        if prisoner_data[9]:
            self.prisoner_entries["cell_id"].insert(0, prisoner_data[9])
    
    def clear_prisoner_form(self):
        for field, entry in self.prisoner_entries.items():
            if field == "crime":
                entry.delete("1.0", tk.END)
            elif "date" in field:
                entry.set_date(None)
            elif field in ["gender", "status"]:
                entry.set('')
            else:
                entry.delete(0, tk.END)
    
    def refresh_prisoner_list(self):
        try:
            cursor = self.connection.cursor()
            query = """SELECT prisoner_id, first_name, last_name, gender, date_of_birth, 
                      date_of_incarceration, date_of_release, crime_committed, status, cell_id 
                      FROM Prisoner"""
            cursor.execute(query)
            
            # Clear existing data
            for row in self.prisoner_tree.get_children():
                self.prisoner_tree.delete(row)
            
            # Add new data
            for row in cursor.fetchall():
                formatted_row = list(row)
                # Format dates
                for i in range(4, 7):
                    if formatted_row[i]:
                        formatted_row[i] = formatted_row[i].strftime('%Y-%m-%d')
                self.prisoner_tree.insert('', 'end', values=formatted_row)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading prisoners: {str(e)}")

    # Cell CRUD Operations
    def add_cell(self):
        try:
            cursor = self.connection.cursor()
            
            values = []
            for field in ["cell_number", "capacity", "current_occupancy", "block_number"]:
                value = self.cell_entries[field].get()
                if field in ["capacity", "current_occupancy"] and value:
                    value = int(value)
                values.append(value)
            
            query = """INSERT INTO Cell (cell_number, capacity, current_occupancy, block_number) 
                      VALUES (%s, %s, %s, %s)"""
            
            cursor.execute(query, values)
            self.connection.commit()
            
            messagebox.showinfo("Success", "Cell added successfully!")
            self.clear_cell_form()
            self.refresh_cell_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error adding cell: {str(e)}")
    
    def update_cell(self):
        selected_item = self.cell_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a cell to update")
            return
        
        try:
            cursor = self.connection.cursor()
            cell_id = self.cell_tree.item(selected_item)['values'][0]
            
            values = []
            for field in ["cell_number", "capacity", "current_occupancy", "block_number"]:
                value = self.cell_entries[field].get()
                if field in ["capacity", "current_occupancy"] and value:
                    value = int(value)
                values.append(value)
            
            values.append(cell_id)
            
            query = """UPDATE Cell SET cell_number=%s, capacity=%s, 
                      current_occupancy=%s, block_number=%s WHERE cell_id=%s"""
            
            cursor.execute(query, values)
            self.connection.commit()
            
            messagebox.showinfo("Success", "Cell updated successfully!")
            self.refresh_cell_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error updating cell: {str(e)}")
    
    def delete_cell(self):
        selected_item = self.cell_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a cell to delete")
            return
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this cell?"):
            return
        
        try:
            cursor = self.connection.cursor()
            cell_id = self.cell_tree.item(selected_item)['values'][0]
            
            # Check if cell has prisoners
            cursor.execute("SELECT COUNT(*) FROM Prisoner WHERE cell_id=%s", (cell_id,))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Error", "Cannot delete cell with prisoners assigned!")
                return
            
            query = "DELETE FROM Cell WHERE cell_id=%s"
            cursor.execute(query, (cell_id,))
            self.connection.commit()
            
            messagebox.showinfo("Success", "Cell deleted successfully!")
            self.clear_cell_form()
            self.refresh_cell_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting cell: {str(e)}")
    
    def load_cell_data(self, event):
        selected_item = self.cell_tree.selection()
        if not selected_item:
            return
        
        cell_data = self.cell_tree.item(selected_item)['values']
        
        # Clear form first
        self.clear_cell_form()
        
        # Set values in form
        self.cell_entries["cell_number"].insert(0, cell_data[1])
        self.cell_entries["capacity"].insert(0, cell_data[2])
        self.cell_entries["current_occupancy"].insert(0, cell_data[3])
        self.cell_entries["block_number"].insert(0, cell_data[4])
    
    def clear_cell_form(self):
        for entry in self.cell_entries.values():
            entry.delete(0, tk.END)
    
    def refresh_cell_list(self):
        try:
            cursor = self.connection.cursor()
            query = "SELECT cell_id, cell_number, capacity, current_occupancy, block_number FROM Cell"
            cursor.execute(query)
            
            # Clear existing data
            for row in self.cell_tree.get_children():
                self.cell_tree.delete(row)
            
            # Add new data
            for row in cursor.fetchall():
                self.cell_tree.insert('', 'end', values=row)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading cells: {str(e)}")

    # Visitor CRUD Operations
    def add_visitor(self):
        try:
            cursor = self.connection.cursor()
            
            values = []
            for field in ["prisoner_id", "first_name", "last_name", "relationship", "visit_date", "visit_time"]:
                if field == "visit_date":
                    value = self.visitor_entries[field].get_date()
                else:
                    value = self.visitor_entries[field].get()
                
                if field == "prisoner_id" and value:
                    value = int(value)
                    
                values.append(value)
            
            query = """INSERT INTO Visitor (prisoner_id, first_name, last_name, 
                      relationship, visit_date, visit_time) 
                      VALUES (%s, %s, %s, %s, %s, %s)"""
            
            cursor.execute(query, values)
            self.connection.commit()
            
            messagebox.showinfo("Success", "Visitor added successfully!")
            self.clear_visitor_form()
            self.refresh_visitor_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error adding visitor: {str(e)}")
    
    def update_visitor(self):
        selected_item = self.visitor_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a visitor to update")
            return
        
        try:
            cursor = self.connection.cursor()
            visitor_id = self.visitor_tree.item(selected_item)['values'][0]
            
            values = []
            for field in ["prisoner_id", "first_name", "last_name", "relationship", "visit_date", "visit_time"]:
                if field == "visit_date":
                    value = self.visitor_entries[field].get_date()
                else:
                    value = self.visitor_entries[field].get()
                
                if field == "prisoner_id" and value:
                    value = int(value)
                    
                values.append(value)
            
            values.append(visitor_id)
            
            query = """UPDATE Visitor SET prisoner_id=%s, first_name=%s, last_name=%s, 
                      relationship=%s, visit_date=%s, visit_time=%s WHERE visitor_id=%s"""
            
            cursor.execute(query, values)
            self.connection.commit()
            
            messagebox.showinfo("Success", "Visitor updated successfully!")
            self.refresh_visitor_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error updating visitor: {str(e)}")
    
    def delete_visitor(self):
        selected_item = self.visitor_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a visitor to delete")
            return
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this visitor?"):
            return
        
        try:
            cursor = self.connection.cursor()
            visitor_id = self.visitor_tree.item(selected_item)['values'][0]
            
            query = "DELETE FROM Visitor WHERE visitor_id=%s"
            cursor.execute(query, (visitor_id,))
            self.connection.commit()
            
            messagebox.showinfo("Success", "Visitor deleted successfully!")
            self.clear_visitor_form()
            self.refresh_visitor_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting visitor: {str(e)}")
    
    def load_visitor_data(self, event):
        selected_item = self.visitor_tree.selection()
        if not selected_item:
            return
        
        visitor_data = self.visitor_tree.item(selected_item)['values']
        
        # Clear form first
        self.clear_visitor_form()
        
        # Set values in form
        self.visitor_entries["prisoner_id"].insert(0, visitor_data[1])
        self.visitor_entries["first_name"].insert(0, visitor_data[2])
        self.visitor_entries["last_name"].insert(0, visitor_data[3])
        self.visitor_entries["relationship"].insert(0, visitor_data[4])
        
        if visitor_data[5]:
            self.visitor_entries["visit_date"].set_date(datetime.strptime(visitor_data[5], '%Y-%m-%d').date())
        
        self.visitor_entries["visit_time"].insert(0, visitor_data[6])
    
    def clear_visitor_form(self):
        for field, entry in self.visitor_entries.items():
            if field == "visit_date":
                entry.set_date(None)
            else:
                entry.delete(0, tk.END)
    
    def refresh_visitor_list(self):
        try:
            cursor = self.connection.cursor()
            query = """SELECT visitor_id, prisoner_id, first_name, last_name, 
                      relationship, visit_date, visit_time FROM Visitor"""
            cursor.execute(query)
            
            # Clear existing data
            for row in self.visitor_tree.get_children():
                self.visitor_tree.delete(row)
            
            # Add new data
            for row in cursor.fetchall():
                formatted_row = list(row)
                # Format date
                if formatted_row[5]:
                    formatted_row[5] = formatted_row[5].strftime('%Y-%m-%d')
                self.visitor_tree.insert('', 'end', values=formatted_row)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading visitors: {str(e)}")

    # Staff CRUD Operations
    def add_staff(self):
        try:
            cursor = self.connection.cursor()
            
            values = []
            for field in ["first_name", "last_name", "gender", "dob", "role", "salary", "hire_date"]:
                if field in ["dob", "hire_date"]:
                    value = self.staff_entries[field].get_date()
                elif field == "salary":
                    value = float(self.staff_entries[field].get())
                else:
                    value = self.staff_entries[field].get()
                    
                values.append(value)
            
            query = """INSERT INTO Staff (first_name, last_name, gender, date_of_birth, 
                      role, salary, hire_date) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            
            cursor.execute(query, values)
            self.connection.commit()
            
            messagebox.showinfo("Success", "Staff member added successfully!")
            self.clear_staff_form()
            self.refresh_staff_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error adding staff: {str(e)}")
    
    def update_staff(self):
        selected_item = self.staff_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a staff member to update")
            return
        
        try:
            cursor = self.connection.cursor()
            staff_id = self.staff_tree.item(selected_item)['values'][0]
            
            values = []
            for field in ["first_name", "last_name", "gender", "dob", "role", "salary", "hire_date"]:
                if field in ["dob", "hire_date"]:
                    value = self.staff_entries[field].get_date()
                elif field == "salary":
                    value = float(self.staff_entries[field].get())
                else:
                    value = self.staff_entries[field].get()
                    
                values.append(value)
            
            values.append(staff_id)
            
            query = """UPDATE Staff SET first_name=%s, last_name=%s, gender=%s, date_of_birth=%s, 
                      role=%s, salary=%s, hire_date=%s WHERE staff_id=%s"""
            
            cursor.execute(query, values)
            self.connection.commit()
            
            messagebox.showinfo("Success", "Staff member updated successfully!")
            self.refresh_staff_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error updating staff: {str(e)}")
    
    def delete_staff(self):
        selected_item = self.staff_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a staff member to delete")
            return
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this staff member?"):
            return
        
        try:
            cursor = self.connection.cursor()
            staff_id = self.staff_tree.item(selected_item)['values'][0]
            
            # Check if staff is referenced in incidents
            cursor.execute("SELECT COUNT(*) FROM IncidentReport WHERE staff_id=%s", (staff_id,))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Error", "Cannot delete staff member referenced in incidents!")
                return
            
            # Check if staff is a doctor referenced in medical records
            cursor.execute("SELECT COUNT(*) FROM MedicalRecord WHERE doctor_id=%s", (staff_id,))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Error", "Cannot delete doctor referenced in medical records!")
                return
            
            query = "DELETE FROM Staff WHERE staff_id=%s"
            cursor.execute(query, (staff_id,))
            self.connection.commit()
            
            messagebox.showinfo("Success", "Staff member deleted successfully!")
            self.clear_staff_form()
            self.refresh_staff_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting staff: {str(e)}")
    
    def load_staff_data(self, event):
        selected_item = self.staff_tree.selection()
        if not selected_item:
            return
        
        staff_data = self.staff_tree.item(selected_item)['values']
        
        # Clear form first
        self.clear_staff_form()
        
        # Set values in form
        self.staff_entries["first_name"].insert(0, staff_data[1])
        self.staff_entries["last_name"].insert(0, staff_data[2])
        self.staff_entries["gender"].set(staff_data[3])
        
        if staff_data[4]:
            self.staff_entries["dob"].set_date(datetime.strptime(staff_data[4], '%Y-%m-%d').date())
        
        self.staff_entries["role"].insert(0, staff_data[5])
        self.staff_entries["salary"].insert(0, staff_data[6])
        
        if staff_data[7]:
            self.staff_entries["hire_date"].set_date(datetime.strptime(staff_data[7], '%Y-%m-%d').date())
    
    def clear_staff_form(self):
        for field, entry in self.staff_entries.items():
            if field in ["dob", "hire_date"]:
                entry.set_date(None)
            elif field == "gender":
                entry.set('')
            else:
                entry.delete(0, tk.END)
    
    def refresh_staff_list(self):
        try:
            cursor = self.connection.cursor()
            query = """SELECT staff_id, first_name, last_name, gender, date_of_birth, 
                      role, salary, hire_date FROM Staff"""
            cursor.execute(query)
            
            # Clear existing data
            for row in self.staff_tree.get_children():
                self.staff_tree.delete(row)
            
            # Add new data
            for row in cursor.fetchall():
                formatted_row = list(row)
                # Format dates
                for i in [4, 7]:  # date_of_birth and hire_date indices
                    if formatted_row[i]:
                        formatted_row[i] = formatted_row[i].strftime('%Y-%m-%d')
                self.staff_tree.insert('', 'end', values=formatted_row)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading staff: {str(e)}")

    # Incident CRUD Operations
    def add_incident(self):
        try:
            cursor = self.connection.cursor()
            
            values = []
            for field in ["prisoner_id", "staff_id", "incident_date", "incident_description"]:
                if field == "incident_date":
                    value = self.incident_entries[field].get_date()
                elif field == "incident_description":
                    value = self.incident_entries[field].get("1.0", tk.END).strip()
                else:
                    value = self.incident_entries[field].get()
                
                if field in ["prisoner_id", "staff_id"] and value:
                    value = int(value)
                    
                values.append(value)
            
            query = """INSERT INTO IncidentReport (prisoner_id, staff_id, incident_date, 
                      incident_description) VALUES (%s, %s, %s, %s)"""
            
            cursor.execute(query, values)
            self.connection.commit()
            
            messagebox.showinfo("Success", "Incident report added successfully!")
            self.clear_incident_form()
            self.refresh_incident_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error adding incident: {str(e)}")
    
    def update_incident(self):
        selected_item = self.incident_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an incident to update")
            return
        
        try:
            cursor = self.connection.cursor()
            report_id = self.incident_tree.item(selected_item)['values'][0]  # use correct column name

            values = []
            for field in ["prisoner_id", "staff_id", "incident_date", "incident_description"]:
                if field == "incident_date":
                    value = self.incident_entries[field].get_date()
                elif field == "incident_description":
                    value = self.incident_entries[field].get("1.0", tk.END).strip()
                else:
                    value = self.incident_entries[field].get()

                if field in ["prisoner_id", "staff_id"] and value:
                    value = int(value)

                values.append(value)

            values.append(report_id)

            query = """UPDATE IncidentReport SET prisoner_id=%s, staff_id=%s, 
                    incident_date=%s, incident_description=%s WHERE report_id=%s"""

            
            cursor.execute(query, values)
            self.connection.commit()
            
            messagebox.showinfo("Success", "Incident report updated successfully!")
            self.refresh_incident_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error updating incident: {str(e)}")
    
    def delete_incident(self):
        selected_item = self.incident_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an incident to delete")
            return
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this incident?"):
            return
        
        try:
            cursor = self.connection.cursor()
            report_id = self.incident_tree.item(selected_item)['values'][0]
            
            query = "DELETE FROM IncidentReport WHERE report_id=%s"
            cursor.execute(query, (report_id,))
            self.connection.commit()
            
            messagebox.showinfo("Success", "Incident report deleted successfully!")
            self.clear_incident_form()
            self.refresh_incident_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting incident: {str(e)}")
    
    def load_incident_data(self, event):
        selected_item = self.incident_tree.selection()
        if not selected_item:
            return
        
        incident_data = self.incident_tree.item(selected_item)['values']
        
        # Clear form first
        self.clear_incident_form()
        
        # Set values in form
        self.incident_entries["prisoner_id"].insert(0, incident_data[1])
        self.incident_entries["staff_id"].insert(0, incident_data[2])
        self.incident_entries["incident_description"].insert("1.0", incident_data[3])
        
        if incident_data[4]:
            self.incident_entries["incident_date"].set_date(datetime.strptime(incident_data[4], '%Y-%m-%d').date())
    
    def clear_incident_form(self):
        for field, entry in self.incident_entries.items():
            if field == "incident_description":
                entry.delete("1.0", tk.END)
            elif field == "incident_date":
                entry.set_date(None)
            else:
                entry.delete(0, tk.END)
    
    def refresh_incident_list(self):
        try:
            cursor = self.connection.cursor()
            query = """SELECT report_id, prisoner_id, staff_id, incident_description, 
                      incident_date FROM IncidentReport"""
            cursor.execute(query)
            
            # Clear existing data
            for row in self.incident_tree.get_children():
                self.incident_tree.delete(row)
            
            # Add new data
            for row in cursor.fetchall():
                formatted_row = list(row)
                # Format date
                if formatted_row[4]:
                    formatted_row[4] = formatted_row[4].strftime('%Y-%m-%d')
                self.incident_tree.insert('', 'end', values=formatted_row)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading incidents: {str(e)}")

    # Medical Record CRUD Operations
    def add_medical(self):
        try:
            cursor = self.connection.cursor()
            
            values = []
            for field in ["prisoner_id", "doctor_id", "examination_date", "diagnosis", "treatment"]:
                if field == "examination_date":
                    value = self.medical_entries[field].get_date()
                elif field in ["diagnosis", "treatment"]:
                    value = self.medical_entries[field].get("1.0", tk.END).strip()
                else:
                    value = self.medical_entries[field].get()
                
                if field in ["prisoner_id", "doctor_id"] and value:
                    value = int(value)
                    
                values.append(value)
            
            query = """INSERT INTO MedicalRecord (prisoner_id, doctor_id, date_of_examination, 
                      diagnosis, treatment) VALUES (%s, %s, %s, %s, %s)"""
            
            cursor.execute(query, values)
            self.connection.commit()
            
            messagebox.showinfo("Success", "Medical record added successfully!")
            self.clear_medical_form()
            self.refresh_medical_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error adding medical record: {str(e)}")
    
    def update_medical(self):
        selected_item = self.medical_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a medical record to update")
            return
        
        try:
            cursor = self.connection.cursor()
            medical_id = self.medical_tree.item(selected_item)['values'][0]  # correct field name

            values = []
            for field in ["prisoner_id", "doctor_id", "examination_date", "diagnosis", "treatment"]:
                        if field == "examination_date":
                            value = self.medical_entries[field].get_date()
                        elif field in ["diagnosis", "treatment"]:
                            value = self.medical_entries[field].get("1.0", tk.END).strip()
                        else:
                            value = self.medical_entries[field].get()

                        if field in ["prisoner_id", "doctor_id"] and value:
                            value = int(value)

                        values.append(value)

            values.append(medical_id)

            query = """UPDATE MedicalRecord SET prisoner_id=%s, doctor_id=%s, 
                            date_of_examination=%s, diagnosis=%s, treatment=%s WHERE medical_id=%s"""

            
            cursor.execute(query, values)
            self.connection.commit()
            
            messagebox.showinfo("Success", "Medical record updated successfully!")
            self.refresh_medical_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error updating medical record: {str(e)}")
    
    def delete_medical(self):
        selected_item = self.medical_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a medical record to delete")
            return
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this medical record?"):
            return
        
        try:
            cursor = self.connection.cursor()
            medical_id = self.medical_tree.item(selected_item)['values'][0]
            
            query = "DELETE FROM MedicalRecord WHERE medical_id=%s"
            cursor.execute(query, (medical_id,))
            self.connection.commit()
            
            messagebox.showinfo("Success", "Medical record deleted successfully!")
            self.clear_medical_form()
            self.refresh_medical_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting medical record: {str(e)}")
    
    def load_medical_data(self, event):
        selected_item = self.medical_tree.selection()
        if not selected_item:
            return
        
        medical_data = self.medical_tree.item(selected_item)['values']
        
        # Clear form first
        self.clear_medical_form()
        
        # Set values in form
        self.medical_entries["prisoner_id"].insert(0, medical_data[1])
        self.medical_entries["diagnosis"].insert("1.0", medical_data[2])
        self.medical_entries["treatment"].insert("1.0", medical_data[3])
        
        if medical_data[4]:
            self.medical_entries["examination_date"].set_date(datetime.strptime(medical_data[4], '%Y-%m-%d').date())
        
        self.medical_entries["doctor_id"].insert(0, medical_data[5])
    
    def clear_medical_form(self):
        for field, entry in self.medical_entries.items():
            if field in ["diagnosis", "treatment"]:
                entry.delete("1.0", tk.END)
            elif field == "examination_date":
                entry.set_date(None)
            else:
                entry.delete(0, tk.END)
    
    def refresh_medical_list(self):
        try:
            cursor = self.connection.cursor()
            query = """SELECT medical_id, prisoner_id, diagnosis, treatment, 
                      date_of_examination, doctor_id FROM MedicalRecord"""
            cursor.execute(query)
            
            # Clear existing data
            for row in self.medical_tree.get_children():
                self.medical_tree.delete(row)
            
            # Add new data
            for row in cursor.fetchall():
                formatted_row = list(row)
                # Format date
                if formatted_row[4]:
                    formatted_row[4] = formatted_row[4].strftime('%Y-%m-%d')
                self.medical_tree.insert('', 'end', values=formatted_row)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading medical records: {str(e)}")

    def __del__(self):
        """Close database connection when object is destroyed"""
        if hasattr(self, 'connection') and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = PrisonerManagementSystem(root)
    root.mainloop()