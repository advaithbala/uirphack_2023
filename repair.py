import pygame
import sys
import random
import time
import textwrap

# Initialize Pygame
pygame.init()
image_folder = './static/repair/'
# Set up some constants
WIDTH, HEIGHT = 1024, 768
FPS = 60

# Set up some colors
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Load background image
bg_image = pygame.image.load(image_folder + 'factory.png')  # Background image
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

# Load car image
car_image = pygame.image.load(image_folder + 'car.png')  # Car image

# Load component images
size = 80
component_images = [
    pygame.transform.scale(pygame.image.load(image_folder + 'battery.png'), (size, size)),  # Battery component
    pygame.transform.scale(pygame.image.load(image_folder + 'motor.png'), (size, size)),  # Motor component
    pygame.transform.scale(pygame.image.load(image_folder + 'chair.png'), (size, size)),  # Seat component
    pygame.transform.scale(pygame.image.load(image_folder + 'tire.png'), (size, size)),  # Chair component
    pygame.transform.scale(pygame.image.load(image_folder + 'headlight.png'), (size, size))  # Headlight component
]

base = component_images[0].get_height()
title_shift = 23
component_shift = 20
# Define the titles of the components
component_titles = [
    "Battery",
    "Motor",
    "Seat",
    "Tire",
    "Headlight"
]

# Initialize car status
car_status = 100

# Initialize dragging status
dragging = None

# Define the required component title
required_title = random.choice(component_titles)  # Randomly select a required component title

# Define the font for the required component title
required_title_font = pygame.font.Font(None, 36)

# Define the font for the score display
score_font = pygame.font.Font(None, 30)

# Initialize score
score = 0

# Set the target score
target_score = 50

# Set up timer
start_time = None
end_time = None
timer_font = pygame.font.Font(None, 30)
countdown_time = 3
countdown_start_time = None
game_started = False
game_ended = False
mechanism_leaving = False
mechanism_entering = False

