import math
from tkinter import Canvas, Tk, font, ALL, SW, mainloop
import matrix


class VirtualCamera:
    SPEED = 0.05
    WIDTH = 640.0
    HEIGHT = 480.0

    def __init__(self):
        # Tworzymy okno i płótno
        self.tk = self.createWindow()
        self.graph = Canvas(self.tk, width=VirtualCamera.WIDTH, height=VirtualCamera.HEIGHT, background='gray')
        self.graph.pack()
        self.fnt = font.Font(family='Verdana', size=12, weight='bold')

        # Parametry szcześcianów
        self.cubes = self.getCubes()

        # Łączymy wektory w ściany
        self.cube_faces = [(0, 1, 2, 3), (1, 5, 6, 2), (5, 4, 7, 6), (4, 0, 3, 7), (0, 4, 5, 1), (3, 2, 6, 7)]
        self.cls = ['orange', 'blue', 'green', 'cyan', 'white', 'purple']

        # Kąty kamery: phi(x), theta(y), psi(z)
        self.ang = [0.0, 0.0, 0.0]

        # Translacja kamery
        self.translation = [0.0, 0.0, 2.0]
        self.zoom = 1.0

        # Macierz: skalowania
        self.scale_matrix = matrix.Matrix(4, 4)
        self.scale_matrix[(0, 0)] = self.zoom
        self.scale_matrix[(1, 1)] = self.zoom
        self.scale_matrix[(2, 2)] = self.zoom

        # Macierz: pochylenia
        self.shear_matrix = matrix.Matrix(4, 4)

        # Macierz: obrotu
        self.rotate_x_matrix = matrix.Matrix(4, 4)
        self.rotate_y_matrix = matrix.Matrix(4, 4)
        self.rotate_z_matrix = matrix.Matrix(4, 4)
        self.rotate_matrix = self.rotate_x_matrix * self.rotate_y_matrix * self.rotate_z_matrix

        # Macierz: translacji
        self.translation_matrix = matrix.Matrix(4, 4)
        self.translation_matrix[(0, 3)] = self.translation[0]
        self.translation_matrix[(1, 3)] = self.translation[1]
        self.translation_matrix[(2, 3)] = self.translation[2]

        # macierz transformacji
        self.transformation_matrix = \
            self.scale_matrix * self.shear_matrix * self.rotate_matrix * self.translation_matrix

        # Macierz: rzutowania
        self.projection_matrix = matrix.Matrix(4, 4)
        fov = 60.0  # Field of View: ile ekranu widać
        zfar = 100.0
        znear = 0.1
        S = 1 / (math.tan(math.radians(fov / 2)))
        self.projection_matrix[(0, 0)] = S / (VirtualCamera.WIDTH / VirtualCamera.HEIGHT)
        self.projection_matrix[(1, 1)] = S
        self.projection_matrix[(2, 2)] = (zfar + znear) / (znear - zfar)
        self.projection_matrix[(3, 2)] = -1.0
        self.projection_matrix[(2, 3)] = 2 * (zfar * znear) / (znear - zfar)

        # przekształcenie do coordynatów na ekranie
        self.to_screen_matrix = matrix.Matrix(4, 4)
        self.to_screen_matrix[(0, 0)] = VirtualCamera.WIDTH / 4
        self.to_screen_matrix[(1, 1)] = -VirtualCamera.HEIGHT / 2
        self.to_screen_matrix[(0, 3)] = VirtualCamera.WIDTH / 2
        self.to_screen_matrix[(1, 3)] = VirtualCamera.HEIGHT / 2

        # obsługa myszki i klawiatury
        self.tk.bind("<Key>", self.key_callback)
        self.tk.bind("<MouseWheel>", self.mousewheel_callback)

        self.update()
        mainloop()

    @staticmethod
    def createWindow():
        tk = Tk()
        tk.resizable(False, False)
        tk.title('Projekt GKiW')
        tk.geometry('%dx%d' % (VirtualCamera.WIDTH, VirtualCamera.HEIGHT))
        return tk

    @staticmethod
    def getCubes():
        """
        Generuje listę sześcianów z których każdy składa się z listry wektorów.
        Ustala listę wzorcową wektorów i listy dla wielokątów generuję przesuwając wektory z listy wzorcowej.
        :return:
        """
        pattern_vectors_cube = [
            matrix.Vector3D(-0.5, 0.5, -0.5),
            matrix.Vector3D(0.5, 0.5, -0.5),
            matrix.Vector3D(0.5, -0.5, -0.5),
            matrix.Vector3D(-0.5, -0.5, -0.5),
            matrix.Vector3D(-0.5, 0.5, 0.5),
            matrix.Vector3D(0.5, 0.5, 0.5),
            matrix.Vector3D(0.5, -0.5, 0.5),
            matrix.Vector3D(-0.5, -0.5, 0.5)
        ]

        return [
            [v + matrix.Vector3D(-1, 0, 0) for v in pattern_vectors_cube],
            [v + matrix.Vector3D(1, 0, 0) for v in pattern_vectors_cube],
            [v + matrix.Vector3D(-1, 0, -2) for v in pattern_vectors_cube],
            [v + matrix.Vector3D(1, 0, -2) for v in pattern_vectors_cube]
        ]

    def update(self):
        self.graph.delete(ALL)

        self.rotate_x_matrix[(1, 1)] = math.cos(math.radians(360.0 - self.ang[0]))
        self.rotate_x_matrix[(1, 2)] = -math.sin(math.radians(360.0 - self.ang[0]))
        self.rotate_x_matrix[(2, 1)] = math.sin(math.radians(360.0 - self.ang[0]))
        self.rotate_x_matrix[(2, 2)] = math.cos(math.radians(360.0 - self.ang[0]))

        self.rotate_y_matrix[(0, 0)] = math.cos(math.radians(360.0 - self.ang[1]))
        self.rotate_y_matrix[(0, 2)] = math.sin(math.radians(360.0 - self.ang[1]))
        self.rotate_y_matrix[(2, 0)] = -math.sin(math.radians(360.0 - self.ang[1]))
        self.rotate_y_matrix[(2, 2)] = math.cos(math.radians(360.0 - self.ang[1]))

        self.rotate_z_matrix[(0, 0)] = math.cos(math.radians(360.0 - self.ang[2]))
        self.rotate_z_matrix[(0, 1)] = -math.sin(math.radians(360.0 - self.ang[2]))
        self.rotate_z_matrix[(1, 0)] = math.sin(math.radians(360.0 - self.ang[2]))
        self.rotate_z_matrix[(1, 1)] = math.cos(math.radians(360.0 - self.ang[2]))

        self.rotate_matrix = self.rotate_x_matrix * self.rotate_y_matrix * self.rotate_z_matrix

        self.translation_matrix[(0, 3)] = -self.translation[0]
        self.translation_matrix[(1, 3)] = -self.translation[1]
        self.translation_matrix[(2, 3)] = -self.translation[2]

        self.scale_matrix[(0, 0)] = self.zoom
        self.scale_matrix[(1, 1)] = self.zoom
        self.scale_matrix[(2, 2)] = self.zoom

        self.transformation_matrix = \
            self.scale_matrix * self.shear_matrix * self.rotate_matrix * self.translation_matrix

        # przygotowuje koordynaty widocznych ścian do narysowania, zwraca także dystans do kamery
        polys_to_draw = [cube for c in self.cubes for cube in self.preparePolygon(c)]

        # algorytm malarza - rysuje wielkoąty zgodnie z odległością do kamery
        polys_to_draw.sort(key=lambda ptd: ptd['distance'], reverse=True)  # sortowanie po odległości
        for poly_to_draw in polys_to_draw:
            self.graph.create_polygon(*poly_to_draw['poly2d'], fill=poly_to_draw['cls'])

        self.drawScreenInfo()

    def drawScreenInfo(self):
        coords_info = 'x: {}, y: {}, z:{}'.format(
            round(self.translation[0], 2),
            round(self.translation[1], 2),
            round(self.translation[2], 2)
        )
        rot_info = 'x_rotation: {}, y_rotation: {}, z_rotation: {}'.format(
            self.ang[0], self.ang[1], self.ang[2]
        )
        zoom_info = 'scaling (zoom): {}'.format(round(self.zoom, 2))

        self.graph.create_text(10, VirtualCamera.HEIGHT - 10, text=coords_info, fill='white', anchor=SW, font=self.fnt)
        self.graph.create_text(10, VirtualCamera.HEIGHT - 30, text=rot_info, fill='white', anchor=SW, font=self.fnt)
        self.graph.create_text(10, VirtualCamera.HEIGHT - 50, text=zoom_info, fill='white', anchor=SW, font=self.fnt)

        controls_info = 'Use arrows for move. \nPress D for down or U for up. \nUse mousewheel to zoom.'
        self.graph.create_text(10, 65, text=controls_info, fill='white', anchor=SW, font=self.fnt)

    def preparePolygon(self, cube: [matrix.Vector3D]):
        # Cube
        polys_to_draw = []
        for i in range(len(self.cube_faces)):
            poly = []
            for j in range(len(self.cube_faces[0])):
                v = cube[self.cube_faces[i][j]]
                r = self.transformation_matrix * v

                poly.append(r)
            n = self.calcNormalVec(poly)
            if not self.isPolygonFrontFace(poly[0], n):  # Backface culling
                continue

            poly2d = []
            nearest_point = 0
            in_viewing_volume = False

            for j in range(len(poly)):
                ps = self.projection_matrix * poly[j]  # 3D do 2D

                p = self.to_screen_matrix * ps
                x, y = int(p.x), int(p.y)
                poly2d.append((x, y))
                nearest_point = max(nearest_point, p.z)

                if (-2.0 <= ps.x <= 2.0) and (-1.0 <= ps.y <= 1.0) and (-10.0 <= ps.z <= 1.0):
                    in_viewing_volume = True

            if in_viewing_volume:
                polys_to_draw.append({'poly2d': poly2d, 'distance': nearest_point, 'cls': self.cls[i]})
        return polys_to_draw

    @staticmethod
    def isPolygonFrontFace(v, n):
        c = matrix.Vector3D(0.0, 0.0, 1.0)
        return (v - c).dot(n) < 0.0

    @staticmethod
    def calcNormalVec(p):
        v1 = p[0] - p[1]
        v2 = p[0] - p[3]
        v = v1.cross(v2)
        v.normalize()
        return v

    def getForwardVec2(self, yrot):  # Where the camera is facing.
        f1 = -math.sin(math.radians(yrot))
        f2 = 0.0
        f3 = -math.cos(math.radians(yrot))
        v = matrix.Vector3D(f1, f2, f3)

        return v

    def mousewheel_callback(self, event):
        if event.num == 5 or event.delta == -120:
            self.zoom -= self.zoom / 3
        if event.num == 4 or event.delta == 120:
            self.zoom += self.zoom / 3
        self.zoom = max(0.1, self.zoom)
        self.zoom = min(10.0, self.zoom)
        self.update()

    def key_callback(self, event):

        v_fwd = self.getForwardVec2(self.ang[1])
        # Do przodu
        if event.keysym == 'Up':
            self.translation[0] += v_fwd.x * VirtualCamera.SPEED
            self.translation[2] += v_fwd.z * VirtualCamera.SPEED
        # Do tyłu
        elif event.keysym == 'Down':
            self.translation[0] -= v_fwd.x * VirtualCamera.SPEED
            self.translation[2] -= v_fwd.z * VirtualCamera.SPEED
        # Obórt w prawo
        elif event.keysym == 'Right':
            self.ang[1] -= 1.5
        # Obrót w lewo
        elif event.keysym == 'Left':
            self.ang[1] += 1.5
        # Do góry
        elif event.keysym == 'u':
            self.translation[1] += VirtualCamera.SPEED
        # Do dołu
        elif event.keysym == 'd':
            self.translation[1] -= VirtualCamera.SPEED
        # Wyjście
        elif event.keysym == 'Escape':
            self.tk.quit()

        # Korekcja
        if self.ang[1] >= 360.0:
            self.ang[1] -= 360.0
        if self.ang[1] < 0.0:
            self.ang[1] += 360.0

        self.update()


if __name__ == "__main__":
    VirtualCamera()
