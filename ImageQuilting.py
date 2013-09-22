#! /usr/bin/env python
import random
import numpy as np
import math
import Image


##################################################################    
# part 1: randomly sampled texture
# randomly samples square patches of size 'patchsize' from sample
# and create an output image of 'outsize'.
# start from the upper left corner, and tile samples until the image
# is full. If the patches don't fit evely into the output image,
# leave black border at the edges.

# random_patch randomly pick a patch according to patchsize on an sample
def random_patch(sample, patchsize):
    pointx = random.randint(0, sample.size[0]-patchsize[0])
    pointy = random.randint(0, sample.size[1]-patchsize[1])
    patchbox = (pointx, pointy, pointx + patchsize[0], pointy +  patchsize[1])
    patch = sample.crop(patchbox)
    return patch


def quilt_random(sample, outsize, patchsize):
    output = Image.new("RGB",outsize,"black")
    sample = Image.open(sample)
    
    for y in range(0, outsize[1]//patchsize[1]):
        for x in range(0, outsize[0]//patchsize[0]):
            patch = random_patch(sample, patchsize)
            pastebox = (x*patchsize[0],y*patchsize[1], (x+1)*patchsize[0], (y+1)*patchsize[1] )
            output.paste(patch,pastebox) 
    
    output.show()
    
    return output
 
    
##################################################################   
# part 2: overlapping patches
# sample new patches to overlap with exitsting ones, 
# the squared difference of which should be below some tolerance (measured per pixel)


def sample_patch(sample,patchsize,x,y):
    patchbox = (x, y, x+patchsize[0], y+patchsize[1])
    patch = sample.crop(patchbox)
    return patch
            
    
# vertical_ssd and horizontal_ssd computes the sum of squared differences within 
# the overlapping region between previous patch and sampled patch

def vertical_ssd(previous_patch, patch, overlap):
    previous_patch = np.asarray(previous_patch)
    patch = np.asarray(patch)
    vertical_diff = previous_patch[:, -overlap:] - patch[:, :overlap]
    vertical_ssd = math.sqrt(np.sum([x*x for x in vertical_diff]))
    return vertical_ssd, vertical_diff

def horizontal_ssd(upper_patch, patch, overlap):
    upper_patch = np.asarray(upper_patch)
    patch = np.asarray(patch)
    horizontal_diff = upper_patch[-overlap:, :] - patch[:overlap, :]
    horizontal_ssd = math.sqrt(np.sum([x*x for x in horizontal_diff]))
    return horizontal_ssd, horizontal_diff


def quilt_simple(inpatch, outsize, patchsize, overlap):
    output = Image.new("RGB", outsize)
    sample = Image.open(inpatch).convert("RGB")
    # randomly pick a patch as the first one
    previous_patch = random_patch(sample, patchsize)
    box = (0, 0, patchsize[0], patchsize[1])
    output.paste(previous_patch,box)

    for y in range((outsize[1]+overlap)//(patchsize[1]-overlap)):
        for x in range((outsize[0]+overlap)//(patchsize[0]-overlap)):
            # first row
            if y==0:
                ssd = vertical_ssd(previous_patch, sample_patch(sample,patchsize,0,0), overlap)[0] 
                for i in range(0, sample.size[0]-patchsize[0]):
                    for j in range(0, sample.size[1]-patchsize[1]):
                        if i!=0:
                            new_ssd = vertical_ssd(previous_patch, sample_patch(sample,patchsize,i,j), overlap)[0]
                            if new_ssd < ssd and new_ssd>0:
                                ssd = new_ssd
                patch = random_patch(sample, patchsize)
                new_ssd = vertical_ssd(previous_patch, patch, overlap)[0] 
                while(new_ssd > 1.05*ssd):
                    patch = random_patch(sample, patchsize)
                    new_ssd = vertical_ssd(previous_patch, patch, overlap)[0]
                if x!=0:               
                    box = (x*patchsize[0]-x*overlap, 0, (x+1)*patchsize[0]-x*overlap, patchsize[1])
            else:                
                upper_box = (x*patchsize[0]-x*overlap,(y-1)*patchsize[1]-(y-1)*overlap,(x+1)*patchsize[0]-x*overlap, y*patchsize[1]-(y-1)*overlap)
                upper_patch = output.crop(upper_box) 
                # calculate horizontal squared difference for patches in the first columns
                if x==0:
                    patch = sample_patch(sample,patchsize,0,0)
                    ssd = horizontal_ssd(upper_patch, patch, overlap)[0]
                    for i in range(0, sample.size[0]-patchsize[0]):
                        for j in range(0, sample.size[1]-patchsize[1]):
                            new_patch = sample_patch(sample,patchsize,i,j)
                            new_ssd = horizontal_ssd(upper_patch, new_patch, overlap)[0]
                            if new_ssd < ssd:
                                ssd = new_ssd
                                patch = new_patch
                    patch = random_patch(sample, patchsize)
                    new_ssd = horizontal_ssd(upper_patch, patch, overlap)[0] 
                    while(new_ssd > 1.05*ssd):
                        patch = random_patch(sample, patchsize)
                        new_ssd = horizontal_ssd(upper_patch, patch, overlap)[0]  
                    box = (0, y*patchsize[1]-y*overlap, patchsize[0], (y+1)*patchsize[1]-y*overlap)
                # calculate both vertical and horizontal squared difference for patches other than the first row
                else:
                    patch = sample_patch(sample,patchsize,0,0)                   
                    ssd = horizontal_ssd(upper_patch, patch, overlap)[0]+vertical_ssd(previous_patch, patch, overlap)[0]
                    for i in range(0, sample.size[0]-patchsize[0]):
                        for j in range(0, sample.size[1]-patchsize[1]):
                            new_patch = sample_patch(sample,patchsize,i,j)
                            new_ssd = horizontal_ssd(upper_patch, new_patch, overlap)[0] + vertical_ssd(previous_patch, new_patch, overlap)[0]
                            if new_ssd < ssd:
                                ssd = new_ssd
                                patch = new_patch
                    patch = random_patch(sample, patchsize)
                    new_ssd = vertical_ssd(previous_patch, patch, overlap)[0] + horizontal_ssd(upper_patch, patch, overlap)[0] 
                    while(new_ssd > 1.05*ssd):
                        patch = random_patch(sample, patchsize)
                        new_ssd = vertical_ssd(previous_patch, patch, overlap)[0] + horizontal_ssd(upper_patch, patch, overlap)[0] 
                    box = (x*patchsize[0]-x*overlap, y*patchsize[1]-y*overlap, (x+1)*patchsize[0]-x*overlap, (y+1)*patchsize[1]-y*overlap)       
            # paste an optimal patch
            print("quilting...")
            output.paste(patch, box)
            previous_patch = patch
    print "Done!"
    output.show()
    
    return output    

    
##################################################################    
# part 3: minimum error boundary cut
# remove edge artifacts from the overlapping patches
# the seam is calculated by using dynamic programming to find the min-cost contiguous path in overlapping part
# the cost is the squared differences of the output image and the newly sampled patch    

# min_path finds the path with the lowest energy given a starting point
# input band contains the values, output is the best seam from band[1,j] to the bottom
def min_path(band, i, j):
    path = np.zeros(len(band))
    path[0] = j
    cost = band[i][j]
    for i in range(1, len(band)):
        j = path[i-1]
        if j==0:
            cost = cost + min(band[i][j], band[i][j+1])
            if band[i][j] < band[i][j+1]:
                path[i] = j
            else:
                path[i] = j+1
        elif j==band.shape[1]-1:
            cost = cost + min(band[i][j], band[i][j-1])
            if band[i][j] < band[i][j-1]:
                path[i] = j
            else:
                path[i] = j-1
        else:
            cost = cost + min(band[i][j-1], band[i][j], band[i][j+1])
            if band[i][j] <= band[i][j-1]:
                if band[i][j] <= band[i][j+1]:
                    path[i] = j
                else:
                    path[i] = j+1
            else:
                path[i] = j-1         
    return cost,path

# min_seam finds the minimal path    
def min_seam(band):
    min_cost = min_path(band,0,0)[0]
    path = min_path(band,0,0)[1]
    for i in range(1, len(band[0])):
        if min_path(band,0,i)[0] < min_cost:
            path = min_path(band,0,i)[1]
            min_cost = min_path(band,0,i)[0]
    return path

# convert rgb to grayscale
def rgb2gray(rgb):
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray
    
def quilt_seam(inpatch, outsize, patchsize, overlap):    
    output = Image.new("RGB", outsize)
    sample = Image.open(inpatch).convert("RGB")
    # randomly pick a patch as the first one
    previous_patch = random_patch(sample, patchsize)
    box = (0, 0, patchsize[0], patchsize[1])
    output.paste(previous_patch,box)
    pixels = output.load()

    for y in range((outsize[1]+overlap)//(patchsize[1]-overlap)):
        for x in range((outsize[0]+overlap)//(patchsize[0]-overlap)):
            # first row
            if y==0:
                ssd = vertical_ssd(previous_patch, sample_patch(sample,patchsize,0,0), overlap)[0] 
                for i in range(0, sample.size[0]-patchsize[0]):
                    for j in range(0, sample.size[1]-patchsize[1]):
                        if i!=0:
                            new_ssd = vertical_ssd(previous_patch, sample_patch(sample,patchsize,i,j), overlap)[0]
                            if new_ssd < ssd and new_ssd!=0:
                                ssd = new_ssd
                patch = random_patch(sample, patchsize)
                new_ssd = vertical_ssd(previous_patch, patch, overlap)[0] 
                while(new_ssd > 1.1*ssd):
                    patch = random_patch(sample, patchsize)
                    new_ssd = vertical_ssd(previous_patch, patch, overlap)[0]
                if x!=0: 
                    band = vertical_ssd(previous_patch, patch, overlap)[1]
                    band = rgb2gray(np.array(band)) 
                    for i in range(band.shape[0]):
                        for j in range(band.shape[1]):
                            band[i][j]=int(band[i][j])
                    seam_v = min_seam(band)
                    patch_arr = np.array(patch)
                    # stitch together
                    for i in range(patch_arr.shape[0]):
                        for j in range(int(seam_v[i]),patch_arr.shape[1]):
                            if j+x*(patchsize[1]-overlap)< outsize[0]:
                                pixels[j+x*(patchsize[1]-overlap),i] = tuple(patch_arr[i,j,])                                       
            else:                
                upper_box = (x*patchsize[0]-x*overlap,(y-1)*patchsize[1]-(y-1)*overlap,(x+1)*patchsize[0]-x*overlap, y*patchsize[1]-(y-1)*overlap)
                upper_patch = output.crop(upper_box) 
                # calculate horizontal squared difference for patches in the first columns
                if x==0:
                    patch = sample_patch(sample,patchsize,0,0)
                    ssd = horizontal_ssd(upper_patch, patch, overlap)[0]
                    for i in range(0, sample.size[0]-patchsize[0]):
                        for j in range(0, sample.size[1]-patchsize[1]):
                            new_patch = sample_patch(sample,patchsize,i,j)
                            new_ssd = horizontal_ssd(upper_patch, new_patch, overlap)[0]
                            if new_ssd < ssd and new_ssd!=0:
                                ssd = new_ssd
                                patch = new_patch 
                                patch = new_patch
                    patch = random_patch(sample, patchsize)
                    new_ssd = horizontal_ssd(upper_patch, patch, overlap)[0] 
                    while(new_ssd > 1.1*ssd):
                        patch = random_patch(sample, patchsize)
                        new_ssd = horizontal_ssd(upper_patch, patch, overlap)[0]
                        
                    band = horizontal_ssd(upper_patch, patch, overlap)[1]
                    band = rgb2gray(np.array(band))
                    for i in range(band.shape[0]):
                        for j in range(band.shape[1]):
                            band[i][j]=int(band[i][j])
                    seam_h = min_seam(band.T)
                    patch_arr = np.array(patch)
                    for i in range(patch_arr.shape[0]):
                        for j in range(patch_arr.shape[1]):
                            if i < seam_h[j]:
                                continue
                            else:
                                if i+y*(patchsize[1]-overlap)<outsize[1]:
                                    pixels[j, i+y*(patchsize[1]-overlap)] = tuple(patch_arr[i, j,])
                # calculate both vertical and horizontal squared difference for patches other than the first row
                else:
                    patch = sample_patch(sample,patchsize,0,0)                   
                    ssd = horizontal_ssd(upper_patch, patch, overlap)[0]+vertical_ssd(previous_patch, patch, overlap)[0]
                    for i in range(0, sample.size[0]-patchsize[0]):
                        for j in range(0, sample.size[1]-patchsize[1]):
                            new_patch = sample_patch(sample,patchsize,i,j)
                            new_ssd = horizontal_ssd(upper_patch, new_patch, overlap)[0] + vertical_ssd(previous_patch, new_patch, overlap)[0]
                            if new_ssd < ssd and new_ssd!=0:
                                ssd = new_ssd
                                patch = new_patch
                    patch = random_patch(sample, patchsize)
                    new_ssd = vertical_ssd(previous_patch, patch, overlap)[0] + horizontal_ssd(upper_patch, patch, overlap)[0] 
                    while(new_ssd > 1.1*ssd):
                        patch = random_patch(sample, patchsize)
                        new_ssd = vertical_ssd(previous_patch, patch, overlap)[0] + horizontal_ssd(upper_patch, patch, overlap)[0]
                        
                    band_v = vertical_ssd(previous_patch, patch, overlap)[1]
                    band_v = rgb2gray(np.array(band_v)) 
                    for i in range(band_v.shape[0]):
                        for j in range(band_v.shape[1]):
                            band_v[i][j]=int(band_v[i][j])
                    seam_v = min_seam(band_v)
                    
                    band_h = horizontal_ssd(upper_patch, patch, overlap)[1]
                    band_h = rgb2gray(np.array(band_h))
                    for i in range(band_h.shape[0]):
                        for j in range(band_h.shape[1]):
                            band_h[i][j]=int(band_h[i][j])
                    seam_h = min_seam(band_h.T)
                    
                    for i in range(patch_arr.shape[0]):
                        for j in range(patch_arr.shape[1]):
                            if i < seam_h[j]:
                                continue
                            if j < seam_v[i]:
                                continue
                            else:
                                if j+x*(patchsize[0]-overlap)<outsize[0] and i+y*(patchsize[1]-overlap)<outsize[1]:
                                    pixels[j+x*(patchsize[0]-overlap), i+y*(patchsize[1]-overlap)] = tuple(patch_arr[i, j,])
                previous_patch = patch
                print("quilting...")
    print("Done!")          
    output.show()
    
    return output    
