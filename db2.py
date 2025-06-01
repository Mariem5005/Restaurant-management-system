import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import hashlib
import logging
logging.basicConfig(level=logging.DEBUG)

# DB connection function with error handling
def connect_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="RedSea3369",
            database="RestaurantDB1"
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to connect to database: {err}")
        return None

def show_signup():
    signup = tk.Toplevel()
    signup.title("📝 Sign Up")
    signup.geometry("400x250")
    signup.resizable(False, False)

    ttk.Label(signup, text="📝 Create a New Account", font=("Segoe UI", 14, "bold")).pack(pady=15)

    frame = ttk.Frame(signup, padding=10)
    frame.pack()

    ttk.Label(frame, text="New Username:").grid(row=0, column=0, sticky="e", pady=5)
    new_username_entry = ttk.Entry(frame, width=30)
    new_username_entry.grid(row=0, column=1, pady=5)

    ttk.Label(frame, text="New Password:").grid(row=1, column=0, sticky="e", pady=5)
    new_password_entry = ttk.Entry(frame, show="*", width=30)
    new_password_entry.grid(row=1, column=1, pady=5)

    def register_user():
        username = new_username_entry.get().strip()
        password = new_password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Input Error", "All fields are required.")
            return

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            conn = connect_db()
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM UserLogin WHERE username=%s", (username,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Username already exists.")
            else:
                cursor.execute("INSERT INTO UserLogin (username, password) VALUES (%s, %s)",
                               (username, hashed_password))
                conn.commit()
                messagebox.showinfo("Success", "Account created successfully.")
                signup.destroy()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    ttk.Button(frame, text="Register", command=register_user).grid(row=2, column=0, columnspan=2, pady=15)

def show_login():
    login = tk.Tk()
    login.title("🔐 Login")
    login.geometry("400x300")
    login.resizable(False, False)

    ttk.Label(login, text="🔐 Please Login", font=("Segoe UI", 16, "bold")).pack(pady=20)

    frame = ttk.Frame(login, padding=10)
    frame.pack()

    ttk.Label(frame, text="Username:").grid(row=0, column=0, sticky="e", pady=5)
    username_entry = ttk.Entry(frame, width=30)
    username_entry.grid(row=0, column=1, pady=5)

    ttk.Label(frame, text="Password:").grid(row=1, column=0, sticky="e", pady=5)
    password_entry = ttk.Entry(frame, show="*", width=30)
    password_entry.grid(row=1, column=1, pady=5)

    def validate_login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            conn = connect_db()
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM UserLogin WHERE username=%s AND password=%s",
                           (username, hashed_password))
            if cursor.fetchone():
                login.destroy()
                show_main_gui()
            else:
                messagebox.showerror("Error", "Invalid credentials")
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    ttk.Button(frame, text="Login", command=validate_login).grid(row=2, column=0, columnspan=2, pady=15)
    ttk.Button(login, text="Sign Up", command=show_signup).pack()

    login.mainloop()

def show_main_gui():
    root = tk.Tk()
    root.title("🍽️ Restaurant Management System")
    root.geometry("1150x750")
    root.resizable(False, False)

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TLabel", font=("Segoe UI", 10))
    style.configure("TButton", font=("Segoe UI", 10, "bold"), background="#4CAF50", foreground="white")
    style.configure("Treeview", font=("Segoe UI", 9))
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    ttk.Label(root, text="Restaurant Management System", font=("Segoe UI", 18, "bold")).pack(pady=10)

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # Create tabs
    customer_tab = ttk.Frame(notebook)
    menu_tab = ttk.Frame(notebook)
    orders_tab = ttk.Frame(notebook)
    employee_tab = ttk.Frame(notebook)
    reports_tab = ttk.Frame(notebook)

    notebook.add(customer_tab, text="Customers")
    notebook.add(menu_tab, text="Menu Items")
    notebook.add(orders_tab, text="Orders & Payments")
    notebook.add(employee_tab, text="Employees & Delivery")
    notebook.add(reports_tab, text="Reports & History")

    build_customer_tab(customer_tab)
    build_menu_tab(menu_tab)
    build_orders_tab(orders_tab)
    build_employee_tab(employee_tab)
    build_reports_tab(reports_tab)

    root.mainloop()

def build_customer_tab(frame):
    conn = connect_db()
    if conn is None:
        return

    cursor = conn.cursor()

    # Frames for forms and table
    form_frame = ttk.LabelFrame(frame, text="Add / Update Customer", padding=10)
    form_frame.pack(side="left", fill="y", padx=10, pady=10)

    columns = ["Customer_ID", "First_Name", "Last_Name", "Email", "Street", "House_Number", "City", "Customer_Type"]
    tree_frame = ttk.LabelFrame(frame, text="Customers List", padding=10)
    tree_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    entries = {}
    for i, field in enumerate(columns):
        ttk.Label(form_frame, text=field.replace("_", " ")).grid(row=i, column=0, sticky="w", pady=2)
        entry = ttk.Entry(form_frame, width=30)
        entry.grid(row=i, column=1, pady=2)
        entries[field] = entry

    def clear_entries():
        for e in entries.values():
            e.delete(0, tk.END)

    def save_customer():
        try:
            vals = [entries[col].get().strip() for col in columns]
            if not vals[0].isdigit():
                messagebox.showerror("Input Error", "Customer ID must be a number.")
                return
            cust_id = int(vals[0])

            cursor.execute("SELECT Customer_ID FROM Customer WHERE Customer_ID=%s", (cust_id,))
            if cursor.fetchone():
                cursor.execute("""
                    UPDATE Customer SET
                    Customer_FirstName=%s, Customer_LastName=%s, Email=%s, Street=%s, 
                    House_Number=%s, City=%s, Customer_Type=%s
                    WHERE Customer_ID=%s
                """, (vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7], cust_id))
                conn.commit()
                messagebox.showinfo("Updated", "Customer updated successfully.")
            else:
                cursor.execute("""
                    INSERT INTO Customer (Customer_ID, Customer_FirstName, Customer_LastName, 
                    Email, Street, House_Number, City, Customer_Type)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """, tuple(vals))
                conn.commit()
                messagebox.showinfo("Added", "Customer added successfully.")

            load_customers()
            clear_entries()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def delete_customer():
        try:
            cust_id = entries["Customer_ID"].get().strip()
            if not cust_id.isdigit():
                messagebox.showerror("Input Error", "Enter a valid Customer ID to delete.")
                return
            cursor.execute("DELETE FROM Customer WHERE Customer_ID=%s", (int(cust_id),))
            conn.commit()
            messagebox.showinfo("Deleted", f"Customer {cust_id} deleted.")
            load_customers()
            clear_entries()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
    for col in columns:
        tree.heading(col, text=col.replace("_", " "))
        tree.column(col, width=100)
    tree.pack(fill="both", expand=True)

    def on_tree_select(event):
        selected = tree.focus()
        if selected:
            vals = tree.item(selected, "values")
            for i, col in enumerate(columns):
                entries[col].delete(0, tk.END)
                entries[col].insert(0, vals[i])

    tree.bind("<<TreeviewSelect>>", on_tree_select)

    def load_customers():
        try:
            cursor.execute("""
                SELECT Customer_ID, Customer_FirstName, Customer_LastName, Email, 
                Street, House_Number, City, Customer_Type 
                FROM Customer ORDER BY Customer_ID
            """)
            rows = cursor.fetchall()
            tree.delete(*tree.get_children())
            for row in rows:
                tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    load_customers()

    btn_frame = ttk.Frame(form_frame)
    btn_frame.grid(row=len(columns), column=0, columnspan=2, pady=10)

    ttk.Button(btn_frame, text="Add / Update", command=save_customer).grid(row=0, column=0, padx=5)
    ttk.Button(btn_frame, text="Delete", command=delete_customer).grid(row=0, column=1, padx=5)
    ttk.Button(btn_frame, text="Clear", command=clear_entries).grid(row=0, column=2, padx=5)

    def on_tab_close():
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
        frame.destroy()

    frame.bind("<Destroy>", lambda e: on_tab_close())

