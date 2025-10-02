"""Lightweight pygame-based visualization helpers.

This module exposes global functions (`init`, `frontier`, `visit`,
`draw_path_segment`, `finish`) used by solvers to stream their
progress. If pygame isn't available or visualization is disabled,
all functions become no-ops so normal runs are unaffected.
"""

try:
    import pygame
except Exception:
    pygame = None

# Simple global visualizer with no-ops if pygame is unavailable
class _NoOpVisualizer:
    def init(self, im, scale_max=1000):
        return self
    def frontier(self, pos):
        pass
    def visit(self, pos):
        pass
    def draw_path_segment(self, a, b):
        pass
    def pump(self):
        pass
    def finish(self):
        pass


class _PygameVisualizer:
    def __init__(self):
        self.screen = None
        self.surface = None
        self.scale = 1
        self.running = False

    def init(self, im, scale_max=800):
        if pygame is None:
            return _NoOpVisualizer()

        width, height = im.size
        # compute integer scale to fit within scale_max
        # scale up small images to fit up to scale_max on the longer side
        longest = max(width, height)
        scale = max(1, scale_max // longest) if longest > 0 else 1
        self.scale = scale

        pygame.init()
        self.surface = pygame.Surface((width, height))
        # Load grayscale into surface (white=paths, black=walls)
        pixels = im.convert('L').load()
        for y in range(height):
            for x in range(width):
                v = pixels[x, y]
                self.surface.set_at((x, y), (v, v, v))

        self.screen = pygame.display.set_mode((width * scale, height * scale))
        pygame.display.set_caption('Maze Visualization')
        self.running = True
        self._blit()
        return self

    def _blit(self):
        if pygame is None:
            return
        if self.scale == 1:
            scaled = self.surface
        else:
            scaled = pygame.transform.scale(self.surface, (self.surface.get_width() * self.scale, self.surface.get_height() * self.scale))
        self.screen.blit(scaled, (0, 0))
        pygame.display.flip()

    def _handle_events(self):
        if pygame is None:
            return
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def _set_px(self, pos, color):
        if pygame is None or not self.running:
            return
        y, x = pos
        # guard bounds
        if 0 <= x < self.surface.get_width() and 0 <= y < self.surface.get_height():
            self.surface.set_at((x, y), color)

    def frontier(self, pos):
        # cyan for frontier
        self._set_px(pos, (0, 200, 200))
        self.pump()

    def visit(self, pos):
        # orange for visited (explored)
        self._set_px(pos, (255, 140, 0))
        self.pump()

    def draw_path_segment(self, a, b):
        # magenta for final path
        ay, ax = a
        by, bx = b
        if ay == by:
            # horizontal
            x0, x1 = (ax, bx) if ax <= bx else (bx, ax)
            for x in range(x0, x1 + 1):
                self._set_px((ay, x), (255, 0, 200))
        elif ax == bx:
            # vertical
            y0, y1 = (ay, by) if ay <= by else (by, ay)
            for y in range(y0, y1 + 1):
                self._set_px((y, ax), (255, 0, 200))
        self.pump()

    def pump(self):
        # pump events and update screen
        if pygame is None or not self.running:
            return
        self._handle_events()
        self._blit()

    def finish(self):
        if pygame is None:
            return
        # keep window open until closed by user
        while self.running:
            self._handle_events()
            pygame.time.wait(50)
        pygame.quit()


# Singleton-like helper
_visualizer = _NoOpVisualizer()

def init(im):
    global _visualizer
    if pygame is None:
        _visualizer = _NoOpVisualizer()
        return _visualizer
    _visualizer = _PygameVisualizer().init(im)
    return _visualizer

def frontier(pos):
    _visualizer.frontier(pos)

def visit(pos):
    _visualizer.visit(pos)

def draw_path_segment(a, b):
    _visualizer.draw_path_segment(a, b)

def finish():
    _visualizer.finish()


