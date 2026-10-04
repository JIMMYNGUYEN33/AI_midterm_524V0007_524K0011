import pygame

pygame.init()

img = pygame.image.load("assets/agent1.png")
new_img = img.copy()

for x in range(new_img.get_width()):
    for y in range(new_img.get_height()):
        r, g, b, a = new_img.get_at((x, y))
        
        if g > r + 20 and g > b + 20:
            new_img.set_at((x, y), (g, r, b, a))

pygame.image.save(new_img, "assets/agent2.png")
print("[+] Đã tự động tạo xong file assets/agent2.png (Màu đỏ)!")

pygame.quit()