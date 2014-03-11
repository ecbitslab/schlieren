function indices = IndexMatrix(peaks,height)
% This function is used RealTimeSchlieren.  Using the peak pixel coordinates
% and the height of a frame of data, this function finds the indices of the
% 3x3 pixel boxes surrounding each peak pixel.
% 
% INPUTS
% 
% peaks: Found using pkfnd, peaks is the coordinates of the peak pixels.
% 
% height:  The height of a frame of data.
% 
% OUTPUTS
% 
% indices: Matrix containing the indices of the 3x3 pixel boxes surrounding
% each peak pixel.  Each row corresponds the a set of 9 pixels' indices,
% where the central column contains the indices of the peak pixels.
% 
% CREATED: June 28, 2013
% 
% BEGIN CODE
% 
% find number of peaks and initialize indices matrix
peakcount = size(peaks,1);
indices = zeros(peakcount,9);

% run through each peak pixel and using a simple algorithm convert
% coordinates to indices
for ii = 1:peakcount;
    colnum = peaks(ii,1);
    rownum = peaks(ii,2);
    indices(ii,1) = rownum - 1 + (colnum - 2) * height;
    indices(ii,2) = rownum - 1 + (colnum - 1) * height;
    indices(ii,3) = rownum - 1 + (colnum) * height;
    indices(ii,4) = indices(ii,1) + 1;
    indices(ii,5) = indices(ii,2) + 1;
    indices(ii,6) = indices(ii,3) + 1;
    indices(ii,7) = indices(ii,1) + 2;
    indices(ii,8) = indices(ii,2) + 2;
    indices(ii,9) = indices(ii,3) + 2;
end
end