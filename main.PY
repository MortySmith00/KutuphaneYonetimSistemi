import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
loan_date = datetime.now().strftime("%Y-%m-%d")


# Veritabanı bağlantısı ve veri alma fonksiyonu
def get_data(query):
    conn = sqlite3.connect('lib.db')
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    return data

# Kullanıcı ekleme fonksiyonu
def insert_user(first_name, last_name, email, phone, window):
    if not first_name or not last_name or not email:
        messagebox.showerror("Hata", "Ad, soyad ve e-posta alanları zorunludur.")
        return
    try:
        conn = sqlite3.connect('lib.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (first_name, last_name, email, phone) VALUES (?, ?, ?, ?)",
                       (first_name, last_name, email, phone))
        conn.commit()
        messagebox.showinfo("Başarılı", "Kullanıcı başarıyla eklendi!")
        window.destroy()
    except sqlite3.Error as e:
        messagebox.showerror("Hata", f"Kullanıcı eklenirken hata oluştu: {e}")
    finally:
        conn.close()

# Kitap ekleme fonksiyonu
def insert_book(title, author, publisher, isbn, total_copies, available_copies, window):
    if not title or not author or not isbn or not total_copies or not available_copies:
        messagebox.showerror("Hata", "Tüm alanlar zorunludur.")
        return
    try:
        conn = sqlite3.connect('lib.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO books (title, author, publisher, isbn, total_copies, available_copies) VALUES (?, ?, ?, ?, ?, ?)",
                       (title, author, publisher, isbn, total_copies, available_copies))
        conn.commit()
        messagebox.showinfo("Başarılı", "Kitap başarıyla eklendi!")
        window.destroy()
    except sqlite3.Error as e:
        messagebox.showerror("Hata", f"Kitap eklenirken hata oluştu: {e}")
    finally:
        conn.close()

def show_users():
    for row in user_tree.get_children():
        user_tree.delete(row)
    query = "SELECT user_id, first_name, last_name, email, phone, membership_date FROM users"
    users = get_data(query)
    for user in users:
        user_tree.insert("", "end", values=user)

def show_books():
    for row in book_tree.get_children():
        book_tree.delete(row)
    query = "SELECT book_id, title, author, publisher, isbn, total_copies, available_copies FROM books"
    books = get_data(query)
    for book in books:
        book_tree.insert("", "end", values=book)

def open_loan_window():
    loan_window = tk.Toplevel(root)
    loan_window.title("Kitap Kirala")
    loan_window.geometry("400x400")

    tk.Label(loan_window, text="Kiralayacak Kişi:", font=("Arial", 12)).pack(pady=5)
    user_combobox = ttk.Combobox(loan_window, values=[f"{user[0]} - {user[1]} {user[2]}" for user in get_data("SELECT user_id, first_name, last_name FROM users")], font=("Arial", 12))
    user_combobox.pack(pady=5)

    tk.Label(loan_window, text="Kiralayacak Kitap:", font=("Arial", 12)).pack(pady=5)
    book_combobox = ttk.Combobox(loan_window, values=[f"{book[0]} - {book[1]}" for book in get_data("SELECT book_id, title FROM books")], font=("Arial", 12))
    book_combobox.pack(pady=5)

    def loan_book():
     selected_user = user_combobox.get().split(" - ")[0]
     selected_book = book_combobox.get().split(" - ")[0]
     loan_date = datetime.now().strftime("%Y-%m-%d") 
     return_date = None  
     status = 0
     try:
        conn = sqlite3.connect('lib.db')
        cursor = conn.cursor()
        cursor.execute("SELECT available_copies FROM books WHERE book_id = ?", (selected_book,))
        available_copies = cursor.fetchone()[0]

        if available_copies <= 0:
            messagebox.showerror("Hata", "Bu kitap mevcut değil.")
            return

        # Kiralama işlemi
        cursor.execute("INSERT INTO loans (user_id, book_id, loan_date, return_date, status) VALUES (?, ?, ?, ?, ?)",
                       (selected_user, selected_book, loan_date, return_date, status))
        cursor.execute("UPDATE books SET available_copies = available_copies - 1 WHERE book_id = ?", (selected_book,))
        
        conn.commit()
        messagebox.showinfo("Başarılı", "Kitap başarıyla kiralandı!")
        loan_window.destroy() 
     except sqlite3.Error as e:
        messagebox.showerror("Hata", f"Kiralama sırasında hata oluştu: {e}")
     finally:
        conn.close()

    btn_loan_book = tk.Button(loan_window, text="Kitap Kirala", command=loan_book, bg="#28A745", fg="white", font=("Arial", 12))
    btn_loan_book.pack(pady=10)

