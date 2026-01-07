import pygame, math, random
import sys

def main():
    pygame.init()
    screen = pygame.display.set_mode( (0, 0), pygame.FULLSCREEN )
    W, H = screen.get_size()
    clock = pygame.time.Clock()

    GRAVITY = 0.4
    FRICTION = 0.95

    class Node:
        def __init__(self, x, y, pinned=False):
            self.x, self.y = x, y
            self.ox, self.oy = x, y
            self.pinned = pinned
            self.healing_cooldown = 0

    class Link:
        def __init__(self, n1, n2):
            self.n1, self.n2 = n1, n2
            self.rest = math.hypot( n1.x - n2.x, n1.y - n2.y )
            self.active = True

    def create_symbiote():
        nodes, links = [], []
        cols, rows = 25, 20
        sp = 25
        ox = (W - cols * sp) // 2
        for y in range( rows ):
            for x in range( cols ):
                nodes.append( Node( ox + x * sp, 50 + y * sp, y == 0 and x % 2 == 0 ) )
        for y in range( rows ):
            for x in range( cols ):
                if x < cols - 1: links.append( Link( nodes[y * cols + x], nodes[y * cols + x + 1] ) )
                if y < rows - 1: links.append( Link( nodes[y * cols + x], nodes[(y + 1) * cols + x] ) )
        return nodes, links

    nodes, links = create_symbiote()
    drag_node = None

    while True:
        screen.fill( (10, 5, 10) )
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: nodes, links = create_symbiote()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pass
                if event.button == 3:
                    for n in nodes:
                        if math.hypot( n.x - mx, n.y - my ) < 20:
                            drag_node = n
                            break
            if event.type == pygame.MOUSEBUTTONUP:
                drag_node = None

        m_left = pygame.mouse.get_pressed()[0]

        if drag_node: drag_node.x, drag_node.y = mx, my

        for n in nodes:
            if not n.pinned and n != drag_node:
                vx = (n.x - n.ox) * FRICTION
                vy = (n.y - n.oy) * FRICTION
                n.ox, n.oy = n.x, n.y
                n.x += vx
                n.y += vy + GRAVITY
                if n.healing_cooldown > 0: n.healing_cooldown -= 1

        for _ in range( 20 ):
            n1 = random.choice( nodes )
            n2 = random.choice( nodes )
            if n1 != n2 and n1.healing_cooldown == 0 and n2.healing_cooldown == 0:
                d = math.hypot( n1.x - n2.x, n1.y - n2.y )
                if d < 30:
                    exists = False
                    for l in links:
                        if l.active and ((l.n1 == n1 and l.n2 == n2) or (l.n1 == n2 and l.n2 == n1)):
                            exists = True
                            break
                    if not exists:
                        links.append( Link( n1, n2 ) )
                        pygame.draw.circle( screen, (255, 255, 255), (int( n1.x ), int( n1.y )), 10 )
                        n1.healing_cooldown = 60
                        n2.healing_cooldown = 60

        for _ in range( 3 ):
            for l in links:
                if not l.active: continue
                dx = l.n2.x - l.n1.x
                dy = l.n2.y - l.n1.y
                d = math.hypot( dx, dy ) + 0.001

                if d > l.rest * 2.5 or (
                        m_left and math.hypot( (l.n1.x + l.n2.x) / 2 - mx, (l.n1.y + l.n2.y) / 2 - my ) < 15):
                    l.active = False
                    continue

                diff = (l.rest - d) / d * 0.5
                if not l.n1.pinned and l.n1 != drag_node: l.n1.x -= dx * diff; l.n1.y -= dy * diff
                if not l.n2.pinned and l.n2 != drag_node: l.n2.x += dx * diff; l.n2.y += dy * diff

        for l in links:
            if l.active:
                pygame.draw.line( screen, (50, 200, 80), (l.n1.x, l.n1.y), (l.n2.x, l.n2.y), 2 )

        pygame.display.flip()
        clock.tick( 60 )

if __name__ == "__main__":
    main()