import numpy as npy
import scipy.fftpack as sf
import math
import matplotlib.pyplot as mplp

def dftregistration(buf1ft,buf2ft,usfac=100):
   """
       # function [output Greg] = dftregistration(buf1ft,buf2ft,usfac);
       # Efficient subpixel image registration by crosscorrelation. This code
       # gives the same precision as the FFT upsampled cross correlation in a
       # small fraction of the computation time and with reduced memory
       # requirements. It obtains an initial estimate of the
crosscorrelation peak
       # by an FFT and then refines the shift estimation by upsampling the DFT
       # only in a small neighborhood of that estimate by means of a
       # matrix-multiply DFT. With this procedure all the image points
are used to
       # compute the upsampled crosscorrelation.
       # Manuel Guizar - Dec 13, 2007

       # Portions of this code were taken from code written by Ann M. Kowalczyk
       # and James R. Fienup.
       # J.R. Fienup and A.M. Kowalczyk, "Phase retrieval for a complex-valued
       # object by using a low-resolution image," J. Opt. Soc. Am. A 7, 450-458
       # (1990).

       # Citation for this algorithm:
       # Manuel Guizar-Sicairos, Samuel T. Thurman, and James R. Fienup,
       # "Efficient subpixel image registration algorithms," Opt. Lett. 33,
       # 156-158 (2008).

       # Inputs
       # buf1ft    Fourier transform of reference image,
       #           DC in (1,1)   [DO NOT FFTSHIFT]
       # buf2ft    Fourier transform of image to register,
       #           DC in (1,1) [DO NOT FFTSHIFT]
       # usfac     Upsampling factor (integer). Images will be registered to
       #           within 1/usfac of a pixel. For example usfac = 20 means the
       #           images will be registered within 1/20 of a pixel.
(default = 1)

       # Outputs
       # output =  [error,diffphase,net_row_shift,net_col_shift]
       # error     Translation invariant normalized RMS error between f and g
       # diffphase     Global phase difference between the two images (should be
       #               zero if images are non-negative).
       # net_row_shift net_col_shift   Pixel shifts between images
       # Greg      (Optional) Fourier transform of registered version of buf2ft,
       #           the global phase difference is compensated for.
   """

   # Compute error for no pixel shift
   if usfac == 0:
       CCmax = npy.sum(buf1ft*npy.conj(buf2ft))
       rfzero = npy.sum(abs(buf1ft)**2)
       rgzero = npy.sum(abs(buf2ft)**2)
       error = 1.0 - CCmax*npy.conj(CCmax)/(rgzero*rfzero)
       error = npy.sqrt(npy.abs(error))
       diffphase = npy.arctan2(npy.imag(CCmax),npy.real(CCmax))
       return error, diffphase

   # Whole-pixel shift - Compute crosscorrelation by an IFFT and locate the
   # peak
   elif usfac == 1:
       ndim = npy.shape(buf1ft)
       m = ndim[0]
       n = ndim[1]
       CC = sf.ifft2(buf1ft*npy.conj(buf2ft))
       max1,loc1 = idxmax(CC)
       rloc = loc1[0]
       cloc = loc1[1]
       CCmax=CC[rloc,cloc]
       rfzero = npy.sum(npy.abs(buf1ft)**2)/(m*n)
       rgzero = npy.sum(npy.abs(buf2ft)**2)/(m*n)
       error = 1.0 - CCmax*npy.conj(CCmax)/(rgzero*rfzero)
       error = npy.sqrt(npy.abs(error))
       diffphase=npy.arctan2(npy.imag(CCmax),npy.real(CCmax))
       md2 = npy.fix(m/2)
       nd2 = npy.fix(n/2)
       if rloc > md2:
           row_shift = rloc - m
       else:
           row_shift = rloc

       if cloc > nd2:
           col_shift = cloc - n
       else:
           col_shift = cloc

       ndim = npy.shape(buf2ft)
       nr = ndim[0]
       nc = ndim[1]
       Nr = sf.ifftshift(npy.arange(-npy.fix(1.*nr/2),npy.ceil(1.*nr/2)))
       Nc = sf.ifftshift(npy.arange(-npy.fix(1.*nc/2),npy.ceil(1.*nc/2)))
       Nc,Nr = npy.meshgrid(Nc,Nr)
       Greg = buf2ft*npy.exp(1j*2*npy.pi*(-1.*row_shift*Nr/nr-1.*col_shift*Nc/nc))
       Greg = Greg*npy.exp(1j*diffphase)
       image_reg = sf.ifft2(Greg) * npy.sqrt(nr*nc)

       #return error,diffphase,row_shift,col_shift
       return error,diffphase,row_shift,col_shift, image_reg

   # Partial-pixel shift
   else:

       # First upsample by a factor of 2 to obtain initial estimate
       # Embed Fourier data in a 2x larger array
       ndim = npy.shape(buf1ft)
       m = ndim[0]
       n = ndim[1]
       mlarge=m*2
       nlarge=n*2
       print("inside align_class sub_pixel alignment function, get rid of this and change dtype back to complex128")
       CC=npy.zeros([mlarge,nlarge],dtype=npy.complex128)
       print("printing index thing: ", m-npy.fix(m/2),type(m-npy.fix(m/2)))
       CC[int(m-npy.fix(m/2)):int(m+1+npy.fix((m-1)/2)),int(n-npy.fix(n/2)):int(n+1+npy.fix((n-1)/2))] = (sf.fftshift(buf1ft)*npy.conj(sf.fftshift(buf2ft)))[:,:]


       # Compute crosscorrelation and locate the peak
       CC = sf.ifft2(sf.ifftshift(CC)) # Calculate cross-correlation
       max1,loc1 = idxmax(npy.abs(CC))

       rloc = (loc1[0])
       cloc = (loc1[1])
       print("At line 125, delete the changes below")
       print(type(rloc), rloc, type(cloc), cloc)
       CCmax = CC[int(rloc),int(cloc)]

       # Obtain shift in original pixel grid from the position of the
       # crosscorrelation peak
       ndim = npy.shape(CC)
       m = ndim[0]
       n = ndim[1]

       md2 = npy.fix(m/2)
       nd2 = npy.fix(n/2)
       if rloc > md2:
           row_shift = rloc - m
       else:
           row_shift = rloc

       if cloc > nd2:
           col_shift = cloc - n
       else:
           col_shift = cloc

       row_shift=row_shift/2
       col_shift=col_shift/2

       # If upsampling > 2, then refine estimate with matrix multiply DFT
       if usfac > 2:
           ### DFT computation ###
           # Initial shift estimate in upsampled grid
           row_shift = 1.*npy.round(row_shift*usfac)/usfac;
           col_shift = 1.*npy.round(col_shift*usfac)/usfac;
           dftshift = npy.fix(npy.ceil(usfac*1.5)/2); ## Center of output array at dftshift+1
           # Matrix multiply DFT around the current shift estimate
           CC = npy.conj(dftups(buf2ft*npy.conj(buf1ft),npy.ceil(usfac*1.5),npy.ceil(usfac*1.5),usfac,\
               dftshift-row_shift*usfac,dftshift-col_shift*usfac))/(md2*nd2*usfac**2)
           # Locate maximum and map back to original pixel grid
           max1,loc1 = idxmax(npy.abs(CC))
           rloc = loc1[0]
           cloc = loc1[1]

           CCmax = CC[int(rloc),int(cloc)]
           rg00 = dftups(buf1ft*npy.conj(buf1ft),1,1,usfac)/(md2*nd2*usfac**2)
           rf00 = dftups(buf2ft*npy.conj(buf2ft),1,1,usfac)/(md2*nd2*usfac**2)
           rloc = rloc - dftshift
           cloc = cloc - dftshift
           row_shift = 1.*row_shift + 1.*rloc/usfac
           col_shift = 1.*col_shift + 1.*cloc/usfac

       # If upsampling = 2, no additional pixel shift refinement
       else:
           rg00 = npy.sum(buf1ft*npy.conj(buf1ft))/m/n;
           rf00 = npy.sum(buf2ft*npy.conj(buf2ft))/m/n;

       error = 1.0 - CCmax*npy.conj(CCmax)/(rg00*rf00);
       error = npy.sqrt(npy.abs(error));
       diffphase = npy.arctan2(npy.imag(CCmax),npy.real(CCmax));
       # If its only one row or column the shift along that dimension has no
       # effect. We set to zero.
       if md2 == 1:
          row_shift = 0

       if nd2 == 1:
          col_shift = 0;

       # Compute registered version of buf2ft
       if usfac > 0:
          ndim = npy.shape(buf2ft)
          nr = ndim[0]
          nc = ndim[1]
          Nr = sf.ifftshift(npy.arange(-npy.fix(1.*nr/2),npy.ceil(1.*nr/2)))
          Nc = sf.ifftshift(npy.arange(-npy.fix(1.*nc/2),npy.ceil(1.*nc/2)))
          Nc,Nr = npy.meshgrid(Nc,Nr)
          Greg = buf2ft*npy.exp(1j*2*npy.pi*(-1.*row_shift*Nr/nr-1.*col_shift*Nc/nc))
          Greg = Greg*npy.exp(1j*diffphase)
       elif (nargout > 1)&(usfac == 0):
          Greg = npy.dot(buf2ft,exp(1j*diffphase))
          
       #mplp.figure(3)
       image_reg = sf.ifft2(Greg) * npy.sqrt(nr*nc)
       #imgplot = mplp.imshow(npy.abs(image_reg))

       #a_ini = npy.zeros((100,100))
       #a_ini[40:59,40:59] = 1.
       #a = a_ini * npy.exp(1j*15.) 
       #mplp.figure(6)
       #imgplot = mplp.imshow(npy.abs(a))       
       #mplp.figure(3)
       #imgplot = mplp.imshow(npy.abs(a)-npy.abs(image_reg))
       #mplp.colorbar()

       # return error,diffphase,row_shift,col_shift,Greg
       return error,diffphase,row_shift,col_shift, image_reg


