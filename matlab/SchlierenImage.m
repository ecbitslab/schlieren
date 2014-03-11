function SchlierenImage(peaks,shifts,condense,map)
% SchlierenImage plots the shifts, between the initial centroids' locations
% and their 'current' locations, at the coordinates of their corresponding 
% peak pixels. This image is then mutiplied by a condensing factor that
% smoothes it. This code is used in RealTimeSchlieren.
% 
% INPUTS
% 
% peaks:  Found using pkfnd
% 
% shifts: Found in RealTimeSchlieren, this is the shifts of each centroids
% in either the x or y direction
% 
% condense: Factor that condenses the image.  default is 0.1, but 0.7
% usually works well
% 
% map:  Color map.  HSV works well for shifts in y, and gray works best for
% shifts in x
% 
% CREATED: June 28, 2013
% 
% BEGIN CODE
% 
% setup default condition for condense
if condense == 0;
    condense = .1; 
end

% locate coordinates of 'highest' peak pixel 
hi = round(max(peaks)/(10*condense));
% initialize frame. frame is matrix in which the shifts will be placed
frame = zeros(hi(1),hi(2)); 
% run through each centroid and place its shift value in frame
for row = 1:size(peaks);
    frame(round(peaks(row,1)/(10*condense)),round(peaks(row,2)/ ...
        (10*condense))) = shifts(row);
end

imagesc(frame);colormap(map)
end