from ursina import * #library ursina menangani grafik, input, dan fisika dalam 3D
from ursina.prefabs.first_person_controller import FirstPersonController #kontorler pemain WASD, Jump, Mouse Look
from random import randint #menghasilkan bii=langan acak untuk menentukan blok akan hancur atau tidak
import subprocess #untuk menjalankan map2

#insialisasi aplikasi ursina
app = Ursina()

#mengatur warna latar belakang
window.fullscreen = False
window.color = color.black

#definisi font untuk menu
FONT = "gui_assets/font/PixelOperatorMono8-Bold.ttf"
FONT_death = "gui_assets/font/Garamond-Roman Light.ttf"

#mengetahui status permainan
game_active = False 

#pembutan menu
title_menu = Text(text='WATCH YOUR STEP!', font=FONT, origin=(0, 0), scale=2, position=(0, 0.4))
start_button = Button(text='Start Game', scale=(0.4, 0.1), position=(0, 0.1), on_click=lambda: start_game())
quit_button = Button(text='Quit Game', scale=(0.5, 0.1), position=(0, -0.1), on_click=lambda: quit_game())
start_button.text_entity.font = FONT
quit_button.text_entity.font = FONT

#insialisasi pemain dengan mode fps
player = FirstPersonController(collider='box', jump_duration=0.35, speed=5) #bentuk fisik berupa kotak, durasi lompat, kecepatan gerakan pemain
player.cursor.visible = True #menampilkan crosshair
max_fall_height = -10 #batas jatuh pemain

#pembuatan tanah start
ground = Entity(model='plane', texture='brick', collider='mesh', scale=(30, 0, 3))
ground = Entity(model='quad', color=color.red, position=(1, 1, -1.5), scale=(40, 5, 3), collider='box')

#objek cube sebagai bungkus rintangan dengan texture menggunakan gambar
cube1 = Entity(model="gui_assets/level/eye_fix.obj", texture='eyenew_sharpened.jpeg', scale=(11), position=(-1630, -1350, 1540), double_sided=True)
cube1.disable()

#membuat kerangka jembatan warna merah
pill1 = Entity(model='cube', color=color.red, scale=(0.4, 0.1, 53), z=28, x=-0.7)
pill2 = duplicate(pill1, x=-3.7)
pill3 = duplicate(pill1, x=0.6)
pill4 = duplicate(pill1, x=3.6)

#fungsi membuat block jembatan
def create_blocks():
    blocks = []
    for i in range(12):
        block = Entity(model='cube', collider='box', color=color.white33, position=(2, 0.1, 3 + i * 4), scale=(3, 0.1, 2.5))
        block2 = duplicate(block, x=-2.2)
        blocks.append((block, block2, randint(0, 10) > 7, randint(0, 10) > 7))
    return blocks
blocks = create_blocks()

#pembuatan tanah finsih dan pop up text
goal = Entity(model='cube', texture='brick', z=55, scale=(10, 1, 10), collider='mesh')
finish_cube = Entity(model='cube', color=color.clear, position=(0, 1.5, 57), scale=(10, 1, 10), collider='box')
finish_message = Text(text='You are not Done yet!, it is just the beginning of all!', font=FONT, position=(0, 0), origin=(0, 0), scale=1, color=color.white)
finish_message.disable()

#pop up saat jatuh
death_message_background = Panel(scale=(0.5, 0.1), color=color.black66, position=(0, 0))
death_message_background.disable()
death_message = Text(text='Try Again', font=FONT_death, position=(0, 0), origin=(0, 0), scale=2, color=color.red)
death_message.disable()

#nyawa pemain
life = 3
offset_x = 10
life_images = [Entity(model='quad', texture='gui_assets/life_heart.png', scale=(10, 10), position=(offset_x + i * 5, 10, 60)) for i in range(3)]

#fungsi memperbarui nyawa
def update_life_indicators():
    for i, life_image in enumerate(life_images):
        if i < life:
            life_image.enable()
        else:
            life_image.disable()

#fungsi memulai permainan
def start_game():
    global game_active, life
    game_active = True
    life = 3
    death_message.text = ''
    death_message_background.disable()
    death_message.disable()
    cube1.enable()

    #menonaktifkan menu
    for e in [title_menu, start_button, quit_button]:
        e.disable()

    #mengaktifkan entitas
    for entity in [player, ground, pill1, pill2, pill3, pill4, goal, finish_cube]:
        entity.enable()

    for block1, block2, _, _ in blocks:
        block1.enable()
        block2.enable()

    player.position = (0, 1, 0)
    update_life_indicators()

#fungsi mengulang permainan
def restart_game():
    global game_active
    game_active = False
    death_message.disable()
    death_message_background.disable()
    cube1.disable()

    for entity in [player, ground, pill1, pill2, pill3, pill4, goal, finish_cube]:
        entity.disable()

    for block1, block2, _, _ in blocks:
        block1.disable()
        block2.disable()

    for life_image in life_images:
        life_image.disable()

    title_menu.enable()
    start_button.enable()
    quit_button.enable()
    finish_message.disable()

#fungsi untuk memuat map2
def load_map2():
    subprocess.Popen(["python", "map2_FIXX.py"])
    application.quit()

#fungsi ketika pemain mati
def player_died():
    global life
    life -= 1

    death_message_background.enable()
    death_message.text = 'Try Again'
    death_message.enable()
    invoke(lambda: (death_message_background.disable(), setattr(death_message, 'text', ''), death_message.disable()), delay=1.5)

    if life <= 0:
        restart_game()
    else:
        update_life_indicators()

#fungsi memperbarui permainan
def update():
    global game_active
    if game_active:
        if player.y < max_fall_height:
            player_died()
            if life > 0:
                player.position = (0, 1, 0)

        block_destroyed = False

        for block1, block2, k, n in blocks:
            if not block_destroyed:
                if block1.intersects() and k:
                    invoke(destroy, block1, delay=0.1)
                    block1.fade_out(duration=0.1)
                    block_destroyed = True
                elif block2.intersects() and n:
                    invoke(destroy, block2, delay=0.1)
                    block2.fade_out(duration=0.1)
                    block_destroyed = True

        if finish_cube.intersects(player):
            finish_message.enable()
            invoke(finish_message.disable, delay=2)
            game_active = False
            invoke(restart_game, delay=2)

        if player.intersects(finish_cube).hit:
            finish_message.enable()
            invoke(load_map2, delay=1)

#shortcut quit dan restart
def input(key):
    if key == 'q':
        quit()
    if key == 'r':
        restart_game()

#fungsi untuk quit
def quit_game():
    application.quit()

#menonaktifkan entitas
for entity in [player, ground, pill1, pill2, pill3, pill4, goal, finish_cube, cube1]:
    entity.disable()

for block1, block2, _, _ in blocks:
    block1.disable()
    block2.disable()

for life_image in life_images:
    life_image.disable()

#mengaktifkan menu utama
title_menu.enable()
start_button.enable()
quit_button.enable()

#menjalankan aplikasi ursina
app.run()