def dftups(inp,nor,noc,usfac=1,roff=0,coff=0):
   """
       # function out=dftups(in,nor,noc,usfac,roff,coff);
       # Upsampled DFT by matrix multiplies, can compute an upsampled
DFT in just
       # a small region.
       # usfac         Upsampling factor (default usfac = 1)
       # [nor,noc]     Number of pixels in the output upsampled DFT, in
       #               units of upsampled pixels (default = size(in))
       # roff, coff    Row and column offsets, allow to shift the
output array to
       #               a region of interest on the DFT (default = 0)
       # Recieves DC in upper left corner, image center must be in (1,1)
       # Manuel Guizar - Dec 13, 2007
       # Modified from dftus, by J.R. Fienup 7/31/06

       # This code is intended to provide the same result as if the following
       # operations were performed
       #   - Embed the array "in" in an array that is usfac times larger in each
       #     dimension. ifftshift to bring the center of the image to (1,1).
       #   - Take the FFT of the larger array
       #   - Extract an [nor, noc] region of the result. Starting with the
       #     [roff+1 coff+1] element.

       # It achieves this result by computing the DFT in the output
array without
       # the need to zeropad. Much faster and memory efficient than the
       # zero-padded FFT approach if [nor noc] are much smaller than
[nr*usfac nc*usfac]
   """

   ndim = npy.shape(inp)
   nr = ndim[0]
   nc = ndim[1]

   # Compute kernels and obtain DFT by matrix products
   print("at line 255 delete everything until a=npy.zeros....")
   print("type and value of nc: ", type(nc), nc)
   print("type and value noc: ", type(noc), noc)
   print("type and value npy.floor(1.*nc/2)", type(npy.floor(1.*nc/2)), npy.floor(1.*nc/2))
   a = npy.zeros([nc,1])
   a[:,0] = ((sf.ifftshift(npy.arange(nc)))-npy.floor(1.*nc/2))[:]
   b = npy.zeros([1,int(noc)])
   b[0,:] = (npy.arange(int(noc))-coff)[:]
   kernc = npy.exp((-1j*2*npy.pi/(nc*usfac))*npy.dot(a,b))
   nndim = kernc.shape
   #print nndim

   a = npy.zeros([int(nor),1])
   a[:,0] = (npy.arange(int(nor))-roff)[:]
   b = npy.zeros([1,int(nr)])
   b[0,:] = (sf.ifftshift(npy.arange(int(nr)))-npy.floor(1.*nr/2))[:]
   kernr = npy.exp((-1j*2*npy.pi/(nr*usfac))*npy.dot(a,b))
   nndim = kernr.shape
   #print nndim

   return npy.dot(npy.dot(kernr,inp),kernc)



