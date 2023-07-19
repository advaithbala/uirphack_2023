import math
import time
from typing import List
import pygame
import sys
import os
import random
import platform
# import subprocess
from repair import repair
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768

roadW = 2000  # road width (left to right)
segL = 200  # segment length (top to bottom)
camD = 0.84  # camera depth
show_N_seg = 300

dark_grass = pygame.Color(0, 154, 0)
light_grass = pygame.Color(16, 200, 16)
white_rumble = pygame.Color(255, 255, 255)
black_rumble = pygame.Color(0, 0, 0)
dark_road = pygame.Color(105, 105, 105)
light_road = pygame.Color(107, 107, 107)

class Line:
    def __init__(self, i):
        self.i = i
        self.x = self.y = self.z = 0.0  # game position (3D space)
        self.X = self.Y = self.W = 0.0  # game position (2D projection)
        self.scale = 0.0  # scale from camera position
        self.curve = 0.0  # curve radius
        self.spriteX = 0.0  # sprite position X
        self.clip = 0.0  # correct sprite Y position
        self.sprite: pygame.Surface = None
        self.sprite_rect: pygame.Rect = None

        self.grass_color: pygame.Color = "black"
        self.rumble_color: pygame.Color = "black"
        self.road_color: pygame.Color = "black"

        self.battery_z_pos : float = None
        self.battery_pos : float =  None

        self.tesla_pos_x : float = None
        self.tesla_pos_y : float = None
        self.tesla_pos: float = None

        self.ret = None
        
    def project(self, camX: int, camY: int, camZ: int):
        self.scale = camD / (self.z - camZ)
        self.X = (1 + self.scale * (self.x - camX)) * WINDOW_WIDTH / 2
        self.Y = (1 - self.scale * (self.y - camY)) * WINDOW_HEIGHT / 2
        self.W = self.scale * roadW * WINDOW_WIDTH / 2

    def drawSprite(self, draw_surface: pygame.Surface):
        if self.sprite is None:
            return
        w = self.sprite.get_width()
        h = self.sprite.get_height()
        destX = self.X + self.scale * self.spriteX * WINDOW_WIDTH / 2
        destY = self.Y + 4
        destW = w * self.W / 266
        destH = h * self.W / 266

        destX += destW * self.spriteX
        destY += destH * -1

        clipH = destY + destH - self.clip
        if clipH < 0:
            clipH = 0
        if clipH >= destH:
            return

        # avoid scalling up images which causes lag
        if destW > w:
            return

        # mask the sprite if below ground (clipH)
        scaled_sprite = pygame.transform.scale(self.sprite, (destW, destH))
        crop_surface = scaled_sprite.subsurface(0, 0, destW, destH - clipH)

        draw_surface.blit(crop_surface, (destX, destY))


def draw_car(draw_surface: pygame.Surface, isTent):
    car_sprite : pygame.Surface = "None"
    if(isTent):
        car_sprite = pygame.image.load(f"images/R1T_Tent.png").convert_alpha()
        spriteW, spriteH = car_sprite.get_width(), car_sprite.get_height()
        scale = 1.6
        scaledW, scaledH = spriteW//scale, spriteH//scale
        scaled_sprite = pygame.transform.scale(car_sprite, (scaledW, scaledH))

        carX = draw_surface.get_width()//2 - scaledW//2 + 15
        carY = draw_surface.get_width()//2 - 425
        draw_surface.blit(scaled_sprite, (carX, carY))

    else:
        car_sprite = pygame.image.load(f"images/R1T_white.png").convert_alpha()
        spriteW, spriteH = car_sprite.get_width(), car_sprite.get_height()
        scale = 1.2
        scaledW, scaledH = spriteW//scale, spriteH//scale
        scaled_sprite = pygame.transform.scale(car_sprite, (scaledW, scaledH))

        carX = draw_surface.get_width()//2 - scaledW//2
        carY = draw_surface.get_width()//2 - 100
        draw_surface.blit(scaled_sprite, (carX, carY))


