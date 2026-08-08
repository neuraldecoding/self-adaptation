% Probe the population-size trajectory of a KMA run.
%
%   octave-cli selfadapt_probe.m <codedir> <FunctionID> <Dimension> <seed>
%
% KMA2D returns EvoPopSize: the population size recorded in each generation.
% Stage one always records the fixed PopSize (5); stage two records AdaPopSize
% after the self-adaptation block has run. This driver reports the trajectory
% without touching the audited sources.
args = argv();
codedir = args{1};
fid     = str2double(args{2});
dim     = str2double(args{3});
seed    = str2double(args{4});

addpath(fileparts(mfilename('fullpath')));
addpath(codedir);

global FunctionID Dimension Nvar Ra Rb FthresholdFX
global PopSize MinAdaPopSize MaxAdaPopSize MaxNumEva
global EvalCount

FunctionID = fid;  Dimension = dim;  MaxNumEva = 25000;  PopSize = 5;
MinAdaPopSize = PopSize * 4;  MaxAdaPopSize = PopSize * 40;
rand('state', seed);  randn('state', seed);

[Nvar,Ra,Rb,FthresholdFX] = GetFunction;
Ra = ones(1,Nvar) .* Ra;
Rb = ones(1,Nvar) .* Rb;

[BestIndividual,OptVal,NumEva,fopt,fmean,ProcTime,EvoPopSize] = KMA2D;

s1 = sum(EvoPopSize == 5);          % generations recorded by the first stage
s2 = EvoPopSize(s1+1:end);          % adaptive sizes recorded by the second stage
if isempty(s2)
    printf(['fid=%d seed=%d stage1_gens=%d stage2_gens=0 ' ...
            'never_reached_stage2\n'], fid, seed, s1);
else
    d    = diff(s2);
    down = sum(d < 0);              % cabang "n - a" pada Eq. (10)
    up   = sum(d > 0);              % cabang "n + a" pada Eq. (10)
    printf(['fid=%d seed=%d stage1_gens=%d stage2_gens=%d ' ...
            'first=%d last=%d min=%d max=%d down=%d up=%d gens_at_max=%d\n'], ...
           fid, seed, s1, numel(s2), s2(1), s2(end), min(s2), max(s2), ...
           down, up, sum(s2 == MaxAdaPopSize));
end
