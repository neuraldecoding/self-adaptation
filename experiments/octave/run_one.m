% Verification driver: run one KMA configuration headlessly under Octave.
%
%   octave-cli run_one.m <codedir> <FunctionID> <Dimension> <seed>
%
% Prints one line of key=value pairs so the caller can parse it. Uses KMA2D
% (never KMA3D) because KMA3D opens figures.
args = argv();
codedir = args{1};
fid     = str2double(args{2});
dim     = str2double(args{3});
seed    = str2double(args{4});

addpath(fileparts(mfilename('fullpath')));   % the random() shim
addpath(codedir);

global FunctionID Dimension Nvar Ra Rb FthresholdFX
global PopSize MinAdaPopSize MaxAdaPopSize MaxNumEva
global EvalCount

FunctionID    = fid;
Dimension     = dim;
MaxNumEva     = 25000;
PopSize       = 5;
MinAdaPopSize = PopSize * 4;
MaxAdaPopSize = PopSize * 40;

rand('state', seed);
randn('state', seed);

[Nvar,Ra,Rb,FthresholdFX] = GetFunction;
Ra = ones(1,Nvar) .* Ra;
Rb = ones(1,Nvar) .* Rb;

try
    [BestIndividual,OptVal,NumEva,fopt,fmean,ProcTime,EvoPopSize] = KMA2D;
    printf('status=ok fid=%d seed=%d opt=%.10g numeva=%d gens=%d time=%.2f\n', ...
           fid, seed, OptVal, NumEva, numel(fopt), ProcTime);
catch err
    printf('status=error fid=%d seed=%d msg=%s\n', fid, seed, strrep(err.message, "\n", ' '));
end
