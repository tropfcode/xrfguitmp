import numpy as np

class Image():
    def __init__(self, im_array, ref_check = False, norm_check = False, align_check = False,
                title = "N/A", f = "N/A", x_shift=0, y_shift=0):
        self.im_array = im_array
        self.img_array2 = im_array
        self.norm_array = np.empty(shape=(0,0))
        self.ref_check = ref_check
        self.norm_check = norm_check
        self.align_check = align_check
        self.title = title
        self.f = f
        self.x_shift = x_shift
        self.y_shift = y_shift
        self.state = 0
        
    def get_state():
        return self.state