def idxmax(data):
   ndim = npy.shape(data)
   #maxd = npy.max(data)
   maxd = npy.max(npy.abs(data))
   t1 = mplp.mlab.find(npy.abs(data) == maxd)
   idx = npy.zeros([len(ndim),])
   for ii in range(len(ndim)-1):
       t1,t2 = npy.modf(1.*t1/npy.prod(ndim[(ii+1):]))
       print("Line 287 in align class delete this: type of t2: ", type(t2), type(idx[ii]))
       print("Type of npy.modf...", type(npy.modf(1.*t1/npy.prod(ndim[(ii+1):]))[0]))
       print(type(npy.modf(1.*t1/npy.prod(ndim[(ii+1):]))[1]))
       idx[ii] = t2
       t1 *= npy.prod(ndim[(ii+1):])
   idx[npy.size(ndim)-1] = t1

   return maxd,idx


def flip_conj(tmp):
    #ndims = npy.shape(tmp)
    #nx = ndims[0]
    #ny = ndims[1]
    #nz = ndims[2]
    #tmp_twin = npy.zeros([nx,ny,nz]).astype(complex)
    #for i in range(0,nx):
    #   for j in range(0,ny):
    #      for k in range(0,nz):
    #         i_tmp = nx - 1 - i
    #         j_tmp = ny - 1 - j
    #         k_tmp = nz - 1 - k
    #         tmp_twin[i,j,k] = tmp[i_tmp,j_tmp,k_tmp].conj()
    #return tmp_twin

    tmp_fft = sf.ifftshift(sf.ifftn(sf.fftshift(tmp)))
    return sf.ifftshift(sf.fftn(sf.fftshift(npy.conj(tmp_fft)))) 

