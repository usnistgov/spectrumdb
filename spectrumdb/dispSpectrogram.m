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