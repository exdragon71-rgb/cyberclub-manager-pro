import multiprocessing
import os
import socket
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox
import webbrowser


def prepare_windowed_streams() -> None:
    if sys.stdout is None:
        sys.stdout = open(
            os.devnull,
            "w",
            encoding="utf-8",
        )

    if sys.stderr is None:
        sys.stderr = open(
            os.devnull,
            "w",
            encoding="utf-8",
        )


prepare_windowed_streams()


import uvicorn

from app.main import app


HOST = "127.0.0.1"
PORT = 8000
APP_URL = f"http://{HOST}:{PORT}/"


def port_is_open() -> bool:
    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    ) as client:
        client.settimeout(0.4)

        return (
            client.connect_ex(
                (HOST, PORT),
            )
            == 0
        )


class DesktopLauncher:
    def __init__(
        self,
        root: tk.Tk,
    ) -> None:
        self.root = root

        self.root.title(
            "CyberClub Manager Pro"
        )

        self.root.geometry(
            "460x260"
        )

        self.root.resizable(
            False,
            False,
        )

        self.server = uvicorn.Server(
            uvicorn.Config(
                app=app,
                host=HOST,
                port=PORT,
                log_level="warning",
                access_log=False,
                log_config=None,
            )
        )

        self.server_thread: (
            threading.Thread
            | None
        ) = None

        self.status_label = tk.Label(
            root,
            text="Запуск приложения...",
            font=(
                "Segoe UI",
                13,
                "bold",
            ),
        )

        self.status_label.pack(
            pady=(35, 12),
        )

        self.address_label = tk.Label(
            root,
            text=APP_URL,
            font=(
                "Segoe UI",
                10,
            ),
        )

        self.address_label.pack(
            pady=(0, 25),
        )

        self.open_button = tk.Button(
            root,
            text="Открыть приложение",
            width=25,
            height=2,
            state=tk.DISABLED,
            command=self.open_browser,
        )

        self.open_button.pack(
            pady=5,
        )

        self.stop_button = tk.Button(
            root,
            text="Остановить и выйти",
            width=25,
            command=self.stop,
        )

        self.stop_button.pack(
            pady=5,
        )

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.stop,
        )

        self.start()

    def start(self) -> None:
        if port_is_open():
            self.status_label.config(
                text=(
                    "Приложение уже запущено"
                )
            )

            self.open_button.config(
                state=tk.NORMAL,
            )

            self.open_browser()
            return

        self.server_thread = (
            threading.Thread(
                target=self.run_server,
                daemon=True,
            )
        )

        self.server_thread.start()

        threading.Thread(
            target=self.wait_for_server,
            daemon=True,
        ).start()

    def run_server(self) -> None:
        try:
            self.server.run()

        except Exception as error:
            self.root.after(
                0,
                lambda: self.show_error(
                    str(error),
                ),
            )

    def wait_for_server(self) -> None:
        for _ in range(80):
            if port_is_open():
                self.root.after(
                    0,
                    self.mark_ready,
                )
                return

            time.sleep(0.25)

        self.root.after(
            0,
            lambda: self.show_error(
                "Сервер не запустился "
                "за 20 секунд.",
            ),
        )

    def mark_ready(self) -> None:
        self.status_label.config(
            text="Приложение работает",
        )

        self.open_button.config(
            state=tk.NORMAL,
        )

        self.open_browser()

    def open_browser(self) -> None:
        webbrowser.open(
            APP_URL,
        )

    def show_error(
        self,
        message: str,
    ) -> None:
        self.status_label.config(
            text="Ошибка запуска",
        )

        messagebox.showerror(
            "CyberClub Manager Pro",
            message,
        )

    def stop(self) -> None:
        self.status_label.config(
            text="Остановка...",
        )

        self.server.should_exit = True

        self.root.after(
            500,
            self.root.destroy,
        )


def main() -> None:
    multiprocessing.freeze_support()

    root = tk.Tk()

    DesktopLauncher(
        root,
    )

    root.mainloop()


if __name__ == "__main__":
    main()