def check_conj(ref, tmp,threshold_flag, threshold,subpixel_flag):
    ndims = npy.shape(ref)
    nx = ndims[0]
    ny = ndims[1]
    nz = ndims[2]

    if threshold_flag == 1:
       ref_tmp = npy.zeros((nx,ny,nz))
       index = npy.where(npy.abs(ref) >= threshold*npy.max(npy.abs(ref)))
       ref_tmp[index] = 1.
       tmp_tmp = npy.zeros((nx,ny,nz))
       index = npy.where(npy.abs(tmp) >= threshold*npy.max(npy.abs(tmp)))
       tmp_tmp[index] = 1.
       tmp_conj = flip_conj(tmp_tmp)
    else:
       ref_tmp = ref
       tmp_tmp = tmp
       tmp_conj = flip_conj(tmp)
       
    tmp_tmp = subpixel_align(ref_tmp,tmp_tmp,threshold_flag,threshold,subpixel_flag)
    tmp_conj = subpixel_align(ref_tmp,tmp_conj,threshold_flag,threshold,subpixel_flag)

    cc_1 = sf.ifftn(ref_tmp*npy.conj(tmp_tmp))
    cc1 = npy.max(cc_1.real)
    #cc1 = npy.max(npy.abs(cc_1))
    cc_2 = sf.ifftn(ref_tmp*npy.conj(tmp_conj))
    cc2 = npy.max(cc_2.real)
    #cc2 = npy.max(npy.abs(cc_2))
    print(cc1, cc2)
    if cc1 > cc2:
        return 0
    else:
        return 1

