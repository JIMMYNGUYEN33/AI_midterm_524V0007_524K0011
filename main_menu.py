import pygame
import sys
import demo_single_agents
import demo_competitive

# --- BẢNG MÀU TƯƠI SÁNG ---
BG_COLOR = (135, 206, 235)       
BTN_NORM = (41, 128, 185)      
BTN_HOVER = (93, 173, 226)
BTN_GREEN_NORM = (46, 204, 113)
BTN_GREEN_HOVER = (88, 214, 141)
BTN_ORANGE_NORM = (243, 156, 18)
BTN_ORANGE_HOVER = (248, 196, 113)
BTN_QUIT_NORM = (231, 76, 60)    
BTN_QUIT_HOVER = (241, 148, 138)
TITLE_COLOR = (255, 215, 0)      
TEXT_COLOR = (255, 255, 255)

def draw_text_with_shadow(surface, text, font, color, x, y):
    shadow = font.render(text, True, (40, 40, 40))
    shadow_rect = shadow.get_rect(center=(x + 4, y + 4))
    surface.blit(shadow, shadow_rect)
    
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=(x, y))
    surface.blit(text_surf, text_rect)

class Button:
    def __init__(self, center_x, center_y, width, height, text, norm_color, hov_color, font):
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (center_x, center_y)
        self.text = text
        self.norm_color = norm_color
        self.hov_color = hov_color
        self.font = font

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.rect.collidepoint(mouse_pos)
        color = self.hov_color if is_hover else self.norm_color

        pygame.draw.rect(surface, (20, 20, 20), self.rect.move(5, 5), border_radius=20)
        pygame.draw.rect(surface, color, self.rect, border_radius=20)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, width=4, border_radius=20)
        
        draw_text_with_shadow(surface, self.text, self.font, TEXT_COLOR, self.rect.centerx, self.rect.centery)
        return is_hover

