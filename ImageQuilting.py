#! /usr/bin/env python

import Image
import random
import numpy as np
import math


# fetch_patch randomly pick a patch according to patchsize on the sample
def fetch_patch(sample, patchsize):
    pointx = random.randint(0, sample.size[0]-patchsize[0])
    pointy = random.randint(0, sample.size[1]-patchsize[1])
    patchbox = (pointx, pointy, pointx + patchsize[0], pointy +  patchsize[1])
    patch = sample.crop(patchbox)
    return patch


# compute_ssd computes the average squared difference of the overlapping region 
# between previous patch and sampled patch
def vertical_ssd(previous_patch, patch, overlap):
    previous_patch = np.asarray(previous_patch)
    patch = np.asarray(patch)
    vertical_diff = previous_patch[:, -overlap:-1] - patch[:, :overlap-1]
    vertical_ssd = math.sqrt(np.sum([x*x for x in vertical_diff]))
    # vertical_diff_red = previous_patch[:, -overlap:-1, 1] - patch[:, :overlap-1, 1]
    # vertical_diff_green = previous_patch[:, -overlap:-1, 2] - patch[:, :overlap-1, 2]
    # vertical_diff_blue = previous_patch[:, -overlap:-1, 3] - patch[:, :overlap-1, 3]
    # vertical_ssd = math.sqrt(np.sum([x*x for x in vertical_diff_red])+ np.sum([x*x for x in vertical_diff_green]) + np.sum([x*x for x in vertical_diff_blue]))
    return vertical_ssd

def horizontal_ssd(upper_patch, patch, overlap):
    upper_patch = np.asarray(upper_patch)
    patch = np.asarray(patch)
    horizontal_diff = upper_patch[-overlap:-1, :] - patch[:overlap-1, :]
    horizontal_ssd = math.sqrt(np.sum([x*x for x in horizontal_diff]))
    # horizontal_diff_red = upper_patch[-overlap:-1, :, 1] - patch[:overlap-1, :, 1]
    # horizontal_diff_green = upper_patch[-overlap:-1, :, 2] - patch[:overlap-1, :, 2]
    # horizontal_diff_blue = upper_patch[-overlap:-1, :, 3] - patch[:overlap-1, :, 3]
    # horizontal_ssd = math.sqrt(np.sum([x*x for x in horizontal_diff_red])+ np.sum([x*x for x in horizontal_diff_green]) + np.sum([x*x for x in horizontal_diff_blue]))
    return horizontal_ssd
    
    
    
# part 1: randomly sampled texture
# randomly samples square patches of size 'patchsize' from sample
# and create an output image of 'outsize'.
# start from the upper left corner, and tile samples until the image
# is full. If the patches don't fit evely into the output image,
# leave black border at the edges.

def quilt_random(sample, outsize, patchsize):
    output = Image.new("RGB",outsize,"black")
    sample = Image.open(sample)
    
    for y in range(0, outsize[1]//patchsize[1]):
        for x in range(0, outsize[0]//patchsize[0]):
            patch = fetch_patch(sample, patchsize)
            pastebox = (x*patchsize[0],y*patchsize[1], (x+1)*patchsize[0], (y+1)*patchsize[1] )
            output.paste(patch,pastebox) 
    
    output.show()
    
    return output
 
    
    
# part 2: overlapping patches
# sample new patches to overlap with exitsting ones, 
# the squared difference of which should be below some tolerance (measured per pixel)

def quilt_simple(inpatch, outsize, patchsize, overlap, tol):
    output = Image.new("RGB", outsize)
    sample = Image.open(inpatch).convert("RGB")
    previous_patch = fetch_patch(sample, patchsize)
    box = (0, 0, patchsize[0], patchsize[1])
    output.paste(previous_patch,box)

    for y in range(0, (outsize[1]+overlap)//(patchsize[1]-overlap)):
        for x in range(0, (outsize[0]+overlap)//(patchsize[0]-overlap)):
            patch = fetch_patch(sample, patchsize)
            # first row
            if y==0:
                v_ssd = vertical_ssd(previous_patch, patch, overlap) 
                while(v_ssd / (overlap * patchsize[1]) > tol):
                    patch = fetch_patch(sample, patchsize)
                    v_ssd = vertical_ssd(previous_patch, patch, overlap) 
                # skip first block
                if x!=0:
                    box = (x*patchsize[0],y*patchsize[1], (x+1)*patchsize[0], (y+1)*patchsize[1])
            else:
                # calculate both vertical and horizontal squared difference for patches other than the first row
                v_ssd = vertical_ssd(previous_patch, patch, overlap)
                upper_box = (x*patchsize[0],(y-1)*patchsize[1],(x+1)*patchsize[0] ,y*patchsize[1])
                upper_patch = output.crop(upper_box) 
                h_ssd = horizontal_ssd(upper_patch, patch, overlap)
                print (v_ssd+h_ssd)/(overlap*(patchsize[0]+patchsize[1]))
                while(((v_ssd+h_ssd)/(overlap*(patchsize[0]+patchsize[1])))>tol):
                    print (v_ssd+h_ssd)/(overlap*(patchsize[0]+patchsize[1]))
                    patch = fetch_patch(sample, patchsize)
                    v_ssd = vertical_ssd(previous_patch, patch, overlap)
                    uupper_box = (x*patchsize[0],(y-1)*patchsize[1],(x+1)*patchsize[0] ,y*patchsize[1])
                    upper_patch = output.crop(upper_box) 
                    h_ssd = horizontal_ssd(upper_patch, patch, overlap)
                box = (x*patchsize[0],y*patchsize[1], (x+1)*patchsize[0], (y+1)*patchsize[1])
            output.paste(patch, box) 
            previous_patch = patch
    
    output.show()
    
    return output        
                
                
            


