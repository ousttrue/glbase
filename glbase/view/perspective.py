import glbase.matrix


class PerspectiveProjection(object):
    def __init__(self):
        self.aspect=1
        self.n=1
        self.f=10000
        self.fovy=30

    def set_size(self, w, h):
        self.aspect=float(w)/float(h)

    def get_matrix(self):
        return glbase.matrix.get_persepective(self.fovy, self.aspect, self.n, self.f)

