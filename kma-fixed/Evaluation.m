%--------------------------------------------------------------------------
% The code of the Evaluation function is adopted from W. Zhao et al. below.
% The six functions: F15, F19, F20, F21, F22, and F23 are slightly modified
% to visualize them in their two first dimensions
%
% GSA code v1.0.
% Developed in MATLAB R2011b
% The code is based on the following papers.
% W. Zhao, L. Wang and Z. Zhang, Atom search optimization and its 
% application to solve a hydrogeologic parameter estimation problem, 
% Knowledge-Based Systems,2019, 163:283-304, https://doi.org/10.1016/j.knosys.2018.08.030.
%
% W. Zhao, L. Wang and Z. Zhang, A novel atom search optimization for 
% dispersion coefficient estimation in groundwater, Future Generation 
% Computer Systems,2019,91:601-610, https://doi.org/10.1016/j.future.2018.05.037.
%--------------------------------------------------------------------------
% PATCHED COPY -- not the upstream release. The pristine v1.0.0 sources are kept
% in ../kma/ as the baseline. Changes are marked with "FIX Ax", see ../TEMUAN.md.
%--------------------------------------------------------------------------

 function fx = Evaluation(x)

 global FunctionID NumEva

 % FIX A4: every call to the objective function is one function evaluation.
 % The published code incremented NumEva by PopSize/SwarmSize per generation,
 % which undercounts the real number of evaluations by 11-20% and misses the
 % initial population and the second-stage ConsPop entirely.
 NumEva = NumEva + 1;

 Dim = length(x);
 
 switch FunctionID
     
%--------------------------------------------------------------------------
% Twenty three classic functions: F1 - F23
%--------------------------------------------------------------------------  

%%%%%%%%%%%%%%%%%%%%%%%%%%unimodal function%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%   
  
%Sphere
case 1
fx=sum(x.^2);

%Schwefel 2.22
case 2 
fx=sum(abs(x))+prod(abs(x));

%Schwefel 1.2
case 3
    fx=0;
    for i=1:Dim
        fx=fx+sum(x(1:i))^2;
    end

%Schwefel 2.21
case 4
    fx=max(abs(x));

%Rosenbrock
case 5
    fx=sum(100*(x(2:Dim)-(x(1:Dim-1).^2)).^2+(x(1:Dim-1)-1).^2);

%Step
case 6
    fx=sum(floor((x+.5)).^2);

%Quartic
case 7
    fx=sum([1:Dim].*(x.^4))+rand;


%%%%%%%%%%%%%%%%%%%%%%%%%%multimodal function%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%Schwefel
case 8
    fx=sum(-x.*sin(sqrt(abs(x))));

%Rastrigin
case 9
    fx=sum(x.^2-10*cos(2*pi.*x))+10*Dim;

%Ackley
case 10
    fx=-20*exp(-.2*sqrt(sum(x.^2)/Dim))-exp(sum(cos(2*pi.*x))/Dim)+20+exp(1);

%Griewank
case 11
    fx=sum(x.^2)/4000-prod(cos(x./sqrt([1:Dim])))+1;

%Penalized
case 12
  a=10;k=100;m=4;
  Dim=length(x);
  fx=(pi/Dim)*(10*((sin(pi*(1+(x(1)+1)/4)))^2)+sum((((x(1:Dim-1)+1)./4).^2).*...
        (1+10.*((sin(pi.*(1+(x(2:Dim)+1)./4)))).^2))+((x(Dim)+1)/4)^2)+sum(k.*...
        ((x-a).^m).*(x>a)+k.*((-x-a).^m).*(x<(-a)));

%Penalized2
case 13
  a=5;k=100;m=4;
  Dim=length(x);
  fx=.1*((sin(3*pi*x(1)))^2+sum((x(1:Dim-1)-1).^2.*(1+(sin(3.*pi.*x(2:Dim))).^2))+...
        ((x(Dim)-1)^2)*(1+(sin(2*pi*x(Dim)))^2))+sum(k.*...
        ((x-a).^m).*(x>a)+k.*((-x-a).^m).*(x<(-a)));

%%%%%%%%%%%%%%%%%%%%%%%%%%fixed-dimensionalmultimodalfunction%%%%%%%%%%%%%%

