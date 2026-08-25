import flet as ft
import requests
from datetime import date
from pathlib import Path

import config

config_data = Path(__file__).parent / "config.py"

placeholder_datum = True

if placeholder_datum:
    datum = "2026-06-15"
else:
    datum = date.today().strftime('%Y-%m-%d')

days_list = [
    ["Pondělí"],
    ["Úterý"],
    ["Středa"],
    ["Čtvrtek"],
    ["Pátek"],
]

color_bg = "#222324"
color_text_primary = "#FFFFFF"
color_text_light = "#E9E4F0"
color_field_background = "#312F38"
color_field_border = "#C3C2C9"
color_button_default = "#423C58"
color_button_hovered = "#5D557A"
color_time_text = "#D1C4E9"
color_table_border = "#7E7E7E"
color_heading_row = "#54405F"
color_error_text = ft.Colors.WHITE
color_error_background = ft.Colors.RED_400


def tokengen():
    url = f"{config.urlskoly}/api/login"
    head = {'Content-Type': 'application/x-www-form-urlencoded'}
    body = f'client_id=ANDR&grant_type=password&username={config.usrname}&password={config.pswrd}'

    try:
        response = requests.post(url, data=body, headers=head, timeout=15)
        response.raise_for_status()
        config.token = response.json().get('access_token')
    except Exception as e:
        config.token = None
        raise RuntimeError(f"Login request failed: {type(e).__name__}: {e}") from e

    if not config.token:
        raise RuntimeError("Server did not return an access_token.")
    return True

def request_timetable():
    base_url = config.urlskoly.rstrip('/')
    url = f"{base_url}/api/3/timetable/actual?date={datum}"
    head = {
        'Authorization': f'Bearer {config.token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=head, timeout=15)
    response.raise_for_status()
    return response.json()

def get_data_for_timetable(timetable_data):
    day_to_row_index = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4}
    max_lessons = 10

    subjects_by_id = {
        s["Id"]: s.get("Abbrev") or s.get("Name") or "N/A"
        for s in timetable_data.get("Subjects", [])
    }

    lessons_by_row = {idx: [] for idx in day_to_row_index.values()}

    for day in timetable_data.get("Days", []):
        row_idx = day_to_row_index.get(day.get("DayOfWeek"))
        if row_idx is None:
            continue

        for atom in sorted(day.get("Atoms", []), key=lambda a: a.get("HourId", 0)):
            subject_id = atom.get("SubjectId") or atom.get("Change", {}).get("SubjectId")
            if subject_id:
                lessons_by_row[row_idx].append(subjects_by_id.get(subject_id, f"ID:{subject_id}"))
            else:
                lessons_by_row[row_idx].append(atom.get("DayDescription", ""))

    for row_idx, row in enumerate(days_list):
        day_name = row[0]
        lessons = lessons_by_row.get(row_idx, [])[:max_lessons]
        lessons += [""] * (max_lessons - len(lessons))
        row[:] = [day_name] + lessons

def login_page(page: ft.Page):
    page.clean()

    def login_in_app():
        print(f"Username: {username_field.value}, Password: {password_field.value}, URL: {url_field.value}")
        config.usrname = username_field.value
        config.pswrd = password_field.value
        config.urlskoly = url_field.value

        with open(config_data, "w", encoding="utf-8") as f:
            f.write(f'usrname = {repr(config.usrname)}\n')
            f.write(f'pswrd = {repr(config.pswrd)}\n')
            f.write(f'urlskoly = {repr(config.urlskoly)}\n')
            f.write('token = None\n')
        page.clean()
        main(page)

    page.window.width = 800 
    page.window.height = 400 

    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    page.bgcolor = color_bg

    page.fonts = {
        "JetBrainsMono": "https://github.com/google/fonts/raw/main/ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf"
    }

    page.theme = ft.Theme(
        font_family="JetBrainsMono",
        text_theme=ft.TextTheme(
            body_medium=ft.TextStyle(color=color_text_primary, font_family="JetBrainsMono"),
            title_large=ft.TextStyle(color=color_text_primary, font_family="JetBrainsMono"),
            title_medium=ft.TextStyle(color=color_text_primary, font_family="JetBrainsMono"),
            title_small=ft.TextStyle(color=color_text_primary, font_family="JetBrainsMono"),
            body_small=ft.TextStyle(color=color_text_primary, font_family="JetBrainsMono"),
        ),
    )

    page.add(
        ft.Column(
            [
                ft.Text("Jednoduchý rozvrh", size=15, weight=ft.FontWeight.BOLD),
                ft.Text("Přihlásit se", size=24, weight=ft.FontWeight.BOLD),
                username_field := ft.TextField(
                    label="Uživatelské jméno", 
                    text_style=ft.TextStyle(color=color_text_light),
                    label_style=ft.TextStyle(color=color_text_light),
                    width=400,
                    bgcolor=color_field_background,
                    border_color=color_field_border,
                    border_width=3,
                    cursor_color=color_text_light,
                ),
                password_field := ft.TextField(
                    label="Heslo", 
                    label_style=ft.TextStyle(color=color_text_light),
                    text_style=ft.TextStyle(color=color_text_light),
                    width=400,
                    bgcolor=color_field_background,
                    border_color=color_field_border,
                    border_width=3,
                    cursor_color=color_text_light,
                    password=True, 
                    can_reveal_password=True
                ),

                url_field := ft.TextField(
                    label="URL školy", 
                    width=400,
                    text_style=ft.TextStyle(color=color_text_light),
                    label_style=ft.TextStyle(color=color_text_light),
                    bgcolor=color_field_background,
                    border_color=color_field_border,
                    border_width=3,
                    cursor_color=color_text_light,
                ),
                ft.ElevatedButton(
                    "Přihlásit se", 
                    width=400,
                    height=50,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=0),
                        bgcolor={
                            ft.ControlState.DEFAULT: color_button_default,
                            ft.ControlState.HOVERED: color_button_hovered,
                        },
                        text_style=ft.TextStyle(weight=ft.FontWeight.W_400, font_family="JetBrainsMono"),
                        color=color_text_light,
                        mouse_cursor=ft.MouseCursor.CLICK,
                    ),
                    on_click=lambda e: login_in_app()
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        )
    )