def build_menu_tab(frame):
    conn = connect_db()
    if conn is None:
        return

    cursor = conn.cursor()

    form_frame = ttk.LabelFrame(frame, text="Add / Update Menu Item", padding=10)
    form_frame.pack(side="left", fill="y", padx=10, pady=10)

    columns = ["Item_ID", "Name", "Description", "Price"]
    tree_frame = ttk.LabelFrame(frame, text="Menu Items List", padding=10)
    tree_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    entries = {}
    for i, field in enumerate(columns):
        ttk.Label(form_frame, text=field.replace("_", " ")).grid(row=i, column=0, sticky="w", pady=2)
        entry = ttk.Entry(form_frame, width=30)
        entry.grid(row=i, column=1, pady=2)
        entries[field] = entry

    def clear_entries():
        for e in entries.values():
            e.delete(0, tk.END)

    def save_menu_item():
        try:
            vals = [entries[col].get().strip() for col in columns]
            if not vals[0].isdigit():
                messagebox.showerror("Input Error", "Item ID must be a number.")
                return
            item_id = int(vals[0])

            try:
                price = float(vals[3])
                if price <= 0:
                    raise ValueError("Price must be positive")
            except ValueError:
                messagebox.showerror("Input Error", "Price must be a valid positive number.")
                return

            cursor.execute("SELECT Item_ID FROM Menu_Item WHERE Item_ID=%s", (item_id,))
            if cursor.fetchone():
                cursor.execute("""
                    UPDATE Menu_Item SET Name=%s, Description=%s, Price=%s WHERE Item_ID=%s
                """, (vals[1], vals[2], price, item_id))
                conn.commit()
                messagebox.showinfo("Updated", "Menu item updated.")
            else:
                cursor.execute("""
                    INSERT INTO Menu_Item (Item_ID, Name, Description, Price) VALUES (%s,%s,%s,%s)
                """, (item_id, vals[1], vals[2], price))
                conn.commit()
                messagebox.showinfo("Added", "Menu item added.")

            load_menu_items()
            clear_entries()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def delete_menu_item():
        try:
            item_id = entries["Item_ID"].get().strip()
            if not item_id.isdigit():
                messagebox.showerror("Input Error", "Enter a valid Item ID to delete.")
                return
            cursor.execute("DELETE FROM Menu_Item WHERE Item_ID=%s", (int(item_id),))
            conn.commit()
            messagebox.showinfo("Deleted", f"Menu Item {item_id} deleted.")
            load_menu_items()
            clear_entries()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
    for col in columns:
        tree.heading(col, text=col.replace("_", " "))
        tree.column(col, width=120)
    tree.pack(fill="both", expand=True)

    def on_tree_select(event):
        selected = tree.focus()
        if selected:
            vals = tree.item(selected, "values")
            for i, col in enumerate(columns):
                entries[col].delete(0, tk.END)
                entries[col].insert(0, vals[i])

    tree.bind("<<TreeviewSelect>>", on_tree_select)

    def load_menu_items():
        try:
            cursor.execute("SELECT Item_ID, Name, Description, Price FROM Menu_Item ORDER BY Item_ID")
            rows = cursor.fetchall()
            tree.delete(*tree.get_children())
            for row in rows:
                tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    load_menu_items()

    btn_frame = ttk.Frame(form_frame)
    btn_frame.grid(row=len(columns), column=0, columnspan=2, pady=10)

    ttk.Button(btn_frame, text="Add / Update", command=save_menu_item).grid(row=0, column=0, padx=5)
    ttk.Button(btn_frame, text="Delete", command=delete_menu_item).grid(row=0, column=1, padx=5)
    ttk.Button(btn_frame, text="Clear", command=clear_entries).grid(row=0, column=2, padx=5)

    def on_tab_close():
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
        frame.destroy()

    frame.bind("<Destroy>", lambda e: on_tab_close())