def subpixel_align(ref,tmp,threshold_flag,threshold, subpixel_flag):
    ndims = npy.shape(ref)
    if npy.size(ndims) == 3:
       nx = ndims[0]
       ny = ndims[1]
       nz = ndims[2]

       if threshold_flag == 1:
          ref_tmp = npy.zeros((nx,ny,nz))
          index = npy.where(npy.abs(ref) >= threshold*npy.max(npy.abs(ref)))
          ref_tmp[index] = 1.
          tmp_tmp = npy.zeros((nx,ny,nz))
          index = npy.where(npy.abs(tmp) >= threshold*npy.max(npy.abs(tmp)))
          tmp_tmp[index] = 1.
          ref_fft = sf.ifftn(sf.fftshift(ref_tmp))
          tmp_fft = sf.ifftn(sf.fftshift(tmp_tmp))
          real_fft = sf.ifftn(sf.fftshift(tmp))
       else:
          ref_fft = sf.ifftn(sf.fftshift(ref))
          tmp_fft = sf.ifftn(sf.fftshift(tmp))

       nest = npy.mgrid[0:nx,0:ny,0:nz]

       result = dftregistration(ref_fft[:,:,0],tmp_fft[:,:,0],usfac=100)
       e, p, cl, r, array_shift = result
       x_shift_1 = cl
       y_shift_1 = r
       result = dftregistration(ref_fft[:,:,nz-1],tmp_fft[:,:,nz-1],usfac=100)
       e, p, cl, r, array_shift = result
       x_shift_2 = cl
       y_shift_2 = r
    
       result = dftregistration(ref_fft[:,0,:],tmp_fft[:,0,:],usfac=100)
       e, p, cl, r, array_shift = result
       x_shift_3 = cl
       z_shift_1 = r
       result = dftregistration(ref_fft[:,ny-1,:],tmp_fft[:,ny-1,:],usfac=100)
       e, p, cl, r, array_shift = result
       x_shift_4 = cl
       z_shift_2 = r
       
       result = dftregistration(ref_fft[0,:,:],tmp_fft[0,:,:],usfac=100)
       e, p, cl, r, array_shift = result
       y_shift_3 = cl
       z_shift_3 = r
       result = dftregistration(ref_fft[nx-1,:,:],tmp_fft[nx-1,:,:],usfac=100)
       e, p, cl, r, array_shift = result
       y_shift_4 = cl
       z_shift_4 = r


       if subpixel_flag == 1:
          x_shift = (x_shift_1 + x_shift_2 + x_shift_3 + x_shift_4)/4.
          y_shift = (y_shift_1 + y_shift_2 + y_shift_3 + y_shift_4)/4.
          z_shift = (z_shift_1 + z_shift_2 + z_shift_3 + z_shift_4)/4.
       else:
          x_shift = npy.floor((x_shift_1 + x_shift_2 + x_shift_3 + x_shift_4)/4.+0.5)
          y_shift = npy.floor((y_shift_1 + y_shift_2 + y_shift_3 + y_shift_4)/4.+0.5)
          z_shift = npy.floor((z_shift_1 + z_shift_2 + z_shift_3 + z_shift_4)/4.+0.5)

       print ('x, y, z shift:', x_shift, y_shift, z_shift)

       if threshold_flag == 1:
          tmp_fft_new = sf.ifftshift(real_fft) * npy.exp(1j*2*npy.pi*(-1.*x_shift*(nest[0,:,:,:]-nx/2.)/(nx)-y_shift*(nest[1,:,:,:]-ny/2.)/(ny)-z_shift*(nest[2,:,:,:]-nz/2.)/(nz)))
       else:
          tmp_fft_new = sf.ifftshift(tmp_fft) * npy.exp(1j*2*npy.pi*(-1.*x_shift*(nest[0,:,:,:]-nx/2.)/(nx)-y_shift*(nest[1,:,:,:]-ny/2.)/(ny)-z_shift*(nest[2,:,:,:]-nz/2.)/(nz)))

    if npy.size(ndims) == 2:
       nx = ndims[0]
       ny = ndims[1]

       if threshold_flag == 1:
          ref_tmp = npy.zeros((nx,ny))
          index = npy.where(npy.abs(ref) >= threshold*npy.max(npy.abs(ref)))
          ref_tmp[index] = 1.
          tmp_tmp = npy.zeros((nx,ny))
          index = npy.where(npy.abs(tmp) >= threshold*npy.max(npy.abs(tmp)))
          tmp_tmp[index] = 1.
          
          ref_fft = sf.ifftn(sf.fftshift(ref_tmp))
          mp_fft = sf.ifftn(sf.fftshift(tmp_tmp))
          real_fft = sf.ifftn(sf.fftshift(tmp))
       else:
          ref_fft = sf.ifftn(sf.fftshift(ref))
          tmp_fft = sf.ifftn(sf.fftshift(tmp))

       nest = npy.mgrid[0:nx,0:ny]

       result = dftregistration(ref_fft[:,:],tmp_fft[:,:],usfac=100)
       e, p, cl, r, array_shift = result
       x_shift = cl
       y_shift = r

       if subpixel_flag == 1:
          x_shift = x_shift
          y_shift = y_shift
       else:
          x_shift = npy.floor(x_shift + 0.5)
          y_shift = npy.floor(y_shift + 0.5)

       print ('x, y shift:', x_shift, y_shift)

       if threshold_flag == 1:
          tmp_fft_new = sf.ifftshift(real_fft) * npy.exp(1j*2*npy.pi*(-1.*x_shift*(nest[0,:,:]-nx/2.)/(nx)-y_shift*(nest[1,:,:]-ny/2.)/(ny)))
       else:
          tmp_fft_new = sf.ifftshift(tmp_fft) * npy.exp(1j*2*npy.pi*(-1.*x_shift*(nest[0,:,:]-nx/2.)/(nx)-y_shift*(nest[1,:,:]-ny/2.)/(ny)))

    return sf.ifftshift(sf.fftn(sf.fftshift(tmp_fft_new))),x_shift,y_shift

    
