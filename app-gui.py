import db_module
from Face_features import get_face_features
from Recogniser import main_app
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox,PhotoImage
nicknames_list = []
users_db=dict()
face_features=[]
nickname=""
user=""
class MainUI(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        global nicknames_list
        global users_db
        try:
            users_db=dict(db_module.get_users())
            #ключи словаря преобразовываются в список 
            nicknames_list=[*users_db] 
        except:
            ""
        self.title_font = tkfont.Font(family='Helvetica', size=16, weight="bold")
        self.title("Система биометрической аутентификации")
        self.resizable(False, False)
        self.geometry("500x250")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.active_name = None
        container = tk.Frame(self)
        container.grid(sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F in (StartPage, PageOne,  PageThree): 
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("StartPage")

    def show_frame(self, page_name):
            frame = self.frames[page_name]
            frame.tkraise()

    def on_closing(self):

        if messagebox.askokcancel("Закрыть", "Вы уверены?"):
            self.destroy()


class StartPage(tk.Frame):

        def __init__(self, parent, controller):
            tk.Frame.__init__(self, parent)
            self.controller = controller
            render = PhotoImage(file="imgs\\homepagepic.png")
            img = tk.Label(self, image=render)
            img.image = render
            img.grid(row=0, column=1, rowspan=4, sticky="nsew")
            label = tk.Label(self, text="        Главная страница        ", font=self.controller.title_font,fg="#263942")
            label.grid(row=0, sticky="ew")
            button1 = tk.Button(self, text="   Добавить пользователя  ", fg="#ffffff", bg="#263942",command=lambda: self.controller.show_frame("PageOne"))
            button2 = tk.Button(self, text="   Войти  ", fg="#ffffff", bg="#263942",command=self.authentification)
            button3 = tk.Button(self, text="Закрыть", fg="#263942", bg="#ffffff", command=self.on_closing)
            button1.grid(row=1, column=0, ipady=3, ipadx=7)
            button2.grid(row=2, column=0, ipady=3, ipadx=2)
            button3.grid(row=3, column=0, ipady=3, ipadx=32)

        
        def authentification(self):
            global users_db
            if len(nicknames_list)==0:
                messagebox.showinfo("", "Сначала нужно создать аккаунт.")
                self.controller.show_frame("PageOne")
            else:
                user=main_app(users_db)
                if not user==None:
                    messagebox.showinfo("", "Добро пожаловать, {}".format(user))
                else:
                    messagebox.showinfo("", "Попробуйте снова.")
                
        def on_closing(self):
            if messagebox.askokcancel("Закрыть", "Вы уверены?"):
                self.controller.destroy()


class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        tk.Label(self, text="Введите ник", fg="#263942", font='Helvetica 12 bold').grid(row=0, column=0, pady=10, padx=5)
        self.user_nickname = tk.Entry(self, borderwidth=3, bg="lightgrey", font='Helvetica 11')
        self.user_nickname.grid(row=0, column=1, pady=10, padx=10)
        self.buttoncanc = tk.Button(self, text="Отмена", bg="#ffffff", fg="#263942", command=lambda: controller.show_frame("StartPage"))
        self.buttonext = tk.Button(self, text="Дальше", fg="#ffffff", bg="#263942", command=self.create_account)
        self.buttoncanc.grid(row=1, column=0, pady=10, ipadx=5, ipady=4)
        self.buttonext.grid(row=1, column=1, pady=10, ipadx=5, ipady=4)
    def create_account(self):
        global nickname
        global nicknames_list
        nickname=self.user_nickname.get()
        if nickname == "None":
            messagebox.showerror("Error", "Ник не может быть пустым")
            return
        elif nickname in nicknames_list:
            messagebox.showerror("Error", "Такой пользователь существует!")
            return
        elif len(nickname) == 0:
            messagebox.showerror("Error", "Ник не может быть пустым!")
            return
        nicknames_list+=nickname
        self.controller.active_name = nickname
        nicknames_list.append(nickname)
        self.controller.show_frame("PageThree")


class PageThree(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.numimglabel = tk.Label(self, text="", font='Helvetica 12 bold', fg="#263942")
        self.numimglabel.grid(row=0, column=0, columnspan=2, sticky="ew", pady=10)
        self.capturebutton = tk.Button(self, text="Добавить данные лица", fg="#ffffff", bg="#263942", command=self.capimg)
        self.savebutton = tk.Button(self, text="Сохранить", fg="#ffffff", bg="#263942",command=self.save_profile)
        self.capturebutton.grid(row=1, column=0, ipadx=5, ipady=4, padx=10, pady=20)
        self.savebutton.grid(row=1, column=1, ipadx=5, ipady=4, padx=10, pady=20)

    def capimg(self):
        messagebox.showinfo("", "Сделать снимок?")
        global face_features
        face_features = get_face_features(self.controller.active_name)

    def save_profile(self):
        global face_features
        global users_db
        if len(face_features)==0:
            messagebox.showerror("Ошибка", "Не добавлены даные лица")
            return
        global nickname
        db_module.create_profile(nickname,face_features)
        users_db[nickname]=face_features
        messagebox.showinfo("", "Профиль был успешно создан")
        self.controller.show_frame("StartPage")




app = MainUI() 
app.iconphoto(False, tk.PhotoImage(file="icon.ico"))
app.mainloop()

