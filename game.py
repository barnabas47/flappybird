import pygame
import sys
import random

# Alap beállítások
FPS = 60

# Színek
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def main_menu(screen, clock):
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 32)
    while True:
        screen.fill(WHITE)
        title = font.render('Flappy Game', True, BLACK)
        start = small_font.render('Játék indítása (SPACE)', True, BLACK)
        quit_ = small_font.render('Kilépés (ESC)', True, BLACK)
        w, h = screen.get_size()
        screen.blit(title, (w//2 - title.get_width()//2, 150))
        screen.blit(start, (w//2 - start.get_width()//2, 300))
        screen.blit(quit_, (w//2 - quit_.get_width()//2, 350))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        clock.tick(FPS)

def main():
    pygame.init()
    SCREEN_WIDTH = 1920
    SCREEN_HEIGHT = 1080
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption('Flappy Game')
    clock = pygame.time.Clock()
    main_menu(screen, clock)

    # Madár, cső és háttérkép betöltése
    bird_img_orig = pygame.image.load("assets/images/bird.png").convert_alpha()
    pipe_img_orig = pygame.image.load("assets/images/pipe.png").convert_alpha()
    try:
        bg_img_orig = pygame.image.load("assets/images/bg.png").convert()
    except:
        bg_img_orig = None

    def get_sizes():
        w, h = screen.get_size()
        # Madár méret: magasság 7%, arányos szélesség
        bird_h = int(h * 0.07)
        bird_w = int(bird_h * (bird_img_orig.get_width() / bird_img_orig.get_height()))
        # Cső: csak szélességben méretezzük, magasság eredeti
        pipe_w = int(w * 0.06)
        pipe_h = pipe_img_orig.get_height()
        return bird_w, bird_h, pipe_w, pipe_h

    def create_pipe(w, h, base_pipe_gap, pipe_width, prev_top_height=None):
        # Mindig az alap pipe_gap-ből indulunk ki
        pipe_gap = base_pipe_gap
        min_top = int(h * 0.06)
        max_top = h - pipe_gap - int(h * 0.12)
        # Alap lyuk pozíció
        top_height = random.randint(min_top, max_top)
        # Ha van előző cső, nézzük a különbséget
        if prev_top_height is not None:
            max_diff = int(h * 0.4)  # max 40% képmagasság
            if abs(top_height - prev_top_height) > max_diff:
                # Csak ehhez a csőhöz növeljük a lyukat
                pipe_gap = int(base_pipe_gap * 1.25)
                min_top2 = max(min_top, prev_top_height - max_diff)
                max_top2 = min(max_top, prev_top_height + max_diff)
                if max_top2 > min_top2:
                    top_height = random.randint(min_top2, max_top2)
        min_pipe_dist = int(pipe_width * 4)  # Minimum távolság: 4x csőszélesség
        max_pipe_dist = int(pipe_width * 6)  # Maximum távolság: 6x csőszélesség
        pipe_dist = random.randint(min_pipe_dist, max_pipe_dist)
        return [w, top_height, pipe_dist, pipe_gap]

    def reset_game():
        w, h = screen.get_size()
        bird_w, bird_h, pipe_width, pipe_height = get_sizes()
        bird_img = pygame.transform.smoothscale(bird_img_orig, (bird_w, bird_h))
        pipe_img = pygame.transform.smoothscale(pipe_img_orig, (pipe_width, pipe_height))
        bird_x = int(w * 0.06)
        ground_height = int(h * 0.055)
        min_y = bird_h // 2 + 10
        max_y = h - ground_height - bird_h - 10
        bird_y = max(min_y, min(h // 2, max_y))
        bird_radius = bird_h // 2
        pipe_gap = int(h * 0.15)
        pipe_vel = max(2, int(w * 0.003))
        first_pipe_x = int(w * 1.0)  # Első cső a képernyő jobb szélén
        first_pipe = create_pipe(first_pipe_x, h, pipe_gap, pipe_width)
        pipes = [first_pipe]
        score = 0
        return bird_x, bird_y, bird_radius, bird_img, pipe_img, pipe_width, pipe_height, pipe_gap, pipe_vel, pipes, score

    bird_x, bird_y, bird_radius, bird_img, pipe_img, pipe_width, pipe_height, pipe_gap, pipe_vel, pipes, score = reset_game()
    bird_vel = 0
    first_frame = 0
    font = pygame.font.SysFont(None, 36)
    running = True
    game_over = False
    best_score = 0
    coins = 0
    try:
        with open("best_score.txt", "r") as f:
            lines = f.readlines()
            if len(lines) >= 2:
                best_score = int(lines[0].strip())
                coins = int(lines[1].strip())
            elif len(lines) == 1:
                best_score = int(lines[0].strip())
                coins = 0
    except:
        best_score = 0
        coins = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and running:
                    bird_vel = -8 * (screen.get_height() / 1080)
                elif event.key == pygame.K_SPACE and game_over:
                    coins += score  # Kör végi pontokat hozzáadjuk a coinhoz
                    bird_x, bird_y, bird_radius, bird_img, pipe_img, pipe_width, pipe_height, pipe_gap, pipe_vel, pipes, score = reset_game()
                    bird_vel = 0
                    first_frame = 0
                    running = True
                    game_over = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                bird_x, bird_y, bird_radius, bird_img, pipe_img, pipe_width, pipe_height, pipe_gap, pipe_vel, pipes, score = reset_game()
                bird_vel = 0
                running = True
                game_over = False

        if running:
            for phase in [0, 1]:
                if phase == 0 and first_frame < 15:
                    first_frame += 1
                elif phase == 0:
                    continue
                bird_vel += 0.5 * (screen.get_height() / 1080)
                bird_y += bird_vel
                if bird_y < 0:
                    bird_y = 0
                    bird_vel = 0
                if bird_y > screen.get_height() - bird_radius:
                    bird_y = screen.get_height() - bird_radius
                    bird_vel = 0
                for pipe in pipes:
                    pipe[0] -= pipe_vel
                # Új cső generálása, figyelve az előző top_height-ot és pipe_gap-et
                last_pipe = pipes[-1]
                last_top = last_pipe[1]
                # Mindig az alap pipe_gap-ből indulunk ki
                if pipes[-1][0] < screen.get_width() - pipes[-1][2]:
                    pipes.append(create_pipe(screen.get_width(), screen.get_height(), pipe_gap, pipe_width, prev_top_height=last_top))
                if pipes[0][0] < -pipe_width:
                    pipes.pop(0)
                    score += 1
                    coins += 1
                if phase == 0:
                    break

            ground_height = int(screen.get_height() * 0.055)
            bird_hitbox_w = int(bird_img.get_width() * 0.7)
            bird_hitbox_h = int(bird_img.get_height() * 0.7)
            bird_rect = pygame.Rect(
                bird_x - bird_hitbox_w // 2,
                int(bird_y) - bird_hitbox_h // 2,
                bird_hitbox_w,
                bird_hitbox_h
            )
            collision = False
            for pipe in pipes:
                pipe_x, top_height, _, curr_gap = pipe if len(pipe) > 3 else (*pipe, pipe_gap)
                top_rect = pygame.Rect(pipe_x, 0, pipe_width, top_height)
                bottom_rect = pygame.Rect(pipe_x, top_height + curr_gap, pipe_width, screen.get_height() - (top_height + curr_gap))
                if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
                    collision = True
                if int(bird_y) + bird_img.get_height() // 2 >= screen.get_height() - ground_height:
                    collision = True
                if int(bird_y) - bird_hitbox_h // 2 <= 0:
                    collision = True
            if collision:
                running = False
                game_over = True
                new_best = False
                if score > best_score:
                    best_score = score
                    new_best = True
                # Always save coins and best_score if either changed
                with open("best_score.txt", "w") as f:
                    f.write(f"{best_score}\n{coins}\n")

        # Háttér és grafika kirajzolása
        w, h = screen.get_size()
        if bg_img_orig:
            bg_img = pygame.transform.smoothscale(bg_img_orig, (w, h))
            screen.blit(bg_img, (0, 0))
        else:
            screen.fill((135, 206, 250))
            pygame.draw.circle(screen, (255, 255, 120), (w-60, 60), 40)
            for cx, cy in [(int(w*0.04), int(h*0.09)), (int(w*0.11), int(h*0.06)), (int(w*0.17), int(h*0.11))]:
                pygame.draw.ellipse(screen, (255,255,255), (cx, cy, int(w*0.03), int(h*0.028)))
                pygame.draw.ellipse(screen, (255,255,255), (cx+int(w*0.01), cy-int(h*0.009), int(w*0.02), int(h*0.025)))
                pygame.draw.ellipse(screen, (255,255,255), (cx-int(w*0.01), cy+int(h*0.009), int(w*0.025), int(h*0.02)))
            ground_height = int(h * 0.055)
            pygame.draw.rect(screen, (110, 180, 60), (0, h-ground_height, w, ground_height))
            pygame.draw.ellipse(screen, (80, 160, 60), (-int(w*0.02), h-ground_height-int(h*0.028), int(w*0.09), int(h*0.07)))
            pygame.draw.ellipse(screen, (90, 170, 70), (int(w*0.115), h-ground_height-int(h*0.018), int(w*0.1), int(h*0.055)))
            for x in range(0, w, max(8, int(w*0.006))):
                pygame.draw.line(screen, (60, 120, 30), (x, h-ground_height+8), (x+2, h-ground_height+18), 2)
        for pipe in pipes:
            pipe_x, top_height, _, curr_gap = pipe if len(pipe) > 3 else (*pipe, pipe_gap)
            # Felső cső: sprite-ot csak szélességben méretezzük, magasság eredeti
            top_pipe_img = pygame.transform.flip(pipe_img, False, True)
            scaled_top = pygame.transform.smoothscale(top_pipe_img, (pipe_width, pipe_img_orig.get_height()))
            # A sprite alja legyen a top_height-nál, tehát y = top_height - sprite_height
            screen.blit(scaled_top, (pipe_x, top_height - pipe_img_orig.get_height()))
            # Alsó cső: sprite-ot csak szélességben méretezzük, magasság eredeti
            scaled_bottom = pygame.transform.smoothscale(pipe_img, (pipe_width, pipe_img_orig.get_height()))
            # A sprite teteje legyen a top_height + curr_gap-nél
            screen.blit(scaled_bottom, (pipe_x, top_height + curr_gap))
        screen.blit(bird_img, (bird_x-bird_img.get_width()//2, int(bird_y)-bird_img.get_height()//2))
        score_surf = font.render(f"Pont: {score}", True, (40,40,40))
        screen.blit(score_surf, (10, 10))
        best_surf = font.render(f"Rekord: {best_score}", True, (40,40,40))
        screen.blit(best_surf, (10, 40))
        coin_surf = font.render(f"Coin: {coins}", True, (218, 165, 32))
        screen.blit(coin_surf, (10, 70))

        if game_over:
            font_big = pygame.font.SysFont(None, 64)
            over_surf = font_big.render("Game Over!", True, (200, 0, 0))
            restart_surf = font.render("Újraindítás: SPACE", True, BLACK)
            quit_surf = font.render("Kilépés: ESC", True, BLACK)
            screen.blit(over_surf, (w//2 - over_surf.get_width()//2, 200))
            screen.blit(restart_surf, (w//2 - restart_surf.get_width()//2, 300))
            screen.blit(quit_surf, (w//2 - quit_surf.get_width()//2, 350))
            pygame.display.flip()
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            bird_x, bird_y, bird_radius, bird_img, pipe_img, pipe_width, pipe_height, pipe_gap, pipe_vel, pipes, score = reset_game()
                            bird_vel = 0
                            first_frame = 0
                            running = True
                            game_over = False
                            waiting = False
                        if event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    main()