def remove_phase_ramp(tmp,threshold_flag, threshold,subpixel_flag):
   tmp_tmp,x_shift,y_shift = subpixel_align(sf.ifftshift(sf.ifftn(sf.fftshift(npy.abs(tmp)))), sf.ifftshift(sf.ifftn(sf.fftshift(tmp))), threshold_flag, threshold,subpixel_flag) 
   tmp_new = sf.ifftshift(sf.fftn(sf.fftshift(tmp_tmp)))
   phase_tmp = npy.angle(tmp_new)
   ph_offset = npy.mean(phase_tmp[npy.where(npy.abs(tmp) >= threshold)])
   phase_tmp = npy.angle(tmp_new) - ph_offset
   return npy.abs(tmp)*npy.exp(1j*phase_tmp)

def pixel_shift(array,x_shift,y_shift,z_shift):
    nx,ny,nz = npy.shape(array)
    tmp = sf.ifftshift(sf.ifftn(sf.fftshift(array)))
    nest = npy.mgrid[0:nx,0:ny,0:nz]
    tmp = tmp * npy.exp(1j*2*npy.pi*(-1.*x_shift*(nest[0,:,:,:]-nx/2.)/(nx)-y_shift*(nest[1,:,:,:]-ny/2.)/(ny)-z_shift*(nest[2,:,:,:]-nz/2.)/(nz)))
    return sf.ifftshift(sf.fftn(sf.fftshift(tmp)))

def pixel_shift_2d(array,x_shift,y_shift):
    nx,ny = npy.shape(array)
    tmp = sf.ifftshift(sf.ifftn(sf.fftshift(array)))
    nest = npy.mgrid[0:nx,0:ny]
    tmp = tmp * npy.exp(1j*2*npy.pi*(-1.*x_shift*(nest[0,:,:]-nx/2.)/(nx)-y_shift*(nest[1,:,:]-ny/2.)/(ny)))
    return sf.ifftshift(sf.fftn(sf.fftshift(tmp)))

def rm_phase_ramp_manual_2d(array,x_shift,y_shift):
    nx,ny = npy.shape(array)
    nest = npy.mgrid[0:nx,0:ny]
    tmp = array * npy.exp(1j*2*npy.pi*(-1.*x_shift*(nest[0,:,:]-nx/2.)/(nx)-y_shift*(nest[1,:,:]-ny/2.)/(ny)))
    return tmp

if (__name__ == '__main__'):
   pass
