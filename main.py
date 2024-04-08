from flet import app, SnackBar, PopupMenuItem, PopupMenuButton, ListTile, Text, AlertDialog, ElevatedButton, TextThemeStyle, Page, Checkbox, AppView, ScrollMode, OutlinedButton, FloatingActionButton, Row, Text, Tab, Tabs, TextField, UserControl, Column, icons, colors, IconButton, CrossAxisAlignment, MainAxisAlignment
import requests
import json


class Task(UserControl):
    def __init__(self, task_name, task_status_change, task_delete):
        super().__init__()
        self.completed = False
        self.task_name = task_name
        self.task_status_change = task_status_change
        self.task_delete = task_delete

    def build(self):
        self.display_task = Checkbox(
            value=False, label=self.task_name, on_change=self.status_changed
        )
        self.edit_name = TextField(expand=1)
        self.display_view = Row(
            alignment=MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=CrossAxisAlignment.CENTER,
            controls=[
                self.display_task,
                Row(
                    spacing=0,
                    controls=[
                        IconButton(
                            icon=icons.CREATE_OUTLINED,
                            tooltip="ویرایش",
                            on_click=self.edit_clicked,
                        ),
                        IconButton(
                            icons.DELETE_OUTLINE,
                            tooltip="حذف",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )
        self.edit_view = Row(
            visible=False,
            alignment=MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=CrossAxisAlignment.CENTER,
            controls=[
                self.edit_name,
                IconButton(
                    icon=icons.DONE_OUTLINE_OUTLINED,
                    icon_color=colors.GREEN,
                    tooltip="اعمال",
                    on_click=self.save_clicked,
                ),
            ],
        )
        return Column(controls=[self.display_view, self.edit_view])

    async def edit_clicked(self, e):
        self.edit_name.value = self.display_task.label
        self.display_view.visible = False
        self.edit_view.visible = True
        await self.update_async()

    async def save_clicked(self, e):
        self.display_task.label = self.edit_name.value
        self.display_view.visible = True
        self.edit_view.visible = False
        await self.update_async()

    async def status_changed(self, e):
        self.completed = self.display_task.value
        await self.task_status_change(self)

    async def delete_clicked(self, e):
        await self.task_delete(self)


class TodoApp(UserControl):

    def sync(acss_token):
        global token
        token = acss_token
        # respons = requests.get("https://todoyar.liara.run/todo/", headers={
        #     'Authorization': f'Bearer {acss_token}'
        # }, data='')
        # tasks_list = respons.json()
        # print(tasks_list)

        # for i in tasks_list:
        #     # print(i.get("title"))
        #     print(i)

    def build(self):
        self.new_task = TextField(
            hint_text="قراره چکار انجام بدی",
            on_submit=self.add_clicked,
            expand=True,
            text_align="RIGHT"
        )
        self.tasks = Column()
        self.filter = Tabs(
            scrollable=False,
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[Tab(text="همه"), Tab(text="فعال"),
                  Tab(text="تکمیل شده")],
        )
        self.items_left = Text(
            "همه تکمیل شد", text_align="RIGHT")

        return Column(
            width=1000,
            controls=[
                Row(
                    controls=[
                        PopupMenuButton(
                            icon=icons.ACCOUNT_CIRCLE,
                            items=[
                                PopupMenuItem(
                                    text="خروج از حساب", icon=icons.EXIT_TO_APP),
                                PopupMenuItem(
                                    text="تغییر پسورد", icon=icons.PASSWORD_OUTLINED),
                                PopupMenuItem(
                                    text="حذف حساب کاربری", icon=icons.DELETE),
                            ],
                        )
                    ]
                ),
                Row(
                    controls=[
                        self.new_task,
                        FloatingActionButton(
                            icon=icons.ADD, on_click=self.add_clicked
                        ),
                    ],
                ),
                Column(
                    spacing=25,
                    controls=[
                        self.filter,
                        self.tasks,
                        Row(
                            alignment=MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=CrossAxisAlignment.CENTER,
                            controls=[
                                self.items_left,
                                OutlinedButton(
                                    text="حذف تکمیل شده ها", on_click=self.clear_clicked
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )

    async def add_clicked(self, e):
        if self.new_task.value:
            # else:

            respons = requests.get("https://todoyar.liara.run/todo/", headers={
                'Authorization': f'Bearer {token}'
            }, data='')
            tasks_list = respons.json()
            self.tasks.controls.clear()
            await self.update_async()
            for i in tasks_list:
                task = Task(i.get("title"),
                            self.task_status_change, self.task_delete)
                self.tasks.controls.append(task)
                await self.new_task.focus_async()
                await self.update_async()

            task = Task(self.new_task.value,
                        self.task_status_change, self.task_delete)
            self.tasks.controls.append(task)

            response = requests.post("https://todoyar.liara.run/todo/", headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }, data=json.dumps({
                "title": self.new_task.value,
                "tik": "False"
            }))
            # print(respons.text)

            self.new_task.value = ""
            await self.new_task.focus_async()
            await self.update_async()

    async def task_status_change(self, task):
        await self.update_async()

    async def task_delete(self, task):
        self.tasks.controls.remove(task)
        await self.update_async()

    async def tabs_changed(self, e):
        await self.update_async()

    async def clear_clicked(self, e):
        for task in self.tasks.controls[:]:
            if task.completed:
                await self.task_delete(task)

    async def update_async(self):
        status = self.filter.tabs[self.filter.selected_index].text
        count = 0
        for task in self.tasks.controls:
            task.visible = (
                status == "همه"
                or (status == "فعال" and task.completed == False)
                or (status == "تکمیل شده" and task.completed)
            )
            if not task.completed:
                count += 1
        self.items_levalue = f"{count} تعداد کارهای ناتمام :"
        await super().update_async()


async def main(page: Page):
    page.title = "تودویار | Todoyar"
    page.horizontal_alignment = CrossAxisAlignment.CENTER
    page.scroll = ScrollMode.ADAPTIVE

    async def login(e):
        login_usern = dlg_modal.content.tabs[0].content.controls[1].value
        passw = dlg_modal.content.tabs[0].content.controls[2].value
        if login_usern and passw != '':
            response = requests.post("https://todoyar.liara.run/login/", headers={
                'Content-Type': 'application/json'},
                data=json.dumps({
                    "username": login_usern,
                    "password": passw
                }))
            if response:
                page.snack_bar.content = Text(
                    "خوش آمدید. برای همگام سازی، شروع به اضافه کردن تسک جدید کنید")
                page.snack_bar.open = True
                refresh_token = response.json().get('refresh')
                access_token = response.json().get('access')
                print(refresh_token, access_token)
                TodoApp.sync(access_token)

                dlg_modal.open = False
            else:
                page.snack_bar.content = Text("مشکلی در ورود وجود دارد")
                page.snack_bar.open = True
        else:
            page.snack_bar.content = Text("پر کردن فیلد ها ضروری است")
            page.snack_bar.open = True
        await page.update_async()

    async def register(e):
        username = dlg_modal.content.tabs[1].content.controls[1].value
        pass1 = dlg_modal.content.tabs[1].content.controls[2].value
        pass2 = dlg_modal.content.tabs[1].content.controls[3].value
        if pass1 == pass2 and pass1 != '' and username != '':

            response = requests.post("https://todoyar.liara.run/register/", data={
                "username": str(username), "password": str(pass1)})

            if response:
                print(response.text)
                print(username)
                dlg_modal.content.tabs[0].content.controls[1].value = username
                dlg_modal.content.tabs[0].content.controls[2].value = pass1
                username = dlg_modal.content.tabs[1].content.controls[3].value = ''
                pass2 = dlg_modal.content.tabs[1].content.controls[3].value = ''
                pass2 = dlg_modal.content.tabs[1].content.controls[2].value = ''

                page.snack_bar.content = Text(
                    "اکانت شما ساخته شد. حالا وارد شوید")
                page.snack_bar.open = True
                # page.update()

            else:
                page.snack_bar.content = Text("مشکل در ارتباط با سرور")
                page.snack_bar.open = True

        elif pass1 != pass2 or username == '' or pass1 == '' or pass2 == '':
            pass2 = dlg_modal.content.tabs[1].content.controls[3].value = ''
            pass2 = dlg_modal.content.tabs[1].content.controls[2].value = ''
            page.snack_bar.content = Text("پر کردن فیلد ها ضروری است")
            page.snack_bar.open = True

        # اگر مقدار تب که الان برابر 1 هست برابر 0 بشه میره توی لاگین و مقدار اونارو میاره
        # dlg_modal.open = False
        await page.update_async()

    page.snack_bar = SnackBar(
        content=Text("خطایی وجود دارد/رخ داده است"),
    )

    dlg_modal = AlertDialog(
        actions_alignment=MainAxisAlignment.END,
        modal=True,
        content=Tabs(
            scrollable=False,
            selected_index=0,
            width=800,
            height=415,
            animation_duration=300,
            tabs=[
                Tab(
                    text="Login",
                    icon=icons.LOGIN,
                    content=Column(
                        controls=[
                            Text(size=30),
                            TextField(
                                label="Username",
                                icon=icons.PERSON,
                                color="blue",
                                height=100,
                                text_align="Left",
                                max_length=20,

                            ),
                            TextField(label="Password",
                                      icon=icons.PASSWORD,
                                      password=True,
                                      color="blue",
                                      height=90,
                                      text_align="Left",
                                      can_reveal_password=True,


                                      ),
                            Text(size=50),
                            ElevatedButton(text="Lets go",
                                           icon=icons.LOGIN,
                                           scale=1,
                                           left="right",
                                           on_click=login,

                                           ),
                        ],
                        spacing=5
                    )
                ),

                Tab(
                    text="Register",
                    icon=icons.ASSIGNMENT,
                    content=Column(
                        controls=[
                            Text(size=30),
                            TextField(
                                label="نام کاربری",
                                icon=icons.ACCOUNT_CIRCLE,
                                color="blue",
                                height=90,
                                text_align="Left",
                                max_length=20,
                            ),
                            TextField(label="رمز عبور",
                                      icon=icons.PASSWORD,
                                      password=True,
                                      color="blue",
                                      height=90,
                                      text_align="Left",
                                      can_reveal_password=True,
                                      ),
                            TextField(label="تکرار رمز عبور",
                                      icon=icons.PASSWORD,
                                      password=True,
                                      color="blue",
                                      height=90,
                                      text_align="Left",
                                      can_reveal_password=True,
                                      ),
                            ElevatedButton(text="ثبت نام",
                                           icon=icons.LOGIN,
                                           scale=1,
                                           left="right",
                                           on_click=register,
                                           ),
                        ],
                        spacing=5,
                    ),
                ),
            ],
        ),
    )

    def open_dlg_modal(e):
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()
    page.dialog = dlg_modal
    dlg_modal.open = True
    await page.add_async(TodoApp())
#app(main)
app(target=main, view=AppView.WEB_BROWSER, assets_dir="assets")