def build_orders_tab(frame):
    conn = connect_db()
    if conn is None:
        return

    cursor = conn.cursor()

    notebook = ttk.Notebook(frame)
    notebook.pack(fill='both', expand=True, padx=10, pady=10)

    # Orders Tab
    orders_tab = ttk.Frame(notebook)
    notebook.add(orders_tab, text="Orders")

    # Payments Tab
    payments_tab = ttk.Frame(notebook)
    notebook.add(payments_tab, text="Payments")

    # ===== Orders Management =====
    orders_form_frame = ttk.LabelFrame(orders_tab, text="Order Details", padding=10)
    orders_form_frame.pack(side='left', fill='y', padx=5, pady=5)

    order_cols = ["Order_ID", "Customer_ID", "Order_Time", "Status", "Order_Type"]
    order_entries = {}

    for i, col in enumerate(order_cols):
        ttk.Label(orders_form_frame, text=col.replace("_", " ")).grid(row=i, column=0, sticky='w', pady=2)
        if col == "Status":
            status_var = tk.StringVar()
            dropdown = ttk.Combobox(orders_form_frame, textvariable=status_var,
                                    values=["Pending", "Processing", "Completed", "Cancelled"])
            dropdown.grid(row=i, column=1, pady=2)
            order_entries[col] = dropdown
        elif col == "Order_Type":
            type_var = tk.StringVar()
            dropdown = ttk.Combobox(orders_form_frame, textvariable=type_var,
                                    values=["InDine", "Delivery"])
            dropdown.grid(row=i, column=1, pady=2)
            order_entries[col] = dropdown
        else:
            entry = ttk.Entry(orders_form_frame, width=25)
            entry.grid(row=i, column=1, pady=2)
            order_entries[col] = entry

    def clear_order_entries():
        for e in order_entries.values():
            if isinstance(e, ttk.Entry):
                e.delete(0, tk.END)
            elif isinstance(e, ttk.Combobox):
                e.set('')

    def save_order():
        try:
            vals = [order_entries[col].get().strip() if isinstance(order_entries[col], ttk.Entry)
                    else order_entries[col].get()
                    for col in order_cols]

            if not vals[0].isdigit() or not vals[1].isdigit():
                messagebox.showerror("Input Error", "Order ID and Customer ID must be numbers.")
                return

            order_id = int(vals[0])
            customer_id = int(vals[1])
            order_time = vals[2]
            status = vals[3]
            order_type = vals[4]

            # Verify customer exists
            cursor.execute("SELECT Customer_ID FROM Customer WHERE Customer_ID=%s", (customer_id,))
            if not cursor.fetchone():
                messagebox.showerror("Error", "Customer doesn't exist.")
                return

            cursor.execute("SELECT Order_ID FROM Orders WHERE Order_ID=%s", (order_id,))
            if cursor.fetchone():
                cursor.execute("""
                UPDATE Orders SET 
                Customer_ID=%s, Order_Time=%s, Status=%s, Order_Type=%s
                WHERE Order_ID=%s
            """, (customer_id, order_time, status, order_type, order_id))
                messagebox.showinfo("Success", "Order updated successfully.")
            else:
                cursor.execute("""
                INSERT INTO Orders (Order_ID, Customer_ID, Order_Time, Status, Order_Type, Restaurant_ID)
                VALUES (%s, %s, %s, %s, %s, 1)
            """, (order_id, customer_id, order_time, status, order_type))
                messagebox.showinfo("Success", "New order added successfully.")

            conn.commit()  # Explicit commit
            load_orders()  # Refresh the orders list
            clear_order_entries()
        except Exception as e:
            conn.rollback()  # Rollback on error
            messagebox.showerror("Database Error", str(e))

    def delete_order():
        order_id = order_entries["Order_ID"].get().strip()
        if not order_id.isdigit():
            messagebox.showerror("Input Error", "Please enter a valid Order ID.")
            return

        try:
            cursor.execute("DELETE FROM Orders WHERE Order_ID=%s", (int(order_id),))
            conn.commit()
            messagebox.showinfo("Success", f"Order {order_id} deleted successfully.")
            load_orders()
            clear_order_entries()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    # Order items management
    items_frame = ttk.LabelFrame(orders_tab, text="Order Items", padding=10)
    items_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)

    ttk.Label(items_frame, text="Item ID:").grid(row=0, column=0)
    item_id_entry = ttk.Entry(items_frame, width=15)
    item_id_entry.grid(row=0, column=1)

    ttk.Label(items_frame, text="Quantity:").grid(row=0, column=2)
    quantity_entry = ttk.Entry(items_frame, width=15)
    quantity_entry.grid(row=0, column=3)

    def add_item_to_order():
        order_id = order_entries["Order_ID"].get().strip()
        item_id = item_id_entry.get().strip()
        quantity = quantity_entry.get().strip()

        if not order_id or not item_id or not quantity:
            messagebox.showerror("Input Error", "All fields are required.")
            return

        try:
        # First verify the order exists
            cursor.execute("SELECT Order_ID FROM Orders WHERE Order_ID=%s", (int(order_id),))
            if not cursor.fetchone():
                messagebox.showerror("Error", "Order doesn't exist. Create the order first.")
                return

        # Verify the menu item exists
            cursor.execute("SELECT Item_ID FROM Menu_Item WHERE Item_ID=%s", (int(item_id),))
            if not cursor.fetchone():
                messagebox.showerror("Error", "Menu item doesn't exist.")
                return

        # Now add the item
            cursor.execute("INSERT INTO contains (Order_ID, Item_ID, Quantity) VALUES (%s, %s, %s)",
                       (int(order_id), int(item_id), int(quantity)))
            conn.commit()  # Explicit commit
            messagebox.showinfo("Success", "Item added to order.")
            load_order_items(int(order_id))
            item_id_entry.delete(0, tk.END)
            quantity_entry.delete(0, tk.END)
        except Exception as e:
            conn.rollback()  # Rollback on error
            messagebox.showerror("Database Error", str(e))

    ttk.Button(items_frame, text="Add Item", command=add_item_to_order).grid(row=0, column=4, padx=5)

    order_items_tree = ttk.Treeview(items_frame, columns=("Item_ID", "Name", "Price", "Quantity"), show="headings")
    order_items_tree.heading("Item_ID", text="Item ID")
    order_items_tree.heading("Name", text="Name")
    order_items_tree.heading("Price", text="Price")
    order_items_tree.heading("Quantity", text="Quantity")
    order_items_tree.grid(row=1, column=0, columnspan=5, pady=10, sticky='nsew')

    def load_order_items(order_id):
        try:
            cursor.execute("""
                SELECT mi.Item_ID, mi.Name, mi.Price, c.Quantity
                FROM contains c
                JOIN Menu_Item mi ON c.Item_ID = mi.Item_ID
                WHERE c.Order_ID = %s
            """, (order_id,))
            items = cursor.fetchall()
            order_items_tree.delete(*order_items_tree.get_children())
            for item in items:
                order_items_tree.insert("", "end", values=item)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    # Orders Treeview
    orders_tree_frame = ttk.Frame(orders_tab)
    orders_tree_frame.pack(fill='both', expand=True)

    orders_tree = ttk.Treeview(orders_tree_frame, columns=order_cols, show="headings")
    for col in order_cols:
        orders_tree.heading(col, text=col.replace("_", " "))
        orders_tree.column(col, width=100)
    orders_tree.pack(side='left', fill='both', expand=True)

    scrollbar = ttk.Scrollbar(orders_tree_frame, orient="vertical", command=orders_tree.yview)
    scrollbar.pack(side='right', fill='y')
    orders_tree.configure(yscrollcommand=scrollbar.set)

    def load_orders():
        try:
            cursor.execute("SELECT Order_ID, Customer_ID, Order_Time, Status, Order_Type FROM Orders")
            orders = cursor.fetchall()
            orders_tree.delete(*orders_tree.get_children())
            for order in orders:
                orders_tree.insert("", "end", values=order)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def on_order_select(event):
        selected = orders_tree.focus()
        if selected:
            values = orders_tree.item(selected, "values")
            clear_order_entries()
            for i, col in enumerate(order_cols):
                if col in ["Status", "Order_Type"]:
                    order_entries[col].set(values[i])
                else:
                    order_entries[col].delete(0, tk.END)
                    order_entries[col].insert(0, values[i])

            load_order_items(int(values[0]))

    orders_tree.bind("<<TreeviewSelect>>", on_order_select)

    # Order buttons
    btn_frame = ttk.Frame(orders_form_frame)
    btn_frame.grid(row=len(order_cols)+1, column=0, columnspan=2, pady=10)

    ttk.Button(btn_frame, text="Save", command=save_order).grid(row=0, column=0, padx=5)
    ttk.Button(btn_frame, text="Delete", command=delete_order).grid(row=0, column=1, padx=5)
    ttk.Button(btn_frame, text="Clear", command=clear_order_entries).grid(row=0, column=2, padx=5)

    # ===== Payments Management =====
    payments_form_frame = ttk.LabelFrame(payments_tab, text="Payment Details", padding=10)
    payments_form_frame.pack(side='left', fill='y', padx=5, pady=5)

    payment_cols = ["Payment_ID", "Order_ID", "Payment_Method", "Amount", "Payment_Date"]
    payment_entries = {}

    for i, col in enumerate(payment_cols):
        ttk.Label(payments_form_frame, text=col.replace("_", " ")).grid(row=i, column=0, sticky='w', pady=2)
        entry = ttk.Entry(payments_form_frame, width=25)
        entry.grid(row=i, column=1, pady=2)
        payment_entries[col] = entry

    method_var = tk.StringVar()
    method_dropdown = ttk.Combobox(payments_form_frame, textvariable=method_var,
                                   values=["Ca", "CC", "OL"])
    method_dropdown.grid(row=2, column=1, pady=2)
    payment_entries["Payment_Method"] = method_dropdown

    def clear_payment_entries():
        for e in payment_entries.values():
            if isinstance(e, ttk.Entry):
                e.delete(0, tk.END)
            elif isinstance(e, ttk.Combobox):
                e.set('')

    def save_payment():
        try:
            vals = [payment_entries[col].get().strip() if isinstance(payment_entries[col], ttk.Entry)
                    else payment_entries[col].get()
                    for col in payment_cols]

            if not vals[0].isdigit() or not vals[1].isdigit():
                messagebox.showerror("Input Error", "Payment ID and Order ID must be numbers.")
                return

            payment_id = int(vals[0])
            order_id = int(vals[1])
            method = vals[2]

            try:
                amount = float(vals[3])
            except ValueError:
                messagebox.showerror("Input Error", "Amount must be a number.")
                return

            payment_date = vals[4]

            cursor.execute("SELECT Payment_ID FROM Payment WHERE Payment_ID=%s", (payment_id,))
            if cursor.fetchone():
                cursor.execute("""
                    UPDATE Payment SET 
                    Order_ID=%s, Payment_Method=%s, Amount=%s, Payment_Date=%s
                    WHERE Payment_ID=%s
                """, (order_id, method, amount, payment_date, payment_id))
                messagebox.showinfo("Success", "Payment updated successfully.")
            else:
                cursor.execute("""
                    INSERT INTO Payment (Payment_ID, Order_ID, Payment_Method, Amount, Payment_Date)
                    VALUES (%s, %s, %s, %s, %s)
                """, (payment_id, order_id, method, amount, payment_date))
                messagebox.showinfo("Success", "New payment added successfully.")

            conn.commit()
            load_payments()
            clear_payment_entries()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def delete_payment():
        payment_id = payment_entries["Payment_ID"].get().strip()
        if not payment_id.isdigit():
            messagebox.showerror("Input Error", "Please enter a valid Payment ID.")
            return

        try:
            cursor.execute("DELETE FROM Payment WHERE Payment_ID=%s", (int(payment_id),))
            conn.commit()
            messagebox.showinfo("Success", f"Payment {payment_id} deleted successfully.")
            load_payments()
            clear_payment_entries()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    # Payments Treeview
    payments_tree_frame = ttk.Frame(payments_tab)
    payments_tree_frame.pack(fill='both', expand=True)

    payments_tree = ttk.Treeview(payments_tree_frame, columns=payment_cols, show="headings")
    for col in payment_cols:
        payments_tree.heading(col, text=col.replace("_", " "))
        payments_tree.column(col, width=100)
    payments_tree.pack(side='left', fill='both', expand=True)

    scrollbar = ttk.Scrollbar(payments_tree_frame, orient="vertical", command=payments_tree.yview)
    scrollbar.pack(side='right', fill='y')
    payments_tree.configure(yscrollcommand=scrollbar.set)

    def load_payments():
        try:
            cursor.execute("""
                SELECT Payment_ID, Order_ID, Payment_Method, Amount, Payment_Date 
                FROM Payment
            """)
            payments = cursor.fetchall()
            payments_tree.delete(*payments_tree.get_children())
            for payment in payments:
                payments_tree.insert("", "end", values=payment)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def on_payment_select(event):
        selected = payments_tree.focus()
        if selected:
            values = payments_tree.item(selected, "values")
            clear_payment_entries()
            for i, col in enumerate(payment_cols):
                if col == "Payment_Method":
                    payment_entries[col].set(values[i])
                else:
                    payment_entries[col].delete(0, tk.END)
                    payment_entries[col].insert(0, values[i])

    payments_tree.bind("<<TreeviewSelect>>", on_payment_select)

    # Payment buttons
    btn_frame = ttk.Frame(payments_form_frame)
    btn_frame.grid(row=len(payment_cols)+1, column=0, columnspan=2, pady=10)

    ttk.Button(btn_frame, text="Save", command=save_payment).grid(row=0, column=0, padx=5)
    ttk.Button(btn_frame, text="Delete", command=delete_payment).grid(row=0, column=1, padx=5)
    ttk.Button(btn_frame, text="Clear", command=clear_payment_entries).grid(row=0, column=2, padx=5)

    # Initial load
    load_orders()
    load_payments()

    def on_tab_close():
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
        frame.destroy()

    frame.bind("<Destroy>", lambda e: on_tab_close())

