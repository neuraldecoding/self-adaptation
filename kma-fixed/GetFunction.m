%=================================================================================
% Komodo Mlipir Algorithm (KMA) version 1.0.0
%
% Developed in MATLAB R2017a based on the following paper:
%
% S. Suyanto, A.A. Ariyanto, A.F. Ariyanto, Komodo Mlipir Algorithm 
% Applied Soft Computing, 2021, 108043, https://doi.org/10.1016/j.asoc.2021.108043
%
% This code is used to get the information of the benchmark function
% selected by the user: FunctionID and Dimension
%
% Updated 23 November 2021 by Prof. Dr. Suyanto, S.T., M.Sc.
% School of Computing, Telkom University
% Jl. Telekomunikasi No 1 Terusan Buah Batu, Bandung 40257, Indonesia
% Email: suyanto@telkomuniversity.ac.id 
% Website: https://suyanto.staff.telkomuniversity.ac.id
%=================================================================================

function [Nvar,Ra,Rb,MV] = GetFunction

global FunctionID Dimension

Nvar = Dimension;  % DEFAULT number of variables for function F1 - F13

%--------------------------------------------------------------------------
% Twenty three classic functions: F1 - F23
%--------------------------------------------------------------------------  
if FunctionID == 1      % Minimum = 0
    Ra   =  100;        % Upper bound of the interval
    Rb   = -100;        % Lower bound of the interval
    MV   = 0;           % The minimum value of the function
elseif FunctionID == 2  % Minimum = 0
    Ra   =  10;         % Upper bound of the interval
    Rb   = -10;         % Lower bound of the interval    
    MV   = 0;           % The minimum value of the function
elseif FunctionID == 3  % Minimum = 0
    Ra   =  100;        % Upper bound of the interval
    Rb   = -100;        % Lower bound of the interval    
    MV   = 0;           % The minimum value of the function
elseif FunctionID == 4  % Minimum = 0
    Ra   =  100;        % Upper bound of the interval
    Rb   = -100;        % Lower bound of the interval    
    MV   = 0;           % The minimum value of the function
elseif FunctionID == 5  % Minimum = 0
    Ra   =  30;         % Upper bound of the interval
    Rb   = -30;         % Lower bound of the interval    
    MV   = 0;           % The minimum value of the function
elseif FunctionID == 6  % Minimum = 0
    Ra   =  100;        % Upper bound of the interval
    Rb   = -100;        % Lower bound of the interval    
    MV   = 0;           % The minimum value of the function
elseif FunctionID == 7  % Minimum = 0
    Ra   =   1.28;      % Upper bound of the interval
    Rb   =  -1.28;      % Lower bound of the interval    
    MV   = 0;           % The minimum value of the function
elseif FunctionID == 8  % Minimum = -418.9829 x 10^30
    Ra   =  500;        % Upper bound of the interval
    Rb   = -500;        % Lower bound of the interval    
    MV   = -418.9829 * Nvar;      % The minimum value of the function
elseif FunctionID == 9  % Minimum = 0
    Ra   =   5.12;      % Upper bound of the interval
    Rb   =  -5.12;      % Lower bound of the interval    
    MV   = 0;           % The minimum value of the function
elseif FunctionID == 10 % Minimum = 0
    Ra   =  32;         % Upper bound of the interval
    Rb   = -32;         % Lower bound of the interval    
    MV   = 0;           % The minimum value of the function
elseif FunctionID == 11 % Minimum = -418.9829 x 10^30
    Ra   =  600;        % Upper bound of the interval
    Rb   = -600;        % Lower bound of the interval    
    MV   = 0;           % The minimum value of the function
elseif FunctionID == 12 % Minimum = 0
    Ra   =  50;         % Upper bound of the interval
    Rb   = -50;         % Lower bound of the interval    
    MV   = 0;           % The minimum value of the function
elseif FunctionID == 13 % Minimum = 0
    Ra   =  50;         % Upper bound of the interval
    Rb   = -50;         % Lower bound of the interval    
    MV   = 0;           % The minimum value of the function
elseif FunctionID == 14 % Minimum = 0.998
    Nvar =   2;         % Number of variables in the function
    Ra   =  65;         % Upper bound of the interval
    Rb   = -65;         % Lower bound of the interval    
    MV   = 0.998;       % The minimum value of the function
elseif FunctionID == 15 % Minimum = 0.0003
    Nvar =   4;         % Number of variables in the function
    Ra   =   5;         % Upper bound of the interval
    Rb   =  -5;         % Lower bound of the interval    
    MV   = 0.0003;      % The minimum value of the function
elseif FunctionID == 16 % Minimum = -1.0316
    Nvar =   2;         % Number of variables in the function
    Ra   =   5;         % Upper bound of the interval
    Rb   =  -5;         % Lower bound of the interval    
    MV   = -1.0316;     % The minimum value of the function
elseif FunctionID == 17 % Minimum = 0.398
    Nvar =   2;         % Number of variables in the function
    Ra   =   5;         % Upper bound of the interval
    Rb   =  -5;         % Lower bound of the interval    
    MV   = 0.398;       % The minimum value of the function
elseif FunctionID == 18 % Minimum = 3
    Nvar =   2;         % Number of variables in the function
    Ra   =   2;         % Upper bound of the interval
    Rb   =  -2;         % Lower bound of the interval    
    MV   =   3;         % The minimum value of the function
elseif FunctionID == 19 % Minimum = -3.86
    Nvar =   3;         % Number of variables in the function
    Ra   =   1;         % Upper bound of the interval
    Rb   =   0;         % Lower bound of the interval    
    MV   = -3.86;       % The minimum value of the function
elseif FunctionID == 20 % Minimum = -3.32
    Nvar =   6;         % Number of variables in the function
    Ra   =   1;         % Upper bound of the interval
    Rb   =   0;         % Lower bound of the interval    
    MV   = -3.32;       % The minimum value of the function
elseif FunctionID == 21 % Minimum = -10.1532
    Nvar =   4;         % Number of variables in the function
    Ra   =  10;         % Upper bound of the interval
    Rb   =   0;         % Lower bound of the interval    
    MV   = -10.1532;    % The minimum value of the function
elseif FunctionID == 22 % Minimum = -10.4029
    Nvar =   4;         % Number of variables in the function
    Ra   =  10;         % Upper bound of the interval
    Rb   =   0;         % Lower bound of the interval    
    MV   = -10.4029;    % The minimum value of the function
elseif FunctionID == 23 % Minimum = -10.5364
    Nvar =   4;         % Number of variables in the function
    Ra   =  10;         % Upper bound of the interval
    Rb   =   0;         % Lower bound of the interval   
    MV   = -10.5364;    % The minimum value of the function
end