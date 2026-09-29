import sys
import ctypes
try:
    import sdl2
except ImportError:
    print("Instale o pysdl2: pip install pysdl2 pysdl2-dll")
    sys.exit(1)

class Canvas:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
        self.window = sdl2.SDL_CreateWindow(
            b"Computacao Grafica do Zero",
            sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED,
            width, height, sdl2.SDL_WINDOW_SHOWN
        )
        self.renderer = sdl2.SDL_CreateRenderer(self.window, -1, sdl2.SDL_RENDERER_ACCELERATED)

        self.texture = sdl2.SDL_CreateTexture(
            self.renderer,
            sdl2.SDL_PIXELFORMAT_RGBA32,
            sdl2.SDL_TEXTUREACCESS_STREAMING,
            width, height
        )
        self.framebuffer = bytearray(width * height * 4)

    def pixel(self, x, y, r, g, b):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return

        indice = (y * self.width + x) * 4

        self.framebuffer[indice] = r
        self.framebuffer[indice + 1] = g
        self.framebuffer[indice + 2] = b
        self.framebuffer[indice + 3] = 255

    def linha_ingenua(self, x0, y0, x1, y1):
        if x0 == x1:
            for y in range(min(y0, y1), max(y0, y1) + 1):
                self.pixel(x0, y, 255, 255, 255)
            return

        m = (y1 - y0) / (x1 - x0)

        b = y0 - m * x0

        for x in range(x0, x1 + 1):
            y = m * x + b

            y = round(y)

            self.pixel(x, y, 255, 255, 255)

    def linha_dda(self, x0, y0, x1, y1):
        dx = x1 - x0
        dy = y1 - y0

        if x0 == x1 and y0 == y1:
            self.pixel(x0, y0, 255, 255, 255)
            return

        passos = max(abs(dx), abs(dy))

        x_inc = dx / passos
        y_inc = dy / passos

        x_atual = float(x0)
        y_atual = float(y0)

        for _ in range(passos + 1):
            self.pixel(
                round(x_atual),
                round(y_atual),
                255, 255, 255
            )

            x_atual += x_inc
            y_atual += y_inc

    def linha_bresenham_simples(self, x0, y0, x1, y1):
        dx = x1 - x0
        dy = y1 - y0

        P = 2 * dy - dx

        y = y0

        for x in range(x0, x1 + 1):

            self.pixel(x, y, 255, 255, 255)

            if P >= 0:
                y += 1
                P -= 2 * dx

            P += 2 * dy

    def linha(self, x0, y0, x1, y1, r, g, b):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)

        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1

        err = dx - dy

        while True:
            self.pixel(x0, y0, r, g, b)

            if x0 == x1 and y0 == y1:
                break

            e2 = 2 * err

            if e2 >= -dy:
                err -= dy
                x0 += sx

            if e2 <= dx:
                err += dx
                y0 += sy

    def triangulo(self, x0, y0, x1, y1, x2, y2, r, g, b):
        self.linha(x0, y0, x1, y1, r, g, b)
        self.linha(x1, y1, x2, y2, r, g, b)
        self.linha(x2, y2, x0, y0, r, g, b)

    def retangulo(self, x, y, largura, altura, r, g, b):
        x1 = x + largura - 1
        y1 = y + altura - 1

        self.linha(x, y, x1, y, r, g, b)
        self.linha(x1, y, x1, y1, r, g, b)
        self.linha(x1, y1, x, y1, r, g, b)
        self.linha(x, y1, x, y, r, g, b)

    def retangulo_preenchido(self, x, y, largura, altura, r, g, b):
        for py in range(y, y + altura):
            for px in range(x, x + largura):
                self.pixel(px, py, r, g, b)

    def triangulo_preenchido(self, x0, y0, x1, y1, x2, y2, r, g, b):
        xmin = min(x0, x1, x2)
        xmax = max(x0, x1, x2)

        ymin = min(y0, y1, y2)
        ymax = max(y0, y1, y2)

        for y in range(ymin, ymax + 1):
            for x in range(xmin, xmax + 1):

                w1 = (x - x0) * (y1 - y0) - (y - y0) * (x1 - x0)
                w2 = (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)
                w3 = (x - x2) * (y0 - y2) - (y - y2) * (x0 - x2)

                if ((w1 >= 0 and w2 >= 0 and w3 >= 0) or
                    (w1 <= 0 and w2 <= 0 and w3 <= 0)):

                    self.pixel(x, y, r, g, b)

    def update(self):
        sdl2.SDL_UpdateTexture(
            self.texture,
            None,
            (ctypes.c_ubyte * len(self.framebuffer)).from_buffer(self.framebuffer),
            self.width * 4
        )
        sdl2.SDL_RenderClear(self.renderer)
        sdl2.SDL_RenderCopy(self.renderer, self.texture, None, None)
        sdl2.SDL_RenderPresent(self.renderer)

    def wait_for_close(self):
        running = True
        event = sdl2.SDL_Event()
        while running:
            while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
                if event.type == sdl2.SDL_QUIT:
                    running = False
            self.update()

        sdl2.SDL_DestroyTexture(self.texture)
        sdl2.SDL_DestroyRenderer(self.renderer)
        sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_Quit()

if __name__ == "__main__":
    screen = Canvas(800, 600)

    screen.retangulo_preenchido(
        0, 0,
        screen.width, screen.height,
        135, 206, 235
    )

    screen.retangulo_preenchido(
        300, 300,
        200, 200,
        255, 215, 0
    )

    screen.retangulo_preenchido(
        375, 400,
        50, 100,
        139, 69, 19
    )

    screen.triangulo_preenchido(
        300, 300,
        500, 300,
        400, 150,
        220, 20, 60
    )

    screen.wait_for_close()