def main(page: ft.Page):

    page.clean()

    COLUMNS = ["Den", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    COLUMNS_TIMES = ["Den", "8:10 - 8:55", "9:00 - 9:45", "10:00 - 10:45", "10:55 - 11:40", "11:50 - 12:35", "12:45 - 13:30", "13:35 - 14:20", "14:00 - 14:45", "14:50 - 15:35"]

    error_message = None

    try:
        tokengen()
        timetable_json = request_timetable()
        get_data_for_timetable(timetable_json)
    except Exception as e:
        error_message = f"{type(e).__name__}: {e}"

    for row in days_list:
        if len(row) > 10:
            del row[10:]
        row.extend([""] * (10 - len(row)))

    page.window.width = 800 
    page.window.height = 400 

    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    page.bgcolor = color_bg

    page.fonts = {
        "JetBrainsMono": "https://github.com/google/fonts/raw/main/ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf"
    }

    page.theme = ft.Theme(
        font_family="JetBrainsMono",
        text_theme=ft.TextTheme(
            body_medium=ft.TextStyle(color=color_text_primary, font_family="JetBrainsMono"),
            title_large=ft.TextStyle(color=color_text_primary, font_family="JetBrainsMono"),
            title_medium=ft.TextStyle(color=color_text_primary, font_family="JetBrainsMono"),
            title_small=ft.TextStyle(color=color_text_primary, font_family="JetBrainsMono"),
            body_small=ft.TextStyle(color=color_text_primary, font_family="JetBrainsMono"),
        ),
    )
    
    columns = [
        ft.DataColumn(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            col,
                            weight=ft.FontWeight.BOLD,
                            size=15,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        *(
                            [
                                ft.Text(
                                    COLUMNS_TIMES[idx],
                                    size=12,
                                    color=color_time_text,
                                    text_align=ft.TextAlign.CENTER,
                                )
                            ]
                            if idx > 0 and idx < len(COLUMNS_TIMES) and COLUMNS_TIMES[idx]
                            else []
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2,
                ),
                width=90 if idx == 0 else 70,
                alignment=ft.alignment.Alignment(0, 0),
            )
        )
        for idx, col in enumerate(COLUMNS)
    ]

    rows = []

    for row_data in days_list:
        cells = []
        for i, value in enumerate(row_data):
            bg = None
            cell_width = 90 if i == 0 else 70

            cells.append(
                ft.DataCell(
                    ft.Container(
                        content=ft.Text(
                            value,
                            weight=ft.FontWeight.BOLD if i == 0 else ft.FontWeight.NORMAL,
                            size=15,
                            font_family="JetBrainsMono",
                            no_wrap=True,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        bgcolor=bg,
                        padding=8,
                        border_radius=6,
                        width=cell_width,
                        alignment=ft.alignment.Alignment(0, 0),
                    )
                )
            )
        rows.append(ft.DataRow(cells=cells))

    table = ft.DataTable(
        columns=columns,
        rows=rows,
        border=ft.Border.all(3, color_table_border),
        vertical_lines=ft.BorderSide(2, color_table_border),
        horizontal_lines=ft.BorderSide(2, color_table_border),
        heading_row_color=color_heading_row,
        heading_row_height=60,
        data_row_min_height=0,
        column_spacing=0,
    )

    page.add(
        ft.Column(
            [
                ft.Text("Jednoduchý rozvrh", size=24, weight=ft.FontWeight.BOLD),
                *(
                    [
                        ft.Container(
                            content=ft.Text(
                                f"Error: {error_message}",
                                color=color_error_text,
                                size=12,
                            ),
                            bgcolor=color_error_background,
                            padding=10,
                            border_radius=6,
                        )
                    ]
                    if error_message
                    else []
                ),
                ft.Row([table], scroll=ft.ScrollMode.AUTO),
            ],
        )
    )

if not getattr(config, 'usrname', None) and not getattr(config, 'pswrd', None):
    ft.run(login_page)
else:
    ft.run(main)