%Foxholes
% FIX A1: this case was labelled "case 16" in the published code. Foxholes is
% F14 (GetFunction.m sets Nvar=2, Ra=65, MV=0.998 for FunctionID 14). Because
% MATLAB runs the first matching case, F16 executed Foxholes instead of Six
% Hump Camel, and F14 matched no case at all, leaving fx unassigned.
case 14
  a=[-32 -16 0 16 32 -32 -16 0 16 32 -32 -16 0 16 32 -32 -16 0 16 32 -32 -16 0 16 32;...
  -32 -32 -32 -32 -32 -16 -16 -16 -16 -16 0 0 0 0 0 16 16 16 16 16 32 32 32 32 32];
    for j=1:25
        b(j)=sum((x'-a(:,j)).^6);
    end
    fx=(1/500+sum(1./([1:25]+b))).^(-1);

%Kowalik
case 15
    a=[.1957 .1947 .1735 .16 .0844 .0627 .0456 .0342 .0323 .0235 .0246];
    b=[.25 .5 1 2 4 6 8 10 12 14 16];b=1./b;
  if Dim == 2
      fx=sum((a-((x(1).*(b.^2+x(2).*b)))));
  else
      fx=sum((a-((x(1).*(b.^2+x(2).*b))./(b.^2+x(3).*b+x(4)))).^2);
 end
 
%Six Hump Camel
case 16
    fx=4*(x(1)^2)-2.1*(x(1)^4)+(x(1)^6)/3+x(1)*x(2)-4*(x(2)^2)+4*(x(2)^4);

%Branin
case 17
    fx=(x(2)-(x(1)^2)*5.1/(4*(pi^2))+5/pi*x(1)-6)^2+10*(1-1/(8*pi))*cos(x(1))+10;

%GoldStein-Price
case 18
    fx=(1+(x(1)+x(2)+1)^2*(19-14*x(1)+3*(x(1)^2)-14*x(2)+6*x(1)*x(2)+3*x(2)^2))*...
        (30+(2*x(1)-3*x(2))^2*(18-32*x(1)+12*(x(1)^2)+48*x(2)-36*x(1)*x(2)+27*(x(2)^2)));

%Hartman 3
case 19
  a=[3 10 30;.1 10 35;3 10 30;.1 10 35];c=[1 1.2 3 3.2];
  p=[.3689 .117 .2673;.4699 .4387 .747;.1091 .8732 .5547;.03815 .5743 .8828];
  fx=0;
  if Dim == 2
      for i=1:4
          fx=fx-c(i)*exp(-(sum(a(i,1:2).*((x-p(i,1:2)).^2))));
      end
  else
      for i=1:4
          fx=fx-c(i)*exp(-(sum(a(i,:).*((x-p(i,:)).^2))));
      end
  end

%Hartman 6
case 20
  af=[10 3 17 3.5 1.7 8;.05 10 17 .1 8 14;3 3.5 1.7 10 17 8;17 8 .05 10 .1 14];
  cf=[1 1.2 3 3.2];
  pf=[.1312 .1696 .5569 .0124 .8283 .5886;.2329 .4135 .8307 .3736 .1004 .9991;...
  .2348 .1415 .3522 .2883 .3047 .6650;.4047 .8828 .8732 .5743 .1091 .0381];
  fx=0;
  
  if Dim == 2
      for i=1:4
          fx=fx-cf(i)*exp(-(sum(af(i,1:2).*((x-pf(i,1:2)).^2))));
      end
  else
      for i=1:4
          fx=fx-cf(i)*exp(-(sum(af(i,:).*((x-pf(i,:)).^2))));
      end
  end
  
%Shekel 5
case 21
  a=[4 4 4 4;1 1 1 1;8 8 8 8;6 6 6 6;3 7 3 7;2 9 2 9;5 5 3 3;8 1 8 1;6 2 6 2;7 3.6 7 3.6];
  c=[0.1 0.2 0.2 0.4 0.4 0.6 0.3 0.7 0.5 0.5];
  fx=0;
  
  if Dim == 2
      for i=1:5
          fx=fx-1/((x-a(i,1:2))*(x-a(i,1:2))'+c(i));
      end
  else
      for i=1:5
          fx=fx-1/((x-a(i,:))*(x-a(i,:))'+c(i));
      end
  end  

%Shekel 7
case 22
  a=[4 4 4 4;1 1 1 1;8 8 8 8;6 6 6 6;3 7 3 7;2 9 2 9;5 5 3 3;8 1 8 1;6 2 6 2;7 3.6 7 3.6];
  c=[0.1 0.2 0.2 0.4 0.4 0.6 0.3 0.7 0.5 0.5];
  fx=0;  
  if Dim == 2
      for i=1:7
          fx=fx-1/((x-a(i,1:2))*(x-a(i,1:2))'+c(i));
      end
  else
      for i=1:7
          fx=fx-1/((x-a(i,:))*(x-a(i,:))'+c(i));
      end
  end  
  
%Shekel 10
case 23
  a=[4 4 4 4;1 1 1 1;8 8 8 8;6 6 6 6;3 7 3 7;2 9 2 9;5 5 3 3;8 1 8 1;6 2 6 2;7 3.6 7 3.6];
  c=[0.1 0.2 0.2 0.4 0.4 0.6 0.3 0.7 0.5 0.5];
  fx=0;
  if Dim == 2
      for i=1:10
          fx=fx-1/((x-a(i,1:2))*(x-a(i,1:2))'+c(i));
      end
  else
      for i=1:10
          fx=fx-1/((x-a(i,:))*(x-a(i,:))'+c(i));
      end
  end  
end