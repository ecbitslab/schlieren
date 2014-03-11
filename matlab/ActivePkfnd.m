function out = ActivePkfnd(im,th,sz)
% Interactive version of pkfnd function
% 
% INPUTS
% See pkfnd
%
% OUTPUT
% 
% out: N x 2 array containing, [row,column] or [y, x] coordinates of local 
% maxima.
%
% CREATED: Sept 29, 2012
% 
% BEGIN CODE
% 
out = pkfnd(im,th,sz);
%Generates a figure of the image with peak locations overlayed as red +.
imagesc(im);
colormap(gray); 
hold on, plot(out(:,1),out(:,2),'r+');
%Prompts user, in Command Window, if they want to retry with different
%parameters.  This will continue until user specifies otherwise.
reply = input('Change Parameters? y/n : ', 's');
if isempty(reply)
    reply = 'y';
end
if reply == 'y'
    close
    clear out
    th = input('New Threshold : ');
    sz = input('New Diameter of Dot : ');
    active_pkfnd(im,th,sz);
elseif reply == 'n'
   close
end
end