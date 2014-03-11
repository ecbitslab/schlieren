function [x_shifts, y_shifts] = RealTimeSchlieren(camera,ID,axis,condense,map) 
% 
% INPUTS
% 
% camera:  Video source's name as designated by MATLAB e.g. 'winvideo'
% 
% ID: Video source's ID as designated by MATLAB e.g. 1
% 
% axis: Direction of shifts i.e x or y axis.  This needs to be either a 1
% or 2. 1 being shifts in the x direction and 2 being shifts in the y
% direction.
% 
% condense: factor that condenses the schlieren image.  0.7 works pretty
% well.
% 
% map:  Color map for schlieren image.
%
% OUTPUTS
% 
% x_shifts: Matrix which consists of the initial centroid coordinates in the
% first two columns and the shifts of each centroid in the x direction in the
% rest of its columns.
%
% y_shifts: Same as x_shifts except the shifts correspond to the shifts in
% the y direction.
% 
% CREATED: June 28, 2013
% 
% BEGIN CODE
% 
% Camera set-up
src = videoinput(camera,ID);
set(src,'FramesPerTrigger',1,'ReturnedColorSpace','grayscale');
% Grab initial background image
start(src);wait(src);
stop(src);

frame = getdata(src,1);
% Find peaks in background image
peaks = ActivePkfnd(frame,20,5);
% Construct matrix of peak indices
height = size(frame,1);
indices = IndexMatrix(peaks,height);

% Locate initial centroids' locations
centroids = CentroidLocator(frame,peaks,indices);
x_shifts = centroids;
y_shifts = centroids;

% Set-up for schlieren frames
set(src,'FramesPerTrigger',Inf);
start(src);

KeyIsPressed = 0;
gcf
set(gcf,'KeyPressFcn', @EndLoop)

function EndLoop(hObject, event)
	KeyIsPressed = 1;
end

while ~KeyIsPressed
    % Grab frame for schlieren processing
    frame = getdata(src,1);
    % Find new position of centroids
    locs = CentroidLocator(frame,peaks,indices); 
    % Calculate shifts between centroids' locations
    shifts = locs(:, axis) - centroids(:, axis);
    y_shifts(:, src.FrameNumber) = locs(:, 1) - centroids(:, 1);
    x_shifts(:, src.FrameNumber) = locs(:, 2) - centroids(:, 2);
    % Using shifts create a schlieren image
    SchlierenImage(peaks,shifts,condense,map);
end
stop(src)
close(src);
end