import rhinoscriptsyntax as rs
import math

def clamp(minimum, x, maximum):
    return max(minimum, min(x, maximum))
def lerp(min, max, frac):
    return min + (max - min) * frac
    
class Col:
    
    @staticmethod
    def fromLC(c):
        return Col.fromRGB(c[0],c[1],c[2], c[3])
    
    @staticmethod
    def fromHSV(h,s,v, a = 1):
        h = h % 360
        s = clamp(s,0,1)
        v = clamp(v,0,1)
        a = clamp(a,0,1)
        col = Col.hsv2xyz(h,s,v,a)
        return Col(col)
    
    @staticmethod
    def fromRGB(r,g,b,a = 255):
        r = clamp(r,0,255)
        g = clamp(g,0,255)
        b = clamp(b,0,255)
        a = clamp(a,0,255)
        col = Col.rgb2xyz(r,g,b,a)
        return Col(col)
    
    @staticmethod
    def fromXYZ(x,y,z,w = 1):
        x = clamp(x,0,1)
        y = clamp(y,0,1)
        z = clamp(z,0,1)
        w = clamp(w,0,1)
        col = (x,y,z,w)
        return Col(col)
        
    @staticmethod
    def lerp(col1, col2, frac):
        return Col.fromXYZ(
            lerp(col1.x,col2.x,frac),
            lerp(col1.y,col2.y,frac),
            lerp(col1.z,col2.z,frac),
            lerp(col1.w,col2.w,frac)
            )

    @staticmethod
    def greyscale(i, w = 1):
        return Col((i, i, i, w))
        
    @staticmethod
    def hsv2xyz(h, s, v, w = 1):
        h = float(h)
        s = float(s)
        v = float(v)
        w = float(w)
        h60 = h / 60.0
        h60f = math.floor(h60)
        hi = int(h60f) % 6
        f = h60 - h60f
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        r, g, b = 0, 0, 0
        if hi == 0: r, g, b = v, t, p
        elif hi == 1: r, g, b = q, v, p
        elif hi == 2: r, g, b = p, v, t
        elif hi == 3: r, g, b = p, q, v
        elif hi == 4: r, g, b = t, p, v
        elif hi == 5: r, g, b = v, p, q
        return r, g, b, w
        
    @staticmethod
    def xyz2hsv(r, g, b, w = 1):
        mx = max(r, g, b)
        mn = min(r, g, b)
        df = mx-mn
        if mx == mn:
            h = 0
        elif mx == r:
            h = (60 * ((g-b)/df) + 360) % 360
        elif mx == g:
            h = (60 * ((b-r)/df) + 120) % 360
        elif mx == b:
            h = (60 * ((r-g)/df) + 240) % 360
        if mx == 0:
            s = 0
        else:
            s = df/mx
        v = mx
        return h, s, v, w
    
    @staticmethod
    def rgb2xyz(r, g , b, a = 255):
        return r/255.0, g/255.0, b/255.0, a/255.0
    
    @staticmethod
    def xyz2rgb(x , y , z, w = 1):
        return x*255, y*255, z*255, w*255

    def __init__(self,xyz):
        self.xyz = xyz
        self.rgb = Col.xyz2rgb(xyz[0],xyz[1],xyz[2], xyz[3])
        self.hsv = Col.xyz2hsv(xyz[0],xyz[1],xyz[2], xyz[3])
        
        self.x = self.xyz[0]
        self.y = self.xyz[1]
        self.z = self.xyz[2]
        self.w = self.xyz[3]
        
        self.r = self.rgb[0]
        self.g = self.rgb[1]
        self.b = self.rgb[2]
        
        self.h = self.hsv[0]
        self.s = self.hsv[1]
        self.v = self.hsv[2]
        
        self.a = self.rgb[3]
        
        
    def toLC(self):
        return self.rgb
        
    def rot(self,angle):
        return Col.fromHSV(self.h + angle,self.s,self.v, self.w)
        
    
    def lit(self,light):
        return Col.fromHSV(self.h,self.s,self.v * light, self.w)
        
    def fde(self,sat):
        return Col.fromHSV(self.h,self.s * sat,self.v, self.w)
        
    def rfl(self,r,s,l):
        return Col.fromHSV(self.h + r, self.s * s, self.v * l, self.w)
        
    def inv(self):
        return Col.fromXYZ(1 - self.x, 1 - self.y, 1 - self.z, self.w)
       
    def alpha(self, alpha):
        return Col.fromXYZ(self.x, self.y, self.z, alpha)
    