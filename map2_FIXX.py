from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import basic_lighting_shader #pencahayaan dasar pada objek 3D
import subprocess

# Inisialisasi aplikasi Ursina
app = Ursina()
window.fullscreen = False
window.color = color.black

# Konfigurasi pemain
jump_force = 35  # Menambah tinggi lompatan pemain
max_fall_height = -20
FONT = "gui_assets/font/PixelOperatorMono8-Bold.ttf"

# Membuat objek pemain dengan kontroler orang pertama
player = FirstPersonController(collider='box', speed=47, jump_duration=5)
player.gravity = 0.8
player.cursor.visible = True
player.position = (0, 1, 0)
player.rotation_y = 180  # Membuat pemain menghadap ke arah sebaliknya

# Membuat entitas pulau melayang
island = Entity(
    model="gui_assets/level/floatingisland_only_NEW.obj",
    position=(135, -60, 300),
    collider='mesh',
    scale=1,
    texture="gui_assets/level/level.png",
    shader=basic_lighting_shader,
    double_sided=True
)

# Membuat entitas latar belakang
background = Entity(
    model="gui_assets/level/eye_long_NEWwwwwwwwwww.obj",
    position=(0, -4350, -500),
    scale=10,
    double_sided=True,
    texture="gui_assets/level/eyenew_sharpened.jpeg"
)
background.rotation_y = -90

# Membuat entitas garis finish
finish = Entity(
    model="Finish_Line.obj",
    position=(134.5, -60, 310),
    scale=1,
    double_sided=True,
    texture="gui_assets/level/finish.png"
)

# Membuat daftar jumppads
jumppads = [
    Entity(model='cube', color=color.red, position=(-11, -6.6, -73), scale=(3, 0.2, 3), collider='box', rotation=(0, 40, 0)),
    Entity(model='cube', color=color.red, position=(18, -6.20, -130), scale=(3, 0.2, 3), collider='box', rotation=(0, 45, 0)),
    Entity(model='cube', color=color.red, position=(-13, -12.5, -351), scale=(2, 0.2, 2), collider='box', rotation=(0, 50, 0)),
    Entity(model='cube', color=color.red, position=(52, -12.5, -477.8), scale=(3, 0.2, 3), collider='box', rotation=(0, 25, 0)),
    Entity(model='cube', color=color.red, position=(40, -6.7, -756.5), scale=(2, 0.2, 2), collider='box', rotation=(0, 25, 0)),
    Entity(model='cube', color=color.red, position=(27, -11, -420), scale=(2, 0.2, 2), collider='box', rotation=(0, -25, 0)),
    Entity(model='cube', color=color.red, position=(35, -4, -630), scale=(2, 0.2, 2), collider='box', rotation=(0, 25, 0)),
    Entity(model='cube', color=color.red, position=(15, -5.5, -558), scale=(2, 0.2, 2), collider='box', rotation=(0, 62, 0)),
    Entity(model='cube', color=color.red, position=(11, -6.2, -710), scale=(2, 0.2, 2), collider='box', rotation=(0, 40, 0)),
]

# Entitas garis finish
finish_line = Entity(
    model='cube',
    color=color.clear,
    position=(-20, 10, -826),
    scale=(45, 45, 5),
    collider='mesh'
)

# Pesan selesai permainan
finish_message = Text(
    text='Congratulations! You finished the game!',
    font=FONT,
    origin=(0, 0),
    scale=2,
    color=color.yellow
)
finish_message.disable()  # Nonaktifkan pesan selesai permainan awalnya

# Variabel timer
timer_text = Text(text="Time: 01:00", origin=(-2.5, -8.5), scale=2, color=color.white)
timer_seconds = 60  # 1 menit
timer_running = True  # Flag untuk mengontrol timer

def restart_game():
    global timer_seconds, timer_running
    timer_seconds = 60  # Reset timer
    timer_text.text = "Time: 01:00"  # Reset tampilan timer
    finish_message.disable()  # Nonaktifkan pesan selesai saat restart
    player.position = (0, 1, 0)
    player.rotation_y = 180  # Reset rotasi pemain
    player.gravity = 0.8  # Reset gravitasi jika diubah selama mode terbang
    player.y_velocity = 0  # Reset kecepatan vertikal
    player.x_velocity = 0  # Reset kecepatan horizontal
    timer_running = True  # Mulai ulang timer

def load_map1():
    # Gunakan subprocess untuk meluncurkan map1.py
    subprocess.Popen(["python", "map1_FIX.py"])
    application.quit()  # Tutup jendela permainan saat ini

def input(key):
    if key == 'q':
        quit()

    if key == 'r':
        player.position = (0, 1, 0)

def update():
    global timer_seconds, timer_running

    if timer_running:
        timer_seconds -= time.dt  # Kurangi timer

        # Update tampilan timer
        minutes = int(timer_seconds // 60)
        seconds = int(timer_seconds % 60)
        timer_text.text = f"Time: {minutes:01}:{seconds:01}"
    
    if timer_seconds <= 0:
        timer_running = False  # Hentikan timer
        load_map1()  # Muat peta berikutnya
    
    if player.y < max_fall_height:
        restart_game()

    if held_keys['shift']:
        player.gravity = 5
    else:
        player.gravity = 0.8

    # Deteksi interaksi dengan jumppads
    for jumppad in jumppads:
        if player.intersects(jumppad).hit:
            player.y += jump_force  # Terapkan gaya lompatan
            break  # Pastikan hanya satu gaya lompatan yang diterapkan pada satu waktu

    # Deteksi interaksi dengan garis finish
    if player.intersects(finish_line).hit:
        finish_message.enable()  # Tampilkan pesan selesai
        timer_running = False  # Hentikan timer
        invoke(lambda: finish_message.disable(), delay=2)  # Sembunyikan pesan setelah 2 detik
        invoke(restart_game, delay=2.5)  # Mulai ulang permainan setelah menampilkan pesan selesai

app.run()