# Kullanıcı ekleme arayüzü
def open_add_user_window():
    add_user_window = tk.Toplevel(root)
    add_user_window.title("Yeni Kullanıcı Ekle")
    add_user_window.geometry("300x350")

    tk.Label(add_user_window, text="Ad:", font=("Arial", 12)).pack(pady=5)
    entry_first_name = tk.Entry(add_user_window, font=("Arial", 12))
    entry_first_name.pack(pady=5)

    tk.Label(add_user_window, text="Soyad:", font=("Arial", 12)).pack(pady=5)
    entry_last_name = tk.Entry(add_user_window, font=("Arial", 12))
    entry_last_name.pack(pady=5)

    tk.Label(add_user_window, text="E-posta:", font=("Arial", 12)).pack(pady=5)
    entry_email = tk.Entry(add_user_window, font=("Arial", 12))
    entry_email.pack(pady=5)

    tk.Label(add_user_window, text="Telefon:", font=("Arial", 12)).pack(pady=5)
    entry_phone = tk.Entry(add_user_window, font=("Arial", 12))
    entry_phone.pack(pady=5)

    btn_add_user = tk.Button(add_user_window, text="Kullanıcı Ekle", command=lambda: insert_user(
        entry_first_name.get(), 
        entry_last_name.get(), 
        entry_email.get(), 
        entry_phone.get(),
        add_user_window 
    ), bg="#28A745", fg="white", font=("Arial", 12))
    btn_add_user.pack(pady=10)