def build_employee_tab(frame):
    conn = connect_db()
    if conn is None:
        return

    cursor = conn.cursor()

    notebook = ttk.Notebook(frame)
    notebook.pack(fill='both', expand=True, padx=10, pady=10)

    # Employees Tab
    employees_tab = ttk.Frame(notebook)
    notebook.add(employees_tab, text="Employees")

    # Delivery Tab
    delivery_tab = ttk.Frame(notebook)
    notebook.add(delivery_tab, text="Delivery")

    # ===== Employees Management =====
    emp_form_frame = ttk.LabelFrame(employees_tab, text="Employee Details", padding=10)
    emp_form_frame.pack(side='left', fill='y', padx=5, pady=5)

    emp_cols = ["Employee_ID", "Employee_FirstName", "Employee_LastName", "Salary", "Role", "Username", "Email"]
    emp_entries = {}

    for i, col in enumerate(emp_cols):
        ttk.Label(emp_form_frame, text=col.replace("_", " ")).grid(row=i, column=0, sticky='w', pady=2)
        if col == "Role":
            role_var = tk.StringVar()
            dropdown = ttk.Combobox(emp_form_frame, textvariable=role_var,
                                    values=["D", "W", "C"])  # D=Delivery, W=Waiter, C=Chef
            dropdown.grid(row=i, column=1, pady=2)
            emp_entries[col] = dropdown
        else:
            entry = ttk.Entry(emp_form_frame, width=25)
            entry.grid(row=i, column=1, pady=2)
            emp_entries[col] = entry

    def clear_emp_entries():
        for e in emp_entries.values():
            if isinstance(e, ttk.Entry):
                e.delete(0, tk.END)
            elif isinstance(e, ttk.Combobox):
                e.set('')

    def save_employee():
        try:
            vals = [emp_entries[col].get().strip() if isinstance(emp_entries[col], ttk.Entry)
                    else emp_entries[col].get()
                    for col in emp_cols]

            if not vals[0].isdigit():
                messagebox.showerror("Input Error", "Employee ID must be a number.")
                return

            emp_id = int(vals[0])
            first_name = vals[1]
            last_name = vals[2]

            try:
                salary = float(vals[3])
            except ValueError:
                messagebox.showerror("Input Error", "Salary must be a number.")
                return

            role = vals[4]
            username = vals[5]
            email = vals[6]

            cursor.execute("SELECT Employee_ID FROM Employee WHERE Employee_ID=%s", (emp_id,))
            if cursor.fetchone():
                cursor.execute("""
                    UPDATE Employee SET 
                    Employee_FirstName=%s, Employee_LastName=%s, Salary=%s, Role=%s,
                    Username=%s, Email=%s
                    WHERE Employee_ID=%s
                """, (first_name, last_name, salary, role, username, email, emp_id))
                messagebox.showinfo("Success", "Employee updated successfully.")
            else:
                cursor.execute("""
                    INSERT INTO Employee (Employee_ID, Employee_FirstName, Employee_LastName, 
                    Salary, Role, Username, Email)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (emp_id, first_name, last_name, salary, role, username, email))
                messagebox.showinfo("Success", "New employee added successfully.")

            conn.commit()
            load_employees()
            clear_emp_entries()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def delete_employee():
        emp_id = emp_entries["Employee_ID"].get().strip()
        if not emp_id.isdigit():
            messagebox.showerror("Input Error", "Please enter a valid Employee ID.")
            return

        try:
            cursor.execute("DELETE FROM Employee WHERE Employee_ID=%s", (int(emp_id),))
            conn.commit()
            messagebox.showinfo("Success", f"Employee {emp_id} deleted successfully.")
            load_employees()
            clear_emp_entries()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    # Employees Treeview
    emp_tree_frame = ttk.Frame(employees_tab)
    emp_tree_frame.pack(fill='both', expand=True)

    emp_tree = ttk.Treeview(emp_tree_frame, columns=emp_cols, show="headings")
    for col in emp_cols:
        emp_tree.heading(col, text=col.replace("_", " "))
        emp_tree.column(col, width=100)
    emp_tree.pack(side='left', fill='both', expand=True)

    scrollbar = ttk.Scrollbar(emp_tree_frame, orient="vertical", command=emp_tree.yview)
    scrollbar.pack(side='right', fill='y')
    emp_tree.configure(yscrollcommand=scrollbar.set)

    def load_employees():
        try:
            cursor.execute("""
                SELECT Employee_ID, Employee_FirstName, Employee_LastName, 
                       Salary, Role, Username, Email 
                FROM Employee
            """)
            employees = cursor.fetchall()
            emp_tree.delete(*emp_tree.get_children())
            for emp in employees:
                emp_tree.insert("", "end", values=emp)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def on_emp_select(event):
        selected = emp_tree.focus()
        if selected:
            values = emp_tree.item(selected, "values")
            clear_emp_entries()
            for i, col in enumerate(emp_cols):
                if col == "Role":
                    emp_entries[col].set(values[i])
                else:
                    emp_entries[col].delete(0, tk.END)
                    emp_entries[col].insert(0, values[i])

    emp_tree.bind("<<TreeviewSelect>>", on_emp_select)

    # Employee buttons
    btn_frame = ttk.Frame(emp_form_frame)
    btn_frame.grid(row=len(emp_cols)+1, column=0, columnspan=2, pady=10)

    ttk.Button(btn_frame, text="Save", command=save_employee).grid(row=0, column=0, padx=5)
    ttk.Button(btn_frame, text="Delete", command=delete_employee).grid(row=0, column=1, padx=5)
    ttk.Button(btn_frame, text="Clear", command=clear_emp_entries).grid(row=0, column=2, padx=5)

    # ===== Delivery Management =====
    delivery_form_frame = ttk.LabelFrame(delivery_tab, text="Delivery Details", padding=10)
    delivery_form_frame.pack(side='left', fill='y', padx=5, pady=5)

    delivery_cols = ["Employee_ID", "First_Name", "Last_Name", "Availability", "Assigned_Areas"]
    delivery_entries = {}

    for i, col in enumerate(delivery_cols):
        ttk.Label(delivery_form_frame, text=col.replace("_", " ")).grid(row=i, column=0, sticky='w', pady=2)
        if col in ["First_Name", "Last_Name"]:
            label = ttk.Label(delivery_form_frame, text="", width=25)
            label.grid(row=i, column=1, pady=2)
            delivery_entries[col] = label
        elif col == "Availability":
            avail_var = tk.StringVar()
            dropdown = ttk.Combobox(delivery_form_frame, textvariable=avail_var,
                                    values=["Available", "Unavailable"])
            dropdown.grid(row=i, column=1, pady=2)
            delivery_entries[col] = dropdown
        elif col == "Assigned_Areas":
            areas_var = tk.StringVar()
            cursor.execute("SELECT Area_code FROM Delivery_Area")
            areas = [area[0] for area in cursor.fetchall()]
            dropdown = ttk.Combobox(delivery_form_frame, textvariable=areas_var, values=areas)
            dropdown.grid(row=i, column=1, pady=2)
            delivery_entries[col] = dropdown
        else:
            entry = ttk.Entry(delivery_form_frame, width=25)
            entry.grid(row=i, column=1, pady=2)
            delivery_entries[col] = entry

    def clear_delivery_entries():
        for e in delivery_entries.values():
            if isinstance(e, ttk.Entry):
                e.delete(0, tk.END)
            elif isinstance(e, ttk.Combobox):
                e.set('')
            elif isinstance(e, ttk.Label):
                e.config(text="")

    def save_delivery():
        try:
            emp_id = delivery_entries["Employee_ID"].get().strip()
            if not emp_id.isdigit():
                messagebox.showerror("Input Error", "Employee ID must be a number.")
                return

            emp_id = int(emp_id)
            availability = 1 if delivery_entries["Availability"].get() == "Available" else 0
            area_code = delivery_entries["Assigned_Areas"].get()

            cursor.execute("SELECT Role FROM Employee WHERE Employee_ID=%s", (emp_id,))
            emp = cursor.fetchone()
            if not emp:
                messagebox.showerror("Error", "Employee not found.")
                return
            if emp[0] != 'Delivery':
                messagebox.showerror("Error", "Employee is not a delivery person.")
                return

            cursor.execute("SELECT Employee_ID FROM Delivery_Boy WHERE Employee_ID=%s", (emp_id,))
            if cursor.fetchone():
                cursor.execute("""
                    UPDATE Delivery_Boy SET 
                    Availability=%s
                    WHERE Employee_ID=%s
                """, (availability, emp_id))

                cursor.execute("DELETE FROM Delivery_Assignment WHERE Employee_ID=%s", (emp_id,))
                if area_code:
                    cursor.execute("""
                        INSERT INTO Delivery_Assignment (Employee_ID, Area_Code) 
                        VALUES (%s, %s)
                    """, (emp_id, area_code))

                messagebox.showinfo("Success", "Delivery person updated successfully.")
            else:
                cursor.execute("""
                    INSERT INTO Delivery_Boy (Employee_ID, Availability)
                    VALUES (%s, %s)
                """, (emp_id, availability))

                if area_code:
                    cursor.execute("""
                        INSERT INTO Delivery_Assignment (Employee_ID, Area_Code) 
                        VALUES (%s, %s)
                    """, (emp_id, area_code))

                messagebox.showinfo("Success", "New delivery person added successfully.")

            conn.commit()
            load_delivery()
            clear_delivery_entries()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def delete_delivery():
        emp_id = delivery_entries["Employee_ID"].get().strip()
        if not emp_id.isdigit():
            messagebox.showerror("Input Error", "Please enter a valid Employee ID.")
            return

        try:
            cursor.execute("DELETE FROM Delivery_Boy WHERE Employee_ID=%s", (int(emp_id),))
            conn.commit()
            messagebox.showinfo("Success", f"Delivery person {emp_id} deleted successfully.")
            load_delivery()
            clear_delivery_entries()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    # Delivery Treeview
    delivery_tree_frame = ttk.Frame(delivery_tab)
    delivery_tree_frame.pack(fill='both', expand=True)

    delivery_tree = ttk.Treeview(delivery_tree_frame, columns=delivery_cols, show="headings")
    for col in delivery_cols:
        delivery_tree.heading(col, text=col.replace("_", " "))
        delivery_tree.column(col, width=100)
    delivery_tree.pack(side='left', fill='both', expand=True)

    scrollbar = ttk.Scrollbar(delivery_tree_frame, orient="vertical", command=delivery_tree.yview)
    scrollbar.pack(side='right', fill='y')
    delivery_tree.configure(yscrollcommand=scrollbar.set)

    def load_delivery():
        try:
            cursor.execute("""
                SELECT e.Employee_ID, e.Employee_FirstName, e.Employee_LastName, 
                       db.Availability, GROUP_CONCAT(da.Area_Code SEPARATOR ', ') AS Areas
                FROM Employee e
                JOIN Delivery_Boy db ON e.Employee_ID = db.Employee_ID
                LEFT JOIN Delivery_Assignment da ON db.Employee_ID = da.Employee_ID
                GROUP BY e.Employee_ID
            """)
            delivery_boys = cursor.fetchall()
            delivery_tree.delete(*delivery_tree.get_children())
            for boy in delivery_boys:
                availability = "Available" if boy[3] else "Unavailable"
                delivery_tree.insert("", "end", values=(boy[0], boy[1], boy[2], availability, boy[4]))
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def on_delivery_select(event):
        selected = delivery_tree.focus()
        if selected:
            values = delivery_tree.item(selected, "values")
            clear_delivery_entries()
            delivery_entries["Employee_ID"].delete(0, tk.END)
            delivery_entries["Employee_ID"].insert(0, values[0])
            delivery_entries["First_Name"].config(text=values[1])
            delivery_entries["Last_Name"].config(text=values[2])
            delivery_entries["Availability"].set(values[3])
            if len(values) > 4 and values[4]:
                delivery_entries["Assigned_Areas"].set(values[4])

    delivery_tree.bind("<<TreeviewSelect>>", on_delivery_select)

    # Delivery buttons
    btn_frame = ttk.Frame(delivery_form_frame)
    btn_frame.grid(row=len(delivery_cols)+1, column=0, columnspan=2, pady=10)

    ttk.Button(btn_frame, text="Save", command=save_delivery).grid(row=0, column=0, padx=5)
    ttk.Button(btn_frame, text="Delete", command=delete_delivery).grid(row=0, column=1, padx=5)
    ttk.Button(btn_frame, text="Clear", command=clear_delivery_entries).grid(row=0, column=2, padx=5)

    # Delivery Orders Section
    delivery_orders_frame = ttk.LabelFrame(delivery_tab, text="Delivery Orders", padding=10)
    delivery_orders_frame.pack(fill='both', expand=True, padx=5, pady=5)

    ttk.Label(delivery_orders_frame, text="Order ID:").grid(row=0, column=0)
    delivery_order_id_entry = ttk.Entry(delivery_orders_frame, width=15)
    delivery_order_id_entry.grid(row=0, column=1)

    ttk.Label(delivery_orders_frame, text="Delivery Fee:").grid(row=0, column=2)
    delivery_fee_entry = ttk.Entry(delivery_orders_frame, width=15)
    delivery_fee_entry.grid(row=0, column=3)

    def assign_delivery():
        emp_id = delivery_entries["Employee_ID"].get().strip()
        order_id = delivery_order_id_entry.get().strip()
        fee = delivery_fee_entry.get().strip()

        if not emp_id or not order_id or not fee:
            messagebox.showerror("Input Error", "All fields are required.")
            return

        try:
            fee = float(fee)
            cursor.execute("""
                INSERT INTO Delivery_Order (Order_ID, Delivery_fee, D_Employee_ID)
                VALUES (%s, %s, %s)
            """, (int(order_id), fee, int(emp_id)))

            cursor.execute("""
                UPDATE Orders SET Status='Out for Delivery'
                WHERE Order_ID=%s
            """, (int(order_id),))

            conn.commit()
            messagebox.showinfo("Success", "Delivery assigned successfully.")
            load_delivery_orders()
            delivery_order_id_entry.delete(0, tk.END)
            delivery_fee_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    ttk.Button(delivery_orders_frame, text="Assign Delivery", command=assign_delivery).grid(row=0, column=4, padx=5)

    # Delivery Orders Treeview
    delivery_orders_tree = ttk.Treeview(delivery_orders_frame,
                                        columns=("Order_ID", "Customer", "Delivery_Boy", "Fee", "Status"),
                                        show="headings")
    delivery_orders_tree.heading("Order_ID", text="Order ID")
    delivery_orders_tree.heading("Customer", text="Customer")
    delivery_orders_tree.heading("Delivery_Boy", text="Delivery Boy")
    delivery_orders_tree.heading("Fee", text="Fee")
    delivery_orders_tree.heading("Status", text="Status")
    delivery_orders_tree.grid(row=1, column=0, columnspan=5, pady=10, sticky='nsew')

    def load_delivery_orders():
        try:
            cursor.execute("""
                SELECT o.Order_ID, 
                       CONCAT(c.Customer_FirstName, ' ', c.Customer_LastName) AS Customer,
                       CONCAT(e.Employee_FirstName, ' ', e.Employee_LastName) AS Delivery_Boy,
                       do.Delivery_fee, o.Status
                FROM Orders o
                JOIN Customer c ON o.Customer_ID = c.Customer_ID
                JOIN Delivery_Order do ON o.Order_ID = do.Order_ID
                JOIN Employee e ON do.D_Employee_ID = e.Employee_ID
                WHERE o.Status IN ('Out for Delivery', 'Completed')
            """)
            orders = cursor.fetchall()
            delivery_orders_tree.delete(*delivery_orders_tree.get_children())
            for order in orders:
                delivery_orders_tree.insert("", "end", values=order)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def on_delivery_order_select(event):
        selected = delivery_orders_tree.focus()
        if selected:
            values = delivery_orders_tree.item(selected, "values")
            delivery_order_id_entry.delete(0, tk.END)
            delivery_order_id_entry.insert(0, values[0])

    delivery_orders_tree.bind("<<TreeviewSelect>>", on_delivery_order_select)

    # Complete Delivery Button
    def complete_delivery():
        order_id = delivery_order_id_entry.get().strip()
        if not order_id:
            messagebox.showerror("Input Error", "Please select an order first.")
            return

        try:
            cursor.execute("""
                UPDATE Orders SET Status='Completed'
                WHERE Order_ID=%s
            """, (int(order_id),))
            conn.commit()
            messagebox.showinfo("Success", "Delivery marked as completed.")
            load_delivery_orders()
            delivery_order_id_entry.delete(0, tk.END)
            delivery_fee_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    ttk.Button(delivery_orders_frame, text="Complete Delivery", command=complete_delivery).grid(row=2, column=0, columnspan=5, pady=5)

    # Initial load
    load_employees()
    load_delivery()
    load_delivery_orders()

    def on_tab_close():
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
        frame.destroy()

    frame.bind("<Destroy>", lambda e: on_tab_close())

def build_reports_tab(frame):
    conn = connect_db()
    if conn is None:
        return

    cursor = conn.cursor(dictionary=True)

    notebook = ttk.Notebook(frame)
    notebook.pack(fill='both', expand=True, padx=10, pady=10)

    # Sales Report Tab
    sales_tab = ttk.Frame(notebook)
    notebook.add(sales_tab, text="Sales Reports")

    # Employee Performance Tab
    performance_tab = ttk.Frame(notebook)
    notebook.add(performance_tab, text="Employee Performance")

    # ===== Sales Reports =====
    sales_frame = ttk.LabelFrame(sales_tab, text="Sales Reports", padding=10)
    sales_frame.pack(fill='both', expand=True, padx=10, pady=10)

    # Date range selection
    ttk.Label(sales_frame, text="From Date:").grid(row=0, column=0, padx=5, pady=5)
    from_date_entry = ttk.Entry(sales_frame)
    from_date_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(sales_frame, text="To Date:").grid(row=0, column=2, padx=5, pady=5)
    to_date_entry = ttk.Entry(sales_frame)
    to_date_entry.grid(row=0, column=3, padx=5, pady=5)

    # Report type selection
    ttk.Label(sales_frame, text="Report Type:").grid(row=1, column=0, padx=5, pady=5)
    report_type = ttk.Combobox(sales_frame, values=["Daily Sales", "Customer Spending", "Menu Item Popularity"])
    report_type.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky='ew')

    def generate_sales_report():
        try:
            from_date = from_date_entry.get()
            to_date = to_date_entry.get()
            report = report_type.get()

            if not from_date or not to_date or not report:
                messagebox.showerror("Input Error", "Please fill all fields")
                return

            if report == "Daily Sales":
                query = """
                    SELECT DATE(o.Order_Time) AS Date, 
                           SUM(p.Total_payment) AS Total_Sales,
                           COUNT(o.Order_ID) AS Order_Count
                    FROM Orders o
                    JOIN Payment p ON o.Order_ID = p.Order_ID
                    WHERE o.Order_Time BETWEEN %s AND %s
                    GROUP BY DATE(o.Order_Time)
                    ORDER BY Date
                """
                cursor.execute(query, (from_date, to_date))
            elif report == "Customer Spending":
                query = """
                    SELECT c.Customer_ID, 
                           CONCAT(c.Customer_FirstName, ' ', c.Customer_LastName) AS Customer,
                           COUNT(o.Order_ID) AS Order_Count,
                           SUM(p.Total_payment) AS Total_Spent
                    FROM Customer c
                    JOIN Orders o ON c.Customer_ID = o.Customer_ID
                    JOIN Payment p ON o.Order_ID = p.Order_ID
                    WHERE o.Order_Time BETWEEN %s AND %s
                    GROUP BY c.Customer_ID
                    ORDER BY Total_Spent DESC
                """
                cursor.execute(query, (from_date, to_date))
            elif report == "Menu Item Popularity":
                query = """
                    SELECT mi.Item_ID, mi.Name, 
                           COUNT(c.Order_ID) AS Times_Ordered,
                           SUM(mi.Price) AS Total_Revenue
                    FROM Menu_Item mi
                    JOIN contains c ON mi.Item_ID = c.Item_ID
                    JOIN Orders o ON c.Order_ID = o.Order_ID
                    WHERE o.Order_Time BETWEEN %s AND %s
                    GROUP BY mi.Item_ID
                    ORDER BY Times_Ordered DESC
                """
                cursor.execute(query, (from_date, to_date))

            results = cursor.fetchall()

            # Display results in new window
            result_window = tk.Toplevel()
            result_window.title(f"Report: {report}")

            if not results:
                ttk.Label(result_window, text="No data found for the selected criteria").pack()
                return

            # Create treeview
            tree = ttk.Treeview(result_window)
            tree["columns"] = list(results[0].keys())

            for col in tree["columns"]:
                tree.heading(col, text=col)
                tree.column(col, width=100)

            for row in results:
                tree.insert("", "end", values=list(row.values()))

            tree.pack(fill='both', expand=True)

            # Add export button
            def export_to_csv():
                import csv
                filename = f"{report.replace(' ', '_')}_{from_date}_to_{to_date}.csv"
                with open(filename, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(results[0].keys())
                    for row in results:
                        writer.writerow(row.values())
                messagebox.showinfo("Success", f"Report exported to {filename}")

            ttk.Button(result_window, text="Export to CSV", command=export_to_csv).pack()

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    ttk.Button(sales_frame, text="Generate Report", command=generate_sales_report).grid(row=2, column=0, columnspan=4, pady=10)

    # ===== Employee Performance =====
    performance_frame = ttk.LabelFrame(performance_tab, text="Employee Performance", padding=10)
    performance_frame.pack(fill='both', expand=True, padx=10, pady=10)

    # Employee type selection
    ttk.Label(performance_frame, text="Employee Type:").grid(row=0, column=0, padx=5, pady=5)
    emp_type = ttk.Combobox(performance_frame, values=["All", "Chef", "Waiter", "Delivery"])
    emp_type.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

    def generate_performance_report():
        try:
            emp_type_val = emp_type.get()

            if emp_type_val == "All":
                query = """
                    SELECT e.Employee_ID, 
                       CONCAT(e.Employee_FirstName, ' ', e.Employee_LastName) AS Employee,
                       e.Role,
                       CASE 
                           WHEN e.Role = 'Chef' THEN (
                               SELECT COUNT(*) FROM Orders o 
                               JOIN contains c ON o.Order_ID = c.Order_ID 
                               WHERE c.Item_ID IN (
                                   SELECT Item_ID FROM Menu_Item 
                                   WHERE Menu_ID = (
                                       SELECT Menu_ID FROM Restaurant 
                                       WHERE Restaurant_ID = o.Restaurant_ID
                                   )
                               )
                           )
                           WHEN e.Role = 'Waiter' THEN (
                               SELECT COUNT(*) FROM Orders 
                               WHERE Status = 'Completed' AND Order_Type = 'InDine'
                           )
                           WHEN e.Role = 'Delivery' THEN (
                               SELECT COUNT(*) FROM Delivery_Order 
                               WHERE D_Employee_ID = e.Employee_ID
                           )
                           ELSE 0
                       END AS Performance_Metric
                FROM Employee e
                ORDER BY Performance_Metric DESC
                """
            elif emp_type_val == "Chef":
                query = """
                    SELECT e.Employee_ID, 
                           CONCAT(e.Employee_FirstName, ' ', e.Employee_LastName) AS Employee,
                           COUNT(DISTINCT o.Order_ID) AS Orders_Prepared
                    FROM Employee e
                    JOIN Orders o ON e.Employee_ID = o.Restaurant_ID  -- Simplified for demo
                    WHERE e.Role = 'Chef'
                    GROUP BY e.Employee_ID
                    ORDER BY Orders_Prepared DESC
                """
            elif emp_type_val == "Waiter":
                query = """
                    SELECT e.Employee_ID, 
                           CONCAT(e.Employee_FirstName, ' ', e.Employee_LastName) AS Employee,
                           COUNT(o.Order_ID) AS Tables_Served
                    FROM Employee e
                    JOIN Orders o ON e.Employee_ID = o.Restaurant_ID  -- Simplified for demo
                    WHERE e.Role = 'Waiter' AND o.Order_Type = 'InDine'
                    GROUP BY e.Employee_ID
                    ORDER BY Tables_Served DESC
                """
            elif emp_type_val == "Delivery":
                query = """
                    SELECT e.Employee_ID, 
                           CONCAT(e.Employee_FirstName, ' ', e.Employee_LastName) AS Employee,
                           COUNT(do.Order_ID) AS Deliveries_Completed,
                           AVG(TIMESTAMPDIFF(MINUTE, o.Order_Time, ch.Date_Visited)) AS Avg_Delivery_Time_Mins
                    FROM Employee e
                    JOIN Delivery_Boy db ON e.Employee_ID = db.Employee_ID
                    JOIN Delivery_Order do ON db.Employee_ID = do.D_Employee_ID
                    JOIN Orders o ON do.Order_ID = o.Order_ID
                    JOIN Customer_History ch ON o.Order_ID = ch.Order_ID
                    WHERE o.Status = 'Completed'
                    GROUP BY e.Employee_ID
                    ORDER BY Deliveries_Completed DESC
                """

            cursor.execute(query)
            results = cursor.fetchall()

            # Display results in new window
            result_window = tk.Toplevel()
            result_window.title(f"Employee Performance: {emp_type_val}")

            if not results:
                ttk.Label(result_window, text="No data found").pack()
                return

            # Create treeview
            tree = ttk.Treeview(result_window)
            tree["columns"] = list(results[0].keys())

            for col in tree["columns"]:
                tree.heading(col, text=col)
                tree.column(col, width=100)

            for row in results:
                tree.insert("", "end", values=list(row.values()))

            tree.pack(fill='both', expand=True)

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    ttk.Button(performance_frame, text="Generate Report", command=generate_performance_report).grid(row=1, column=0, columnspan=2, pady=10)

    def on_tab_close():
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
        frame.destroy()

    frame.bind("<Destroy>", lambda e: on_tab_close())

if __name__ == "__main__":
    show_login()