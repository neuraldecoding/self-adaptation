% Shim for verification with GNU Octave only.
%
% kma/levy.m calls random('Normal',mu,sigma,n,m), which lives in the MATLAB
% Statistics and Machine Learning Toolbox. Octave provides it only through the
% "statistics" package. This shim implements exactly the one call form that
% levy.m needs, so the audited sources in kma/ and kma-fixed/ can run unmodified.
% It is NOT part of KMA and must never be placed on the path in MATLAB.
function z = random(name, mu, sigma, n, m)
if ~strcmpi(name, 'Normal')
    error('random shim: only the Normal distribution is implemented');
end
z = mu + sigma .* randn(n, m);
