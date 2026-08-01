% Replays the AllHQ row indexing of the second stage (finding A2) with real
% Octave/MATLAB array semantics, using the sizes KMA actually runs with:
% MaxAdaPopSize = 200, SwarmSize = 5, NumBM = 2 -> 40 micro-swarms, 80 rows.
SwarmSize = 5; NumBM = 2; AdaPopSize = 200; Nvar = 50;

% first loop of KMA2D.m builds AllHQ with NumBM rows per micro-swarm
AllHQ = ones(AdaPopSize/SwarmSize*NumBM, Nvar);   % 80 real big males
printf('built    : rows=%3d  all-zero rows=%2d\n', rows(AllHQ), sum(all(AllHQ==0,2)));

% second loop, published indexing (kma/KMA2D.m:174)
A = AllHQ;
for ind = 1:SwarmSize:AdaPopSize
    A(ind:ind+NumBM-1,:) = ones(NumBM,Nvar);
end
printf('published: rows=%3d  all-zero rows=%2d  <- phantom individuals at the origin\n', ...
       rows(A), sum(all(A==0,2)));

% second loop, fixed indexing (kma-fixed/KMA2D.m)
B = AllHQ;
for ind = 1:SwarmSize:AdaPopSize
    IndHQ = ((ind-1)/SwarmSize)*NumBM + 1;
    B(IndHQ:IndHQ+NumBM-1,:) = ones(NumBM,Nvar);
end
printf('fixed    : rows=%3d  all-zero rows=%2d\n', rows(B), sum(all(B==0,2)));
