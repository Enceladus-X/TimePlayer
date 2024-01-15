import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, timedelta
import threading
import time
from pygame import mixer

class AudioPlayerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("TimePlayer")
        self.master.geometry("500x350")

        self.audio_files = []
        self.play_time = None
        self.last_play_time = None
        self.playing = False  # 현재 음악이 재생 중인지 여부
        self.cancelled = False  # 취소 여부

        # 오디오 파일 선택 버튼
        self.select_button = tk.Button(master, text="Select Audio Files", command=self.select_audio_files)
        self.select_button.pack(pady=10)

        # 시 선택
        self.hour_label = tk.Label(master, text="Select Hour:")
        self.hour_label.pack()

        self.hour_combobox = ttk.Combobox(master, state="readonly", values=[str(i) for i in range(24)])
        self.hour_combobox.set("0")  # 초기 선택값 설정
        self.hour_combobox.pack(pady=5)

        # 분 선택
        self.minute_label = tk.Label(master, text="Select Minute:")
        self.minute_label.pack()

        self.minute_combobox = ttk.Combobox(master, state="readonly", values=[str(i) for i in range(0, 60)])
        self.minute_combobox.set("0")  # 초기 선택값 설정
        self.minute_combobox.pack(pady=10)

        # 오디오 파일 선택 여부 확인 레이블
        self.audio_label = tk.Label(master, text="No audio file selected", fg="red")
        self.audio_label.pack(pady=10)

        # 선택된 시간 및 오디오 파일 안내 문구
        self.play_info_label = tk.Label(master, text="")
        self.play_info_label.pack(pady=5)

        # 활성화/대기 버튼
        self.activate_button = tk.Button(master, text="Activate", command=self.activate_audio)
        self.activate_button.pack(pady=10)

        # 취소 버튼
        self.cancel_button = tk.Button(master, text="Cancel", command=self.cancel_audio, state=tk.DISABLED)
        self.cancel_button.pack(pady=5)

        # 24시간 주기로 실행되는 스레드
        threading.Thread(target=self.run_periodically, daemon=True).start()

    def select_audio_files(self):
        self.audio_files = filedialog.askopenfilenames(title="Select Audio Files", filetypes=[("Audio Files", "*.mp3;*.wav")])

        if self.audio_files:
            self.audio_label.config(text="Audio file(s) selected", fg="green")
        else:
            self.audio_label.config(text="No audio file selected", fg="red")

    def activate_audio(self):
        if self.playing:
            messagebox.showinfo("Info", "Music is already playing.")
            return

        if not self.audio_files:
            messagebox.showinfo("Error", "No audio files selected.")
            return

        selected_hour = int(self.hour_combobox.get())
        selected_minute = int(self.minute_combobox.get())

        now = datetime.now()
        self.play_time = now.replace(hour=selected_hour, minute=selected_minute, second=0, microsecond=0)

        if self.play_time < now:
            # If the specified time has already passed for today, schedule for the same time on the next day
            self.play_time = self.play_time.replace(day=now.day + 1)

        wait_time = (self.play_time - now).total_seconds()
        threading.Thread(target=self.play_audio_thread, args=(wait_time,)).start()

        self.activate_button.config(state=tk.DISABLED, text="Waiting for music to finish...")
        self.cancel_button.config(state=tk.NORMAL)

        play_time_str = self.play_time.strftime("%I:%M %p")
        audio_files_str = "\n".join(self.audio_files)
        self.play_info_label.config(text=f"Audio will play at {play_time_str}\nFiles:\n{audio_files_str}")

    def play_audio_thread(self, wait_time):
        self.playing = True
        self.cancelled = False

        time.sleep(wait_time)

        while not self.cancelled:
            now = datetime.now()
            # 마지막으로 재생한 시간이 있고, 그 시간으로부터 1분이 지나지 않았으면 재생하지 않음
            if self.last_play_time and (now - self.last_play_time).total_seconds() < 60:
                break

            mixer.init()

            for file in self.audio_files:
                if self.cancelled:
                    break

                mixer.music.load(file)
                mixer.music.play()
                # 대기시간동안 스레드를 중지할 수 있으므로, 음악이 재생될 동안 대기
                while mixer.music.get_busy():
                    time.sleep(1)

                # 현재 시간을 마지막으로 재생한 시간으로 업데이트
                self.last_play_time = datetime.now()

        self.playing = False
        self.activate_button.config(state=tk.NORMAL, text="Activate")
        self.cancel_button.config(state=tk.DISABLED)
        self.play_info_label.config(text="")

    def cancel_audio(self):
        self.cancelled = True
        self.playing = False
        self.activate_button.config(state=tk.NORMAL, text="Activate")
        self.cancel_button.config(state=tk.DISABLED)
        self.play_info_label.config(text="Cancelled")

    def run_periodically(self):
        while True:
            # 매 24시간마다 실행되도록 설정
            now = datetime.now()
            next_run_time = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

            wait_time = (next_run_time - now).total_seconds()
            time.sleep(wait_time)

            # Activate 버튼을 누르는 것처럼 동작
            self.activate_audio()

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioPlayerApp(root)
    root.mainloop()
