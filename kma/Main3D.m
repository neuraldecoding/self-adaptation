%=================================================================================
% Komodo Mlipir Algorithm (KMA) version 1.0.0
%
% Developed in MATLAB R2017a based on the following paper:
%
% S. Suyanto, A.A. Ariyanto, A.F. Ariyanto, Komodo Mlipir Algorithm 
% Applied Soft Computing, 2021, 108043, https://doi.org/10.1016/j.asoc.2021.108043
%
% Main program with 3D Visualization
% 
% Parameters:
% 1. FunctionID    : Identity of the benchmark function
% 2. Dimension     : dimension of the function to optimize
% 3. MaxNumEva     : Maximum Number of Evaluations
% 4. PopSize       : Population Size (number of Komodo individuals)
% 5. MinAdaPopSize : Minimum Adaptive PopSize
% 6. MaxAdaPopSize : Maximum Adaptive PopSize
%
% Updated 23 November 2021 by Prof. Dr. Suyanto, S.T., M.Sc.
% School of Computing, Telkom University
% Jl. Telekomunikasi No 1 Terusan Buah Batu, Bandung 40257, Indonesia
% Email: suyanto@telkomuniversity.ac.id 
% Website: https://suyanto.staff.telkomuniversity.ac.id
%=================================================================================

clc
clear
close all

global FunctionID Dimension Nvar Ra Rb FthresholdFX
global PopSize MinAdaPopSize MaxAdaPopSize MaxNumEva

%% Set of parameters
FunctionID    = 1;             % Identity of the bencmark function
Dimension     = 50;            % Dimension can be scaled up to millions for F1-F13, but only two first dimensions is visualized
MaxNumEva     = 25000;         % Maximum number of evaluations
PopSize       = 5;             % Population Size (number of Komodo individuals)
MinAdaPopSize = PopSize * 4;   % Minimum Adaptive PopSize
MaxAdaPopSize = PopSize * 40;  % Maximum Adaptive PopSize

%% Get a benchmark function and call KMA to get its global optimum solution
[Nvar,Ra,Rb,FthresholdFX] = GetFunction;
Ra = ones(1,Nvar) .* Ra;
Rb = ones(1,Nvar) .* Rb;

[BestIndividual,OptVal,NumEva,fopt,fmean,ProcTime,EvoPopSize] = KMA3D;

%% Report the result of KMA
disp(['Function              = F' num2str(FunctionID)])
disp(['Dimension             = ' num2str(Dimension)])
disp(['Number of evaluations = ' num2str(NumEva)])
disp(['Processing time (sec) = ' num2str(ProcTime)])
disp(['Global optimum        = ' num2str(FthresholdFX,10)])
disp(['Actual solution       = ' num2str(OptVal,10)])
disp(['Best individual       = ' num2str(BestIndividual)])

%% Visualize the convergence curve of KMA
set(figure, 'position', [100,100,1000,600]);
hold on
plot(fopt,'r-')
plot(fmean,'b--')
title(['Convergence curve of Function F',num2str(FunctionID)]);
xlabel('Generation');
ylabel('Fitness');
legend('Best fitness','Mean fitness')
hold off

%% Visualize the log convergence curve of KMA
if fopt(end) >= 0
    set(figure, 'position', [100,100,1000,600]);
    hold on
    plot(log10(fopt),'r-')
    plot(log10(fmean),'b--')
    title(['Log convergence curve of Function F',num2str(FunctionID)]);
    xlabel('Generation');
    ylabel('Log Fitness');
    legend('Best fitness','Mean fitness')
    hold off
end

%% Visualize the fixed and self-adaptation of population size of KMA
set(figure, 'position', [100,100,1000,600]);
plot(EvoPopSize)
axis([1 length(EvoPopSize) 0 MaxAdaPopSize+5]);
title(['Fixed and self-adaptive population size in the first and second stage for Function F',num2str(FunctionID)]);
xlabel('Generation');
ylabel('Population size (Number of individuals)');