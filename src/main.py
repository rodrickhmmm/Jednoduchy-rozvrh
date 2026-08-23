import flet as ft

from config import token, usrname, pswrd

def main(page: ft.Page):
    page.clean()

    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    page.add(
        ft.Text(
            f"{token}", 
            size=40,
            weight=ft.FontWeight.W_600, 

        ),

        ft.Text(
            f"{usrname}", 
            size=40,
            weight=ft.FontWeight.W_600, 

        ),
        ft.Text(
            f"{pswrd}", 
            size=40,
            weight=ft.FontWeight.W_600, 

        ),
    )


if __name__ == "__main__":
    ft.run(main)
