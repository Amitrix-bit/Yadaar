from flet import Container, BottomSheet, AppView, app, SnackBar, PopupMenuItem, PopupMenuButton, Text, AlertDialog, ElevatedButton, Page, Checkbox, ScrollMode, OutlinedButton, FloatingActionButton, Row, Text, Tab, Tabs, TextField, UserControl, Column, icons, colors, IconButton, CrossAxisAlignment, MainAxisAlignment
import requests
import json


class Task(UserControl):
    def __init__(self, task_name, task_status_change, task_delete, task_id, completed):
        super().__init__()
        self.completed = completed
        self.task_name = task_name
        self.task_status_change = task_status_change
        self.task_delete = task_delete
        self.task_id = task_id

    def build(self):
        self.display_task = Checkbox(
            value=self.completed, label=self.task_name, on_change=self.status_changed, label_position='LEFT'
        )
        self.edit_name = TextField(expand=1)
        self.display_view = Row(
            alignment=MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=CrossAxisAlignment.CENTER,
            controls=[
                Row(
                    spacing=0,
                    controls=[
                        IconButton(
                            icon=icons.CREATE_OUTLINED,
                            tooltip="ویرایش",
                            on_click=self.edit_clicked,
                            icon_color="green"
                        ),
                        IconButton(
                            icons.DELETE_OUTLINE,
                            tooltip="حذف",
                            on_click=self.delete_clicked,
                            icon_color="red"
                        ),
                    ],
                ),
                self.display_task,
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

        response = requests.put(f"https://todoyar.liara.run/todo/{self.task_id}/", headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }, data=json.dumps({
            "title": self.display_task.label
        }))

        self.display_view.visible = True
        self.edit_view.visible = False
        await self.update_async()

    async def status_changed(self, e):
        self.completed = self.display_task.value
        await self.task_status_change(self, task_id=self.task_id, tik=self.completed)

    async def delete_clicked(self, e):
        await self.task_delete(self, id=self.task_id)


class TodoApp(UserControl):

    def sync(acss_token, refresh_token):

        global token
        token = acss_token
        global rfresh_token
        rfresh_token = refresh_token

        responsef = requests.post("https://todoyar.liara.run/todo/", headers={
            'Authorization': f'Bearer {token}'
        })
        if str(responsef) == "<Response [401]>":
            response = requests.post("https://todoyar.liara.run/login/refresh/", headers={
                'Content-Type': 'application/json'
            }, data=json.dumps({
                "refresh": rfresh_token
            }))
            TodoApp.sync(response.json().get("access"), rfresh_token)

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
            tabs=[Tab(text="همه"), Tab(text="تکمیل نشده"),
                  Tab(text="تکمیل شده")],
        )
        self.items_left = Text(
            "خبری نیست", text_align="RIGHT")

        return Column(
            width=1000,
            controls=[
                Row(
                    controls=[
                        PopupMenuButton(
                            icon=icons.ACCOUNT_CIRCLE,
                            items=[
                                PopupMenuItem(
                                    text="همگام سازی مجدد", icon=icons.CLOUD_SYNC, on_click=self.add_clicked),
                                PopupMenuItem(
                                    text="خروج از حساب کاربری", icon=icons.EXIT_TO_APP, on_click=self.forget_user),
                                # PopupMenuItem(
                                #     text="تغییر پسورد", icon=icons.PASSWORD_OUTLINED, on_click=self.delete_account),
                                PopupMenuItem(
                                    text="حذف حساب کاربری", icon=icons.DELETE, on_click=self.delete_account),
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

    async def forget_user(self, e):
        await self.page.client_storage.clear_async()
        self.page.dialog.open = True
        await self.page.update_async()

    async def delete_account(self, e):
        self.page.bottom_sheet.open = True
        await self.page.update_async()

    async def bs_yes(self):
        requests.delete("https://todoyar.liara.run/account/delete/", headers={
            'Authorization': f'Bearer {token}'
        })
        await self.page.client_storage.clear_async()
        self.page.dialog.open = True
        await self.page.update_async()
        self.page.bottom_sheet.open = False

    async def bs_no(self):
        self.page.bottom_sheet.open = False

    async def add_clicked(self, e):
        # ایده ای هست که میتونی مستقیما از کلاس تسک این کارارو انجام بدی منظورم گرفتن و فرستادن ای پی آی هست
        if self.new_task.value:
            # else:
            requests.post("https://todoyar.liara.run/todo/", headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }, data=json.dumps({
                "title": self.new_task.value,
                "tik": "False"
            }))

        respons = requests.get("https://todoyar.liara.run/todo/", headers={
            'Authorization': f'Bearer {token}'
        }, data='')

        tasks_list = respons.json()
        self.tasks.controls.clear()
        for i in tasks_list:
            task = Task(i.get("title"),
                        self.task_status_change, self.task_delete, i.get("id"), completed=i.get('tik'))
            self.tasks.controls.append(task)
            # await self.new_task.focus_async()
            # await self.update_async()
        self.new_task.value = ""
        await self.new_task.focus_async()
        await self.update_async()

    async def task_status_change(self, task, task_id='', tik=''):
        if task_id != '':
            requests.put(f"https://todoyar.liara.run/todo/{task_id}/", headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }, data=json.dumps({
                "tik": tik
            }))
        await self.update_async()

    async def task_id(self, e):
        await self.update_async()

    async def task_delete(self, task, id=''):
        self.tasks.controls.remove(task)
        await self.update_async()
        if id != '':
            requests.delete(f"https://todoyar.liara.run/todo/{id}/", headers={
                'Authorization': f'Bearer {token}'
            })

    async def tabs_changed(self, e):
        await self.update_async()

    async def clear_clicked(self, e):
        for task in self.tasks.controls[:]:
            if task.completed:
                requests.delete(f"https://todoyar.liara.run/todo/{task.task_id}/", headers={
                    'Authorization': f'Bearer {token}'
                })
                await self.task_delete(task)

    async def update_async(self):
        status = self.filter.tabs[self.filter.selected_index].text
        count = 0
        for task in self.tasks.controls:
            task.visible = (
                status == "همه"
                or (status == "تکمیل نشده" and task.completed == False)
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
            if len(passw) < 8 or len(login_usern) < 5:
                page.snack_bar.content = Text(
                    "حداقل کاراکتر برای نام کاربری 5 حرف و برای پسورد 8 حرف است")
                page.snack_bar.open = True
            else:
                response = requests.post("https://todoyar.liara.run/account/login/", headers={
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

                    await page.client_storage.set_async("access_token", access_token)
                    await page.client_storage.set_async("refresh_token", refresh_token)
                    # print(refresh_token, access_token)
                    TodoApp.sync(access_token, refresh_token)
                    dlg_modal.open = False

                else:
                    page.snack_bar.content = Text("مشکلی در ورود وجود دارد")
                    page.snack_bar.open = True
        else:
            page.snack_bar.content = Text("پر کردن فیلد ها ضروری است")
            page.snack_bar.open = True
        await page.update_async()
    bs = BottomSheet(
        Container(
            Column(
                [
                    Text("""آیا از حذف حساب کاربری خود اطمینان دارید؟
                            این عمل قابل بازگشت نخواهد بود
                            تمامی یادداشت های شما از بین خواهند رفت""", text_align="RIGHT"),

                    Row(
                        [
                            ElevatedButton("بله", color="red",
                                           on_click=TodoApp.bs_yes),
                            ElevatedButton("خیر", on_click=TodoApp.bs_no),
                        ],
                    ),
                ],





                tight=True,
            ),
            padding=10,
        ),
    )

    async def register(e):
        username = dlg_modal.content.tabs[1].content.controls[1].value
        pass1 = dlg_modal.content.tabs[1].content.controls[2].value
        pass2 = dlg_modal.content.tabs[1].content.controls[3].value
        if pass1 == pass2 and pass1 != '' and username != '':
            if len(pass1) < 8 or len(username) < 5:
                page.snack_bar.content = Text(
                    "حداقل کاراکتر برای نام کاربری 5 حرف و برای پسورد 8 حرف است")
                page.snack_bar.open = True
            else:

                response = requests.post("https://todoyar.liara.run/account/register/", data={
                    "username": str(username), "password": str(pass1)})

                if response:
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
            page.snack_bar.content = Text("پر کردن صحیح فیلد ها ضروری است")
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
                    text="ورود",
                    icon=icons.LOGIN,
                    content=Column(
                        controls=[
                            Text(size=30),
                            TextField(
                                label="نام کاربری",
                                icon=icons.PERSON,
                                color="blue",
                                height=100,
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
                                      max_length=20,

                                      ),
                            Text(size=50),
                            ElevatedButton(text="بزن بریم",
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
                    text="عضویت",
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
                                      max_length=20,
                                      ),
                            TextField(label="تکرار رمز عبور",
                                      icon=icons.PASSWORD,
                                      password=True,
                                      color="blue",
                                      height=90,
                                      text_align="Left",
                                      can_reveal_password=True,
                                      max_length=20,
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

    page.dialog = dlg_modal
    page.bottom_sheet = bs
    # 3
    # await page.client_storage.clear_async()
    # 3
    if await page.client_storage.contains_key_async("access_token"):
        acs_tok = await page.client_storage.get_async("access_token")
        rfr_tok = await page.client_storage.get_async("refresh_token")
        TodoApp.sync(acs_tok, rfr_tok)
    else:
        dlg_modal.open = True
    await page.add_async(TodoApp())

# app(main)
app(target=main, view=AppView.WEB_BROWSER, assets_dir="assets")