# Load mechanism image
# mechanism_image = pygame.image.load(image_folder + 'mechanism.png')  # Mechanism image
#resize the img to 130,130
mechanism_image = pygame.transform.scale(pygame.image.load(image_folder + 'mechanism.png'), (130, 130))  # Mechanism image
mechanism_rect = mechanism_image.get_rect(right=WIDTH, centery=HEIGHT // 2)
mechanism_speed = 5
opening_sentences = [
    "Unfortunately, ",
    "Your car is damaged.",
    "But no worries",
    "Let's fix it ASAP.",
    "Don't forget the clock is ticking."
]

closing_sentences = [
    "Great!",
    "Now your car is back to the track again!",
    "Please drive safe!"
]

sentence_index = 0

# Countdown and start text font
countdown_font = pygame.font.Font(None, 60)

# Dialogue window
dialogue_window_image = pygame.transform.scale(pygame.image.load(image_folder + 'dialogue_window.png'), (200, 150))  # Dialogue window image
dialogue_window_rect = dialogue_window_image.get_rect(right=mechanism_rect.left - 10, centery=mechanism_rect.centery)
dialogue_text_font = pygame.font.Font(None, 24)
dialogue_text = dialogue_text_font.render(opening_sentences[0], True, BLACK)
dialogue_text_rect = dialogue_text.get_rect(center=dialogue_window_rect.center)

# Game loop
while True:
    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for i, component_image in enumerate(component_images):
                if pygame.Rect(10, 10 + i * 110, component_image.get_width(), component_image.get_height()).collidepoint(
                        event.pos):
                    dragging = i
                    break
        elif event.type == pygame.MOUSEBUTTONUP:
            if dragging is not None and car_rect.collidepoint(event.pos):
                if component_titles[dragging] == required_title:
                    score += 10
                    print("Correct component dragged!")  # Replace with your desired action
                    required_title = random.choice(component_titles)  # Randomly select a new required component title
                    if score >= target_score:
                        end_time = time.time()
                        time_taken = end_time - start_time
                        print("Congratulations! You completed the task in", round(time_taken, 2), "seconds.")
                        mechanism_entering = True
                        game_ended = True
            dragging = None

    # Draw the background
    screen.blit(bg_image, (0, 0))

    # Draw the white mask
    mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    mask.fill((255, 255, 255, 128))  # White color with 50% transparency
    screen.blit(mask, (0, 0))

    # Draw the white column behind the components
    pygame.draw.rect(screen, WHITE, (0, 0, 200, HEIGHT))

    # Draw the car
    car_rect = car_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(car_image, car_rect)

    # Draw the components with titles
    for i, component_image in enumerate(component_images):
        if dragging == i:
            pos = pygame.mouse.get_pos()
        else:
            pos = (10, 10 + i * 110+component_shift)  # Adjust the vertical spacing to accommodate the larger component size
        screen.blit(component_image, pos)

        # Draw component title
        font = pygame.font.Font(None, 30)
        text = font.render(component_titles[i], True, RED)
        screen.blit(text, (pos[0], base+ pos[1]- component_image.get_height()-title_shift))

    # Draw the required component title at the center-top
    
    required_title_text = required_title_font.render(required_title, True, RED)
    required_title_pos = (WIDTH // 2 - required_title_text.get_width() // 2, 10)
    if game_started:
        screen.blit(required_title_text, required_title_pos)

    # Draw the score at the top right
    score_text = score_font.render("Score: " + str(score), True, WHITE)
    score_pos = (WIDTH - score_text.get_width() - 10, 10)
    screen.blit(score_text, score_pos)

    
    # Mechanism sliding animation
    screen.blit(mechanism_image, mechanism_rect)
    if not game_started and mechanism_rect.right > WIDTH - 10:
        mechanism_rect.x -= mechanism_speed
    elif game_started and not mechanism_leaving and mechanism_rect.right > 0:
        mechanism_leaving = True
    elif mechanism_leaving and not game_ended:
        mechanism_rect.x -= mechanism_speed
        dialogue_window_rect.x -= mechanism_speed
        if mechanism_rect.right <= 0:
            mechanism_leaving = False
    elif game_ended and mechanism_rect.right < WIDTH:
        mechanism_rect.x += mechanism_speed

    if not game_started:
        if countdown_start_time is None:
            countdown_start_time = time.time()
        countdown_time_remaining = countdown_time - int(time.time() - countdown_start_time)
        if countdown_time_remaining > 0:
            countdown_text = countdown_font.render(str(countdown_time_remaining), True, BLACK)
            countdown_text_pos = (
            WIDTH // 2 - countdown_text.get_width() // 2, HEIGHT // 2 - countdown_text.get_height() // 2)
            screen.blit(countdown_text, required_title_pos)
        elif sentence_index == len(opening_sentences):
            game_started = True
            start_time = time.time()
            start_text = countdown_font.render("Start!", True, WHITE)
            start_text_pos = (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 - start_text.get_height() // 2)
            screen.blit(start_text, start_text_pos)

    # Draw the dialogue window
    if not game_started or mechanism_leaving or mechanism_entering:
        screen.blit(dialogue_window_image, dialogue_window_rect)
        screen.blit(dialogue_text, dialogue_text_rect)

    # Update dialogue text
    if not game_started and sentence_index < len(opening_sentences):
        print(f'sentence_index: {sentence_index}')
        # use this condition to check if the time is up
        if time.time() - countdown_start_time > sentence_index + 1:
            sentence_index += 1
            # print(f"Opening Sentence {opening_sentences[sentence_index]}")
            if sentence_index < len(opening_sentences):
                text = textwrap.fill(opening_sentences[sentence_index], 20)
                dialogue_text = dialogue_text_font.render(text, True, BLACK)
                dialogue_text_rect = dialogue_text.get_rect(center=dialogue_window_rect.center)

    if game_ended and mechanism_entering and sentence_index < len(opening_sentences) + len(closing_sentences):
        if end_time is not None and time.time() - end_time > sentence_index - len(opening_sentences) + 1:
            sentence_index += 1
            if sentence_index < len(opening_sentences) + len(closing_sentences):
                #use textwrap to wrap the text, and set the width of the text to 20
                text = textwrap.fill(closing_sentences[sentence_index - len(opening_sentences)], 10)
                dialogue_text = dialogue_text_font.render(text, True, BLACK)
                dialogue_text_rect = dialogue_text.get_rect(center=dialogue_window_rect.center)
            elif sentence_index == len(opening_sentences) + len(closing_sentences):
                pygame.quit()
                sys.exit()


    # Draw the timer at the top right
    if game_started and not game_ended:
        current_time = round(time.time() - start_time, 2)
        timer_text = timer_font.render("Time: \n" + str(current_time) + "s", True, WHITE)
        timer_pos = (WIDTH - timer_text.get_width() - 10, 50)
        screen.blit(timer_text, timer_pos)

    # Flip the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(FPS)