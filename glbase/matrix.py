import numpy
import math

def to_radian(degree):
    return degree/180.0*math.pi

def get_persepective(fovy, aspect, near, far):
    f=math.atan(float(fovy)/2.0)
    return numpy.array([
        [f/aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, float(far+near)/float(near-far), float(2*far*near)/float(near-far)],
        [0, 0, -1.0, 0]
        ], 'f')

def get_euler(h, p ,b):
    sh=math.sin(to_radian(h))
    sp=math.sin(to_radian(p))
    sb=math.sin(to_radian(b))
    ch=math.cos(to_radian(h))
    cp=math.cos(to_radian(p))
    cb=math.cos(to_radian(b))
    return numpy.array([
        [ch*cb+sh*sp*sb, -ch*sb+sh*sp*cb, sh*cp, 0],
        [sb*cp, cb*cp, -sp, 0],
        [-sh*cb+ch*sp*sb, sb*sh+ch*sp*cb, ch*cp, 0],
        [0, 0, 0, 1]
        ], 'f')

