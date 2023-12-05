#This code will be used to filter an image that has been taken and then detect the edge for MTF
from PIL import Image, ImageFilter

#create the image object
ImagePath = 'C:/Users/Public/NeutronImaging/NewStationCode'
image1 = Image.open((ImagePath + '/Test60s_40EM4.tif'))
#apply the median filter
image1.mode = 'I'
imageMed = image1.point(lambda i:i*(1./256)).convert('L').filter(ImageFilter.MedianFilter(size = 2))
FilteredPath = ImagePath+'/Test60s_40EM_med6.tif'
imageMed.save(FilteredPath)