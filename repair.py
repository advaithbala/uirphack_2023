import pygame
import sys
import random
import time
import textwrap

#set the env to currrent path
import os
import sys


# Game loop
def repair():
    os.chdir(sys.path[0])
    # print(f"current path: {sys.path[0]}")
    # Initialize Pygame
    pygame.init()
    image_folder = sys.path[0]+'/static/repair/'
    # Set up some constants
    WIDTH, HEIGHT = 1024, 768
    FPS = 60

    # Set up some colors
    RED = (255, 0, 0)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    countdown_time_remaining =3

    # Create the screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    #Font
    # Define the font for the required component title
    required_title_font = pygame.font.SysFont("Arial", 36)

    # Define the font for the score display
    score_font = pygame.font.SysFont("Arial", 30)

    # Countdown and start text font
    countdown_font = pygame.font.SysFont("Arial", 40)

    # Dialogue text font
    dialogue_text_font = pygame.font.SysFont("Arial", 15)

    # Timer font
    timer_font = pygame.font.SysFont("Arial", 30)


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
    time_stamp = None
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

    # Initialize score
    score = 0

    # Set the target score
    target_score = 10

    # Set up timer
    start_time = None
    end_time = None
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
        "Unfortunately",
        # "Your car is damaged",
        "Running out battery caused some damage",
        "But no worries",
        "Let's fix it ASAP",
        "Don't forget the clock is ticking."
    ]

    closing_sentences = [
        "Great!",
        "Now your car works again!",
        "Please drive safe!",
        "Please drive safe!"
    ]

    sentence_index = 0

    # Dialogue window
    dialogue_window_image = pygame.transform.scale(pygame.image.load(image_folder + 'dialogue_window.png'), (200, 150))  # Dialogue window image
    dialogue_window_rect = dialogue_window_image.get_rect(right=mechanism_rect.left - 10, centery=mechanism_rect.centery)
    dialogue_text = dialogue_text_font.render(opening_sentences[0], True, BLACK)
    dialogue_text_rect = dialogue_text.get_rect(center=dialogue_window_rect.center)

    while True:
        # Event loop
        for event in pygame.event.get():
            # if event.type == pygame.QUIT:
                # pygame.quit()
                # sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
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
                            mechanism_leaving = True
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
            font = pygame.font.SysFont("Arial", 15)
            text = font.render(component_titles[i], True, RED)
            screen.blit(text, (pos[0], base+ pos[1]- component_image.get_height()-title_shift))

        # Draw the required component title at the center-top
        
        required_title_text = required_title_font.render(required_title, True, RED)
        required_title_pos = (WIDTH // 2 - required_title_text.get_width() // 2, 10)
        if game_started and not game_ended:
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
            mechanism_rect.x += mechanism_speed
            dialogue_window_rect.x+= mechanism_speed
            dialogue_text_rect.x+= mechanism_speed
            if mechanism_rect.right <= 0:
                mechanism_leaving = False
        elif mechanism_leaving and mechanism_rect.right < 0 and not game_ended:
            mechanism_leaving = False
        elif game_ended and not mechanism_entering and mechanism_rect.right > WIDTH:
            mechanism_rect.x -= mechanism_speed
            dialogue_window_rect.x -= mechanism_speed
        elif game_ended and not mechanism_entering and not mechanism_rect.right > WIDTH:
            mechanism_entering = True

        # else:
        #     mechanism_rect.x = WIDTH 
        if time_stamp is None:
            time_stamp = time.time()
        if not game_started:#count down when the sentence_index equals to the length of the opening_sentences
            if not game_started and sentence_index == len(opening_sentences) and countdown_time_remaining>=1:
                if countdown_start_time is None:
                    countdown_start_time = time.time()
                countdown_time_remaining = countdown_time - int(time.time() - countdown_start_time)
                countdown_text = countdown_font.render(str(countdown_time_remaining), True, BLACK)
                screen.blit(countdown_text, required_title_pos)
                # print(f"countdown_time_remaining: {countdown_time_remaining}")
                if countdown_time_remaining==0:
                    start_time = time.time()
                    game_started = True
        # Draw the dialogue window
        if not game_started or mechanism_leaving or mechanism_entering:
            screen.blit(dialogue_window_image, dialogue_window_rect)
            screen.blit(dialogue_text, dialogue_text_rect)

        # Update dialogue text
        if not game_started and sentence_index < len(opening_sentences):
            # sentence_index += 1
            # print(f'sentence_index: {sentence_index}')
            # use this condition to check if the time is up
            if time.time() - time_stamp >1:
                sentence_index += 1
                time_stamp = time.time()
                # print(f"Opening Sentence {opening_sentences[sentence_index]}")
                if sentence_index < len(opening_sentences):
                    text = textwrap.fill(opening_sentences[sentence_index], 20)
                    text = text.replace('\n', ' ')
                    dialogue_text = dialogue_text_font.render(text, True, BLACK)
                    dialogue_text_rect = dialogue_text.get_rect(center=dialogue_window_rect.center)

        if game_ended and mechanism_entering and sentence_index < len(opening_sentences) + len(closing_sentences):
            # time_stamp = end_time
            if end_time is not None and time.time() - end_time > 1.5:
                end_time = time.time()
                sentence_index += 1
                if sentence_index < len(opening_sentences) + len(closing_sentences):
                    #use textwrap to wrap the text, and set the width of the text to 20
                    text = textwrap.fill(closing_sentences[sentence_index - len(opening_sentences)], 10)
                    text = text.replace('\n', ' ')
                    dialogue_text = dialogue_text_font.render(text, True, BLACK)
                    dialogue_text_rect = dialogue_text.get_rect(center=dialogue_window_rect.center)
                elif sentence_index == len(opening_sentences) + len(closing_sentences):
                    return round(time_taken, 2)
        # Draw the timer at the top right
        if game_started and not game_ended:
            current_time = round(time.time() - start_time, 2)
            timer_text = timer_font.render("Time:", True, WHITE)
            timer_pos = (WIDTH - timer_text.get_width() - 10, 50)
            screen.blit(timer_text, timer_pos)
            timer_text = timer_font.render(str(current_time) + "s", True, WHITE)
            timer_pos = (WIDTH - timer_text.get_width() - 10, 70)
            screen.blit(timer_text, timer_pos)

        # Flip the display
        pygame.display.flip()

        # Cap the frame rate
        pygame.time.Clock().tick(FPS)