def draw_distance(draw_surface: pygame.Surface, distance):

    font = pygame.font.Font('PixeloidSansBold-PKnYd.ttf', 32)
    text = font.render("Distance: ", True, (0, 9, 0), None)
    textRect = text.get_rect()
    textX = 400
    textY = 150
    textRect.center = (textX, textY)  
    draw_surface.blit(text, textRect)

    # Format distance as 0.00 km
    distance_text = str(distance//100) + " m"
    distance_display = font.render(distance_text, True, (0, 0, 0))
    distance_rect = distance_display.get_rect(center=(textX + 200, textY))
    draw_surface.blit(distance_display, distance_rect)

def draw_battery(draw_surface: pygame.Surface, battery_level, battery_max):


    # Battery icon
    batteryW = 80
    batteryH = 32
    batteryX = draw_surface.get_width() - 200
    batteryY = 32
    charged_level = int(batteryW * (battery_level / battery_max))
    pygame.draw.rect(draw_surface, (0,150,0), pygame.Rect(batteryX, batteryY, charged_level, batteryH))
    pygame.draw.rect(draw_surface, (0,0,0), pygame.Rect(batteryX, batteryY, batteryW, batteryH), 2, 5)
    pygame.draw.rect(draw_surface, (0,0,0), pygame.Rect(batteryX + batteryW, batteryY + 5, 5, 22))


    font = pygame.font.Font('PixeloidSansBold-PKnYd.ttf', 32)
    text = font.render(str(battery_level), True, (0, 0, 0), None)
    textRect = text.get_rect()
    textX = batteryX + batteryW // 2 * 3 + 20
    textY = batteryY + batteryH // 2
    textRect.center = (textX, textY)  
    draw_surface.blit(text, textRect)

def draw_timer(draw_surface: pygame.Surface, time_left):
    font = pygame.font.Font('PixeloidSansBold-PKnYd.ttf', 32)
    text = font.render("Time :  ", True, (0, 0, 0), None)
    textRect = text.get_rect()
    textX = 400
    textY = 100
    textRect.center = (textX, textY)  
    draw_surface.blit(text, textRect)

    # Calculate minutes and seconds from time_left
    minutes = time_left // 60
    seconds = time_left % 60

    # Format time as MM:SS
    time_text = f"{minutes:02}:{seconds:02}"
    time_display = font.render(time_text, True, (0, 0, 0))
    time_rect = time_display.get_rect(center=(textX + 150, textY))
    draw_surface.blit(time_display, time_rect)


def drawQuad(
    surface: pygame.Surface,
    color: pygame.Color,
    x1: int,
    y1: int,
    w1: int,
    x2: int,
    y2: int,
    w2: int,
):
    pygame.draw.polygon(
        surface, color, [(x1 - w1, y1), (x2 - w2, y2), (x2 + w2, y2), (x1 + w1, y1)]
    )

def map_value(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

class GameWindow:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Rivian Adventure")
        self.window_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.last_time = time.time()
        self.dt = 0
        self.crashed_CD = 0
        self.battery_max = 7777
        self.battery_level = self.battery_max
        self.game_started = False
        self.game_ended = False
        self.tesla = pygame.transform.scale(pygame.image.load("./static/tesla.png"), (150, 100))
        self.flame = pygame.transform.scale(pygame.image.load("./static/flame.png"), (150, 100))
        self.timer_duration = 2 * 60  # 2 minutes
        self.time_left = self.timer_duration
        self.distance = 0 

        # background
        if platform.system() == "Darwin":
            self.background_image = pygame.image.load("images/bg.png").convert()
        else: 
            self.background_image = pygame.image.load("images/bg.png").convert_alpha()

        self.background_image = pygame.transform.scale(
            self.background_image, (WINDOW_WIDTH, self.background_image.get_height())
        )
        self.background_surface = pygame.Surface(
            (self.background_image.get_width() * 3, self.background_image.get_height())
        )
        self.background_surface.blit(self.background_image, (0, 0))
        self.background_surface.blit(
            self.background_image, (self.background_image.get_width(), 0)
        )
        self.background_surface.blit(
            self.background_image, (self.background_image.get_width() * 2, 0)
        )
        self.background_rect = self.background_surface.get_rect(
            topleft=(-self.background_image.get_width(), 0)
        )
        self.window_surface.blit(self.background_surface, self.background_rect)

        # sprites
        self.sprites: List[pygame.Surface] = []
          
        for i in range(1, 9):
            if platform.system() == "Darwin":
                tmp = pygame.image.load(f"images/{i}.png")
                if i==8:
                    tmp = pygame.transform.scale(tmp, (100,200))
                self.sprites.append(tmp.convert())
            else: 
                tmp = pygame.image.load(f"images/{i}.png")
                if i==8:
                    tmp = pygame.transform.scale(tmp,  (100,200))
                self.sprites.append(tmp.convert_alpha())
                
    def draw_enter_page(self):
        # Draw the transparent mask over the game window
        # mask = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        #set a transparent color 
        mask = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        mask.fill((0, 0, 0, 1))  # Semi-transparent black
        self.window_surface.blit(mask, (0, 0))

        # Draw the "Start Playing" button with rounded corners
        button_width = 250
        button_height = 80
        button_rect = pygame.Rect(
            (WINDOW_WIDTH - button_width) // 2,
            (WINDOW_HEIGHT - button_height) // 2,
            button_width,
            button_height
        )
        padding = 10  # Padding around the button
        outer_button_rect = button_rect.inflate(padding, padding)

        mouse_pos = pygame.mouse.get_pos()
        if button_rect.collidepoint(mouse_pos):
            button_color = (200, 200, 200)  # Light gray
            outer_button_color = (150, 150, 150)  # Darker gray
        else:
            button_color = (255, 255, 255)  # White
            outer_button_color = (200, 200, 200)  # Light gray

        pygame.draw.rect(self.window_surface, outer_button_color, outer_button_rect, border_radius=10)
        pygame.draw.rect(self.window_surface, button_color, button_rect, border_radius=10)

        # Draw the "Start Playing" button text
        font = pygame.font.Font('PixeloidSansBold-PKnYd.ttf', 28)  # Smaller font size
        text = font.render("Start Playing", True, (0, 0, 0))
        self.text_rect = text.get_rect(center=button_rect.center)
        self.window_surface.blit(text, self.text_rect)

        # Set up the font for the game title
        title_font = pygame.font.Font("PixeloidSansBold-PKnYd.ttf", 48)

        # Render the game title text
        title_text = title_font.render("Rivian Adventure", True, (255, 255, 255))

        # Get the rectangle for the rendered text
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 100))

        # Draw the game title on the window surface
        self.window_surface.blit(title_text, title_rect)

    def draw_end_page(self, dist):
        mask = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        mask.fill((0, 0, 0, 0))  # Semi-transparent black
        self.window_surface.blit(mask, (0, 0))

        # Draw the "Start Playing" button with rounded corners
        button_width = 250
        button_height = 80
        button_rect = pygame.Rect(
            (WINDOW_WIDTH - button_width) // 2,
            (WINDOW_HEIGHT - button_height) // 2,
            button_width,
            button_height
        )
        padding = 10  # Padding around the button
        outer_button_rect = button_rect.inflate(padding, padding)

        mouse_pos = pygame.mouse.get_pos()
        if button_rect.collidepoint(mouse_pos):
            button_color = (200, 200, 200)  # Light gray
            outer_button_color = (150, 150, 150)  # Darker gray
        else:
            button_color = (255, 255, 255)  # White
            outer_button_color = (200, 200, 200)  # Light gray

        pygame.draw.rect(self.window_surface, outer_button_color, outer_button_rect, border_radius=10)
        pygame.draw.rect(self.window_surface, button_color, button_rect, border_radius=10)

        # Draw the play again button
        font = pygame.font.Font('PixeloidSansBold-PKnYd.ttf', 28)  # Smaller font size
        text = font.render("Play Again", True, (0, 0, 0))
        self.play_again_rect = text.get_rect(center=button_rect.center)
        self.window_surface.blit(text, self.play_again_rect)

        draw_distance(self.window_surface, dist)
        draw_timer(self.window_surface, self.time_left)

    prevPlayerX = 0

    def run(self):

        # create road lines for each segment
        lines: List[Line] = []
        for i in range(1600):
            line = Line(i)
            line.z = (
                i * segL + 0.00001
            )  # adding a small value avoids Line.project() errors

            # change color at every other 3 lines (int floor division)
            grass_color = light_grass if (i // 3) % 2 else dark_grass
            rumble_color = white_rumble if (i // 3) % 2 else black_rumble
            road_color = light_road if (i // 3) % 2 else dark_road

            line.grass_color = grass_color
            line.rumble_color = rumble_color
            line.road_color = road_color

            # right curve
            if 300 < i < 700:
                line.curve = 0.5

            # uphill and downhill
            if i > 750:
                line.y = math.sin(i / 30.0) * 1500

            # left curve
            if i > 1100:
                line.curve = -0.7

            # Sprites segments
            if i < 300 and i % 20 == 0:
                line.spriteX = -2.5
                line.sprite = self.sprites[4]

            if i % 17 == 0:
                line.spriteX = 2.0
                line.sprite = self.sprites[5]

            if i > 300 and i % 20 == 0:
                line.spriteX = -0.7
                line.sprite = self.sprites[3]

            if i > 800 and i % 20 == 0:
                line.spriteX = -1.2
                line.sprite = self.sprites[0]

            if i == 400:
                line.spriteX = -1.2
                line.sprite = self.sprites[6]


            if i % (50) == 0 or i % 65 == 0:
                if random.random() < 0.55:  # 1% chance to place a Tesla on each line
                    line.spriteX = random.uniform(-3, 2)  # Random position on the road
                    line.sprite = self.tesla
                    line.tesla_pos = line.spriteX
            if i % (70) == 0 or i % (120) == 0:
                random_battery_pos = random.uniform(-3, 2)
                line.spriteX = random_battery_pos
                line.battery_pos = line.spriteX
                line.sprite = self.sprites[7]
                for prev_line in lines[-2:]:
                    prev_line.battery_pos = random_battery_pos

            lines.append(line)

        N = len(lines)
        isTent = False
        pos = 0
        playerX = 0  # player start at the center of the road
        playerY = 1000  # camera height offset
        prev_line_has_battery = False
        prev_line_has_tesla = False

        # Set timer duration (in seconds)

        start_time = time.time()

        while True:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP and not self.game_started:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.text_rect.collidepoint(mouse_pos):
                        self.game_started = True
                if event.type == pygame.MOUSEBUTTONUP and self.game_ended:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.play_again_rect.collidepoint(mouse_pos):
                        pygame.quit()
                        python = sys.executable
                        os.execl(python, python, * sys.argv)

            if self.time_left == 0:
                self.game_ended = True

            if self.game_ended: 
                self.draw_end_page(self.distance)
            elif not self.game_started:
                self.draw_enter_page()
            else:

                out_of_bounds = (playerX > 3000) or (playerX < -3000)

                self.dt = time.time() - self.last_time
                self.last_time = time.time()
                self.window_surface.fill((105, 205, 4))

                for event in pygame.event.get([pygame.QUIT]):
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                speed = 0
                keys = pygame.key.get_pressed()
                if keys[pygame.K_t]:
                    isTent = not isTent

                if keys[pygame.K_UP]:
                    if self.battery_level == 0:
                        continue
                    if(out_of_bounds):
                        speed += segL # it has to be N integer times the segment length
                        self.battery_level = max(0, self.battery_level - 2)
                    else:   
                        speed += (segL * 2) # it has to be N integer times the segment length
                        self.battery_level = max(0, self.battery_level - 10)


                if keys[pygame.K_DOWN]:
                    if self.battery_level == 0:
                        continue              
                    speed -= segL  # it has to be N integer times the segment length
                if keys[pygame.K_RIGHT]:
                    if self.battery_level == 0:
                        continue
                    playerX += 75
                if keys[pygame.K_LEFT]:
                    if self.battery_level == 0:
                        continue
                    playerX -= 75
                if keys[pygame.K_w]:
                    playerY += 100
                if keys[pygame.K_s]:
                    playerY -= 100
                # avoid camera going below ground
                if playerY < 500:
                    playerY = 500
                # turbo speed
                if keys[pygame.K_TAB]:
                    speed *= 2  # it has to be N integer times the segment length
                    self.battery_level = max(0, self.battery_level - 30)

                pos += speed
                self.distance += speed

                # loop the circut from start to finish
                while pos >= N * segL:
                    pos -= N * segL
                while pos < 0:
                    pos += N * segL
                startPos = pos // segL

                x = dx = 0.0  # curve offset on x axis

                camH = lines[startPos].y + playerY
                maxy = WINDOW_HEIGHT

                if speed > 0:
                    self.background_rect.x -= lines[startPos].curve * 2
                elif speed < 0:
                    self.background_rect.x += lines[startPos].curve * 2

                if self.background_rect.right < WINDOW_WIDTH:
                    self.background_rect.x = -WINDOW_WIDTH
                elif self.background_rect.left > 0:
                    self.background_rect.x = -WINDOW_WIDTH

                self.window_surface.blit(self.background_surface, self.background_rect)

                # draw road
                for n in range(startPos, startPos + show_N_seg):
                    current = lines[n % N]
                    # loop the circut from start to finish = pos - (N * segL if n >= N else 0)
                    current.project(playerX - x, camH, pos - (N * segL if n >= N else 0))
                    x += dx
                    dx += current.curve

                    current.clip = maxy

                    # don't draw "above ground"
                    if current.Y >= maxy:
                        continue
                    maxy = current.Y

                    prev = lines[(n - 1) % N]  # previous line

                    drawQuad(
                        self.window_surface,
                        current.grass_color,
                        0,
                        prev.Y,
                        WINDOW_WIDTH,
                        0,
                        current.Y,
                        WINDOW_WIDTH,
                    )
                    drawQuad(
                        self.window_surface,
                        current.rumble_color,
                        prev.X,
                        prev.Y,
                        prev.W * 1.2,
                        current.X,
                        current.Y,
                        current.W * 1.2,
                    )
                    drawQuad(
                        self.window_surface,
                        current.road_color,
                        prev.X,
                        prev.Y,
                        prev.W,
                        current.X,
                        current.Y,
                        current.W,
                    )

                # draw sprites
                for n in range(startPos + show_N_seg, startPos + 1, -1):
                    lines[n % N].drawSprite(self.window_surface)

                draw_car(self.window_surface, out_of_bounds)
                draw_battery(self.window_surface, self.battery_level, self.battery_max)

                draw_distance(self.window_surface, self.distance)

                # Calculate time left
                elapsed_time = time.time() - start_time
                self.time_left = max(self.timer_duration - int(elapsed_time), 0)

                draw_timer(self.window_surface, self.time_left)
                pygame.display.update()

                #print car position
                # print(f"Car position: {playerX}, {playerY}")
                if self.battery_level == 0:
                    # print(f"Car position: {playerX}, {playerY}")
                    self.ret = repair()
                    # self.ret = subprocess.Popen(["python", "./repair.py"])
                    # print(f"|-> Repairing cost {self.ret} seconds")
                    if self.ret is not None:
                        self.battery_level = self.battery_max  # Or some code to reset the game state

                # Pick up Battery
                line_has_battery = lines[startPos % N].battery_pos != None
                if not prev_line_has_battery and line_has_battery:
                    battery_pos = lines[startPos % N].battery_pos
                    battery_abs_pos = map_value(battery_pos, -3, 2, -1900, 1900)
                    if abs (battery_abs_pos - playerX) < 400:
                        self.battery_level = min(self.battery_max, self.battery_level + 500)

                # Collide with tesla
                line_has_tesla = lines[startPos % N].tesla_pos != None
                if not prev_line_has_tesla and line_has_tesla:
                    tesla_pos = lines[startPos % N].tesla_pos
                    tesla_abs_pos = map_value(tesla_pos, -3, 2, -1900, 1900)
                    if abs (tesla_abs_pos - (playerX)) < 500:
                        #show the flame here
                        self.crashed_CD = 5 
                        self.window_surface.blit(self.flame, (WINDOW_WIDTH//2 - 50, WINDOW_HEIGHT//2 - 50))
                        self.battery_level = max(0, self.battery_level - 1000)
                if self.crashed_CD > 0:
                    self.crashed_CD -= 1
                    self.window_surface.blit(self.flame, (WINDOW_WIDTH//2 - 50, WINDOW_HEIGHT//2 - 50))
                if self.battery_level == 0:
                    self.ret = repair()
                    if self.ret is not None:
                        self.battery_level = self.battery_max  # Or some code to reset the game state

                prev_line_has_tesla = line_has_tesla
                prev_line_has_battery = line_has_battery

            pygame.display.update()
            self.clock.tick(60)

            
if __name__ == "__main__":
    game = GameWindow()
    game.run()