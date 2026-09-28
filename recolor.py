import pygame

pygame.init()

# 1. Đọc ảnh Agent 1 (Màu xanh)
img = pygame.image.load("assets/agent1.png")
new_img = img.copy()

# 2. Quét toàn bộ điểm ảnh (pixel)
for x in range(new_img.get_width()):
    for y in range(new_img.get_height()):
        r, g, b, a = new_img.get_at((x, y))
        
        # Nếu phát hiện pixel màu xanh lá (Green trội hơn Red và Blue)
        if g > r + 20 and g > b + 20:
            # Hoán đổi giá trị Green và Red để biến thành màu đỏ
            new_img.set_at((x, y), (g, r, b, a))

# 3. Lưu thành file mới cho Agent 2
pygame.image.save(new_img, "assets/agent2.png")
print("[+] Đã tự động tạo xong file assets/agent2.png (Màu đỏ)!")

pygame.quit()