% This software was developed by employees of the National Institute
% of Standards and Technology (NIST), an agency of the Federal
% Government. Pursuant to title 17 United States Code Section 105, works
% of NIST employees are not subject to copyright protection in the United
% States and are considered to be in the public domain. Permission to freely
% use, copy, modify, and distribute this software and its documentation
% without fee is hereby granted, provided that this notice and disclaimer
% of warranty appears in all copies.
%
% THE SOFTWARE IS PROVIDED 'AS IS' WITHOUT ANY WARRANTY OF ANY KIND,
% EITHER EXPRESSED, IMPLIED, OR STATUTORY, INCLUDING, BUT NOT LIMITED
% TO, ANY WARRANTY THAT THE SOFTWARE WILL CONFORM TO SPECIFICATIONS, ANY
% IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE,
% AND FREEDOM FROM INFRINGEMENT, AND ANY WARRANTY THAT THE DOCUMENTATION
% WILL CONFORM TO THE SOFTWARE, OR ANY WARRANTY THAT THE SOFTWARE WILL BE
% ERROR FREE. IN NO EVENT SHALL NASA BE LIABLE FOR ANY DAMAGES, INCLUDING,
% BUT NOT LIMITED TO, DIRECT, INDIRECT, SPECIAL OR CONSEQUENTIAL DAMAGES,
% ARISING OUT OF, RESULTING FROM, OR IN ANY WAY CONNECTED WITH THIS
% SOFTWARE, WHETHER OR NOT BASED UPON WARRANTY, CONTRACT, TORT, OR
% OTHERWISE, WHETHER OR NOT INJURY WAS SUSTAINED BY PERSONS OR PROPERTY
% OR OTHERWISE, AND WHETHER OR NOT LOSS WAS SUSTAINED FROM, OR AROSE OUT
% OF THE RESULTS OF, OR USE OF, THE SOFTWARE OR SERVICES PROVIDED HEREUNDER.
%
% Distributions of NIST software should also include copyright and licensing
% statements of any third-party software that are legally bundled with
% the code in compliance with the conditions of those licenses.


function dispSpectrogram(path,filename,fLO,numSpectra,Vgain,Vcal,fc)
        
        fname=[path,'\',filename];
        
        %tick_vec=linspace(-1.25e2,1.25e2,11)+fLO;  %scales tics on horizontal axis
        
        temp=dlmread(fname,'\t');
        z=temp./1024;
        
        z=z/Vgain;  % Apply calibrations for front end gain, cable loss, splitter loss
        z=z*Vcal;   % Apply calibration for VST gain error
        
        z_len=length(z(:,1));
        
        fMHz=(225/1024)*(-512:511)+fLO;
        z_dBm=20.*log10(z)-10*log10(100)+30;
        subplot(2,2,[1 3]); surf(fMHz,(1024/2250)*(1:numSpectra),z_dBm);  %plot spectrogram
        shading interp
        axis([fMHz(1) fMHz(end) 0 numSpectra*1024/2250])
        %set(gca, 'XTick',tick_vec);
        xlabel('Frequency (MHz)')
        ylabel('Time (s)')
        title(filename(1:17), 'Interpreter', 'none')
        view(0,90)
        
        colorbar
        drawnow
        
        subplot(2,2,2); plot(fMHz,max(z_dBm));
        xlim([fMHz(1) fMHz(end)]);
        set(gca,'YGrid','on');
        xlabel('Frequency (MHz)');
        ylabel('Max-hold (dBm)');
        title(filename(1:17), 'Interpreter', 'none')
        
        if fc==0
            % set fc to frequency of peak power between 3520 MHz and fLO+100 MHz, excluding the LO
            fj=find((fMHz >= 3520) & (fMHz <= fLO+100) & ((fMHz < fLO-1) | (fMHz > fLO+1)));
            [pmax fci]=max(max(z_dBm(:,fj)));
            fMHz_j=fMHz(fj);
            fc=round(fMHz_j(fci));
        end
        fi=find((fMHz > fc-2.5) & (fMHz < fc+2.5));
        subplot(2,2,4); plot((1024/2250)*(1:numSpectra),max(z_dBm(:,fi),[],2));
        set(gca,'YGrid','on');
        xlim([0 numSpectra*1024/2250]);
        xlabel('Time (s)');
        ylabel(sprintf('Max-hold near %g MHz (dBm)',fc));
    end
