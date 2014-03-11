function centroids = CentroidLocator(frame,peaks,indices)  
% Using a frame of data, the coordinates of its peak pixels, and the
% indices of the 3x3 box around each peak pixel, CentroidLocator finds the
% centroids in the frame.  This function is used with RealTimeSchlieren.
% 
% INPUTS
% 
% frame: A frame of data in double and grayscale
% 
% peaks: The coordinates of the peak pixels found using active_pkfnd
% 
% indices:  Matrix containing the indices of the 3x3 pixel boxes
% surrounding each peak pixel
% 
% OUTPUTS
% 
% centroids:  Matrix containing the coordinates of the centroids near each
% peak pixel.
% 
% CREATED: June 28, 2013
% 
% BEGIN CODE:
% 
% find number of peaks and initialize centroids matrix
peakcount = size(peaks,1);
centroids = zeros(peakcount,2);
% run through each peak and use our averaging algorithm calculate the
% locations of each centroid
for ii = 1:peakcount
    colnum = peaks(ii,1);
    rownum = peaks(ii,2);

    % 3x3 total intensity 
    I_tot = frame(indices(ii,1));
    I_tot = I_tot + frame(indices(ii,2));
    I_tot = I_tot + frame(indices(ii,3));
    I_tot = I_tot + frame(indices(ii,4));
    I_tot = I_tot + frame(indices(ii,5));
    I_tot = I_tot + frame(indices(ii,6));
    I_tot = I_tot + frame(indices(ii,7));
    I_tot = I_tot + frame(indices(ii,8));
    I_tot = I_tot + frame(indices(ii,9));
    
    % x weighted intensity
    x_sum = frame(indices(ii,3));
    x_sum = x_sum + frame(indices(ii,6));
    x_sum = x_sum + frame(indices(ii,9));
    x_sum = x_sum - frame(indices(ii,1));
    x_sum = x_sum - frame(indices(ii,4));
    x_sum = x_sum - frame(indices(ii,7));
    
    % y weighted intensity
    y_sum = frame(indices(ii,1));
    y_sum = y_sum + frame(indices(ii,2));
    y_sum = y_sum + frame(indices(ii,3));
    y_sum = y_sum - frame(indices(ii,7));
    y_sum = y_sum - frame(indices(ii,8));
    y_sum = y_sum - frame(indices(ii,9));
    
    % centroid locations
    centroids(ii,1) = x_sum/I_tot + colnum; % centroid x coordinate
    centroids(ii,2) = y_sum/I_tot + rownum; % centroid y coordinate
end
end