def main_menu():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Sokoban AI Challenge")
    
    WIDTH, HEIGHT = screen.get_width(), screen.get_height()
    
    font_title = pygame.font.SysFont("Impact", 85) 
    font_btn = pygame.font.SysFont("Arial", 32, bold=True)
    font_hint = pygame.font.SysFont("Arial", 20, bold=True)
    font_input = pygame.font.SysFont("Impact", 60)

    btn_w, btn_h = 500, 80
    cx = WIDTH // 2
    
    # Các nút ở Màn hình CHÍNH
    btn_main_single = Button(cx, HEIGHT // 2 - 60, btn_w, btn_h, "1. SINGLE AGENT", BTN_GREEN_NORM, BTN_GREEN_HOVER, font_btn)
    btn_main_comp   = Button(cx, HEIGHT // 2 + 60, btn_w, btn_h, "2. COMPETITIVE", BTN_ORANGE_NORM, BTN_ORANGE_HOVER, font_btn)
    btn_main_exit   = Button(cx, HEIGHT // 2 + 180, btn_w, btn_h, "EXIT GAME", BTN_QUIT_NORM, BTN_QUIT_HOVER, font_btn)

    # Các nút ở Màn hình SINGLE
    btn_alg_astar = Button(cx, HEIGHT // 2 - 60, btn_w, btn_h, "PLAY WITH A*", BTN_NORM, BTN_HOVER, font_btn)
    btn_alg_ucs   = Button(cx, HEIGHT // 2 + 60, btn_w, btn_h, "PLAY WITH UCS", BTN_NORM, BTN_HOVER, font_btn)
    btn_back_s    = Button(cx, HEIGHT // 2 + 180, btn_w, btn_h, "BACK", BTN_QUIT_NORM, BTN_QUIT_HOVER, font_btn)

    # Các nút ở Màn hình COMPETITIVE
    btn_start_comp = Button(cx, HEIGHT // 2 + 80, btn_w, btn_h, "START BATTLE", BTN_ORANGE_NORM, BTN_ORANGE_HOVER, font_btn)
    btn_back_c     = Button(cx, HEIGHT // 2 + 180, btn_w, btn_h, "BACK", BTN_QUIT_NORM, BTN_QUIT_HOVER, font_btn)

    # Khung nhập liệu (Input Box) cho số bước n
    input_rect = pygame.Rect(0, 0, 200, 80)
    input_rect.center = (cx, HEIGHT // 2 - 20)
    input_text = "30" # Giá trị mặc định

    # Máy trạng thái (State Machine)
    state = "MAIN"  # MAIN | SINGLE_MENU | COMP_MENU
    
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(BG_COLOR)
        pygame.draw.circle(screen, (160, 220, 245), (WIDTH // 6, HEIGHT // 4), 180)
        pygame.draw.circle(screen, (160, 220, 245), (WIDTH - WIDTH // 6, HEIGHT // 1.5), 250)

        # Hướng dẫn ESC
        hint_surf = font_hint.render("Press [ESC] to Exit", True, (60, 60, 60))
        screen.blit(hint_surf, (WIDTH - hint_surf.get_width() - 25, 20))

        mouse_click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state == "MAIN": running = False
                    else: state = "MAIN"
                
                # Bắt sự kiện gõ phím khi đang ở màn hình nhập bước
                elif state == "COMP_MENU":
                    if event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.unicode.isnumeric():
                        if len(input_text) < 3: # Giới hạn nhập tối đa 999 bước
                            input_text += event.unicode
                            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_click = True

        # ================= VẼ GIAO DIỆN THEO STATE ================= #
        if state == "MAIN":
            draw_text_with_shadow(screen, "SOKOBAN AI CHALLENGE", font_title, TITLE_COLOR, cx, HEIGHT // 4)
            
            if btn_main_single.draw(screen) and mouse_click:
                state = "SINGLE_MENU"
            elif btn_main_comp.draw(screen) and mouse_click:
                state = "COMP_MENU"
            elif btn_main_exit.draw(screen) and mouse_click:
                running = False

        elif state == "SINGLE_MENU":
            draw_text_with_shadow(screen, "SELECT ALGORITHM", font_title, TITLE_COLOR, cx, HEIGHT // 4)
            
            if btn_alg_astar.draw(screen) and mouse_click:
                demo_single_agents.run_game("A*")
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            elif btn_alg_ucs.draw(screen) and mouse_click:
                demo_single_agents.run_game("UCS")
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            elif btn_back_s.draw(screen) and mouse_click:
                state = "MAIN"

        elif state == "COMP_MENU":
            draw_text_with_shadow(screen, "COMPETITIVE SETTINGS", font_title, TITLE_COLOR, cx, HEIGHT // 4 - 30)
            
            # Label hướng dẫn
            lbl_surf = font_btn.render("ENTER MAX STEPS:", True, (40, 40, 40))
            screen.blit(lbl_surf, lbl_surf.get_rect(center=(cx, HEIGHT // 2 - 100)))

            # Vẽ Box nhập liệu
            pygame.draw.rect(screen, (20, 20, 20), input_rect.move(4, 4), border_radius=12)
            pygame.draw.rect(screen, (255, 255, 255), input_rect, border_radius=12)
            pygame.draw.rect(screen, (100, 100, 100), input_rect, width=4, border_radius=12)
            
            # Hiển thị số đang gõ
            txt_surface = font_input.render(input_text + "|", True, (41, 128, 185)) # Ký tự | giả làm con trỏ nhấp nháy
            screen.blit(txt_surface, txt_surface.get_rect(center=input_rect.center))

            if btn_start_comp.draw(screen) and mouse_click:
                # Nếu người dùng xóa hết để trống, lấy mặc định là 25
                final_steps = int(input_text) if input_text.strip() != "" else 25 
                demo_competitive.run_game(final_steps)
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            elif btn_back_c.draw(screen) and mouse_click:
                state = "MAIN"

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_menu()