def open_return_book_window():
    return_window = tk.Toplevel(root)
    return_window.title("Kitap İade Et")
    return_window.geometry("400x300")

    # İade edilecek kitaplar için seçim
    tk.Label(return_window, text="İade Edilecek Kitap:", font=("Arial", 12)).pack(pady=5)
    loan_combobox = ttk.Combobox(return_window, values=[
        f"{loan[0]} - {loan[1]} (Kitap: {loan[2]})" for loan in get_data(
            "SELECT l.loan_id, u.first_name || ' ' || u.last_name AS user_name, b.title AS book_title "
            "FROM loans l "
            "JOIN users u ON l.user_id = u.user_id "
            "JOIN books b ON l.book_id = b.book_id WHERE l.status = 0"
        )
    ], font=("Arial", 12))
    loan_combobox.pack(pady=5)

    def return_book():
     selected_loan = loan_combobox.get().split(" - ")[0] 

     if not selected_loan:
        messagebox.showerror("Hata", "İade edilecek kitap seçilmedi.")
        return

     return_date = datetime.now().strftime("%Y-%m-%d")

     try:
        conn = sqlite3.connect('lib.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE loans SET return_date = ?, status = 1 WHERE loan_id = ?", (return_date, selected_loan))
        cursor.execute("UPDATE books SET available_copies = available_copies + 1 WHERE book_id = (SELECT book_id FROM loans WHERE loan_id = ?)", (selected_loan,))
        conn.commit()
        messagebox.showinfo("Başarılı", "Kitap başarıyla iade edildi!")
        return_window.destroy()
     except sqlite3.Error as e:
        messagebox.showerror("Hata", f"İade sırasında hata oluştu: {e}")
     finally:
        conn.close()

    btn_return_book = tk.Button(return_window, text="Kitabı İade Et", command=return_book, bg="#28A745", fg="white", font=("Arial", 12))
    btn_return_book.pack(pady=10)

    
# Kitap ekleme arayüzü
def open_add_book_window():
    add_book_window = tk.Toplevel(root)
    add_book_window.title("Yeni Kitap Ekle")
    add_book_window.geometry("300x500")

    tk.Label(add_book_window, text="Kitap Adı:", font=("Arial", 12)).pack(pady=5)
    entry_title = tk.Entry(add_book_window, font=("Arial", 12))
    entry_title.pack(pady=5)

    tk.Label(add_book_window, text="Yazar:", font=("Arial", 12)).pack(pady=5)
    entry_author = tk.Entry(add_book_window, font=("Arial", 12))
    entry_author.pack(pady=5)

    tk.Label(add_book_window, text="Yayın Evi:", font=("Arial", 12)).pack(pady=5)
    entry_publisher = tk.Entry(add_book_window, font=("Arial", 12))
    entry_publisher.pack(pady=5)

    tk.Label(add_book_window, text="ISBN:", font=("Arial", 12)).pack(pady=5)
    entry_isbn = tk.Entry(add_book_window, font=("Arial", 12))
    entry_isbn.pack(pady=5)

    tk.Label(add_book_window, text="Toplam Kopya Sayısı:", font=("Arial", 12)).pack(pady=5)
    entry_total_copies = tk.Entry(add_book_window, font=("Arial", 12))
    entry_total_copies.pack(pady=5)

    tk.Label(add_book_window, text="Mevcut Kopya Sayısı:", font=("Arial", 12)).pack(pady=5)
    entry_available_copies = tk.Entry(add_book_window, font=("Arial", 12))
    entry_available_copies.pack(pady=5)

    btn_add_book = tk.Button(add_book_window, text="Kitap Ekle", command=lambda: insert_book(
        entry_title.get(), 
        entry_author.get(), 
        entry_publisher.get(), 
        entry_isbn.get(), 
        entry_total_copies.get(), 
        entry_available_copies.get(),
        add_book_window
    ), bg="#28A745", fg="white", font=("Arial", 12))
    btn_add_book.pack(pady=10)

# Kiralanan kitaplar görüntüle
def show_loans():
    for row in loan_tree.get_children():
        loan_tree.delete(row)

    query = """SELECT l.loan_id, u.first_name || ' ' || u.last_name AS user_name, b.title AS book_title, 
                      l.loan_date, l.return_date, l.status 
               FROM loans l 
               JOIN users u ON l.user_id = u.user_id 
               JOIN books b ON l.book_id = b.book_id"""
    
    loans = get_data(query)
    
    for loan in loans:
        loan_status = "İade Edilmiş" if loan[-1] == 1 else "Kitap Kiralanmış"
        loan_with_status = (loan[0], loan[1], loan[2], loan[3], loan[4], loan_status)
        loan_tree.insert("", "end", values=loan_with_status)


# Arayüz
root = tk.Tk()
root.title("Kütüphane Sistemi")
root.geometry("1400x600")

# Kullanıcılar için Treeview oluştur
user_tree = ttk.Treeview(root, columns=("user_id", "Ad", "Soyad", "E-posta", "Telefon", "Üyelik Tarihi"), show="headings")
user_tree.heading("user_id", text="Kullanıcı ID")
user_tree.heading("Ad", text="Ad")
user_tree.heading("Soyad", text="Soyad")
user_tree.heading("E-posta", text="E-posta")
user_tree.heading("Telefon", text="Telefon")
user_tree.heading("Üyelik Tarihi", text="Üyelik Tarihi")
user_tree.pack(pady=20)

# Kitaplar için Treeview oluştur
book_tree = ttk.Treeview(root, columns=("book_id", "Kitap Adı", "Yazar", "Yayın Evi", "ISBN", "Toplam Kopya", "Mevcut Kopya"), show="headings")
book_tree.heading("book_id", text="Kitap ID")
book_tree.heading("Kitap Adı", text="Kitap Adı")
book_tree.heading("Yazar", text="Yazar")
book_tree.heading("Yayın Evi", text="Yayın Evi")
book_tree.heading("ISBN", text="ISBN")
book_tree.heading("Toplam Kopya", text="Toplam Kopya Sayısı")
book_tree.heading("Mevcut Kopya", text="Mevcut Kopya Sayısı")
book_tree.pack(pady=20)

# Kiralanan kitaplar için Treeview oluştur
loan_tree = ttk.Treeview(root, columns=("loan_id", "Kullanıcı ID", "Kitap ID", "Kiralama Tarihi", "İade Tarihi", "Durum"), show="headings")
loan_tree.heading("loan_id", text="Kiralama ID")
loan_tree.heading("Kullanıcı ID", text="Kullanıcı İsmi")
loan_tree.heading("Kitap ID", text="Kitap İsmi")
loan_tree.heading("Kiralama Tarihi", text="Kiralama Tarihi")
loan_tree.heading("İade Tarihi", text="İade Tarihi")
loan_tree.heading("Durum", text="Durum")
loan_tree.pack(pady=20)

# Üç Treeview'i de gizle
user_tree.pack_forget()
book_tree.pack_forget()
loan_tree.pack_forget()

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

btn_users = tk.Button(button_frame, text="Kullanıcıları Göster", command=lambda: (user_tree.pack(fill=tk.BOTH, expand=True), book_tree.pack_forget(), loan_tree.pack_forget(), show_users()), bg="#007ACC", fg="white", font=("Arial", 12))
btn_users.pack(side=tk.LEFT, padx=5)

btn_books = tk.Button(button_frame, text="Kitapları Göster", command=lambda: (book_tree.pack(fill=tk.BOTH, expand=True), user_tree.pack_forget(), loan_tree.pack_forget(), show_books()), bg="#007ACC", fg="white", font=("Arial", 12))
btn_books.pack(side=tk.LEFT, padx=5)

btn_loans = tk.Button(button_frame, text="Kiralanan Kitaplar", command=lambda: (loan_tree.pack(fill=tk.BOTH, expand=True), user_tree.pack_forget(), book_tree.pack_forget(), show_loans()), bg="#007ACC", fg="white", font=("Arial", 12))
btn_loans.pack(side=tk.LEFT, padx=5)

btn_add_user = tk.Button(button_frame, text="Kullanıcı Ekle", command=open_add_user_window, bg="#28A745", fg="white", font=("Arial", 12))
btn_add_user.pack(side=tk.LEFT, padx=5)

btn_add_book = tk.Button(button_frame, text="Kitap Ekle", command=open_add_book_window, bg="#28A745", fg="white", font=("Arial", 12))
btn_add_book.pack(side=tk.LEFT, padx=5)

btn_loan_book = tk.Button(button_frame, text="Kitap Kirala", command=open_loan_window, bg="#28A745", fg="white", font=("Arial", 12))
btn_loan_book.pack(side=tk.LEFT, padx=5)

btn_return_book = tk.Button(button_frame, text="Kitap İade Et", command=open_return_book_window, bg="#28A745", fg="white", font=("Arial", 12))
btn_return_book.pack(side=tk.LEFT, padx=5)

root.mainloop()
