function dispSpectrogramFolder(path,fLO,gaindB,fc,tdmsListFile)
% Plot spectrograms of metadata in a given folder.
% Inputs
%   path:    path to folder containing metadata
%   fLO:     local oscillator frequency (MHz)
%   gaindB:  net of front end gain, cable loss, splitter loss
%   fc:      center frequency (MHz) around which to max-hold in time (optional)
%   tdmsListFile:    name of text file with list of TDMS files (optional)
%
% Sample usage:
%     >> dispSpectrogramFolder('C:\Virginia Beach\Metadata\30Aug2016_1405_CBS\MaxSpectra',3577,22.5)
% 
%     Right arrow:  go to the next spectrogram
%     Left arrow:  previous spectrogram
%     ‘Home’:  jump to first spectrogram
%     ‘End’:  jump to last spectrogram
%     Single digit [1-9]:  advance that many spectrograms
%     ‘Alt’ + single digit [1-9]:  rewind that many spectrograms

numSpectra=134;

% correct for gain of the amplifier
Vgain=10^(gaindB/20);   % convert amplifier gain to linear units
VcaldB=1.64;            % VST calibration in dB
Vcal=10^(VcaldB/20);

if nargin < 4
    fc=0;
end

fig=figure('KeyPressFcn',{@dispNextSpectrogram,fLO,numSpectra,Vgain,Vcal,fc});

fileList=dir([path,'\*.tsv']);
[tmp indsort]=sort([fileList.datenum]);
fileList=fileList(indsort);

if nargin == 5
    % select only the tsv files having TDMS files in the provided list
    tdmsList=textread([path,'\',tdmsListFile],'%17c.tdms');
    tsvList=[tdmsList repmat('_MaxSpectra.tsv',size(tdmsList,1),1)];
    tsvInd=ismember(char({fileList.name}),tsvList,'rows');
    fileList=fileList(tsvInd);
end

fprintf('%d files found\n\n',length(fileList))

ind=1;
dispSpectrogram(path,fileList(ind).name,fLO,numSpectra,Vgain,Vcal,fc)

    function dispNextSpectrogram(src,event,fLO,numSpectra,Vgain,Vcal,fc)
        % advance by the arrow or number entered
        if strcmp(event.Key,'rightarrow')
            ind=ind+1;
        elseif strcmp(event.Key,'leftarrow')
            ind=ind-1;
        elseif strcmp(event.Key,'home')
            ind=1;
        elseif strcmp(event.Key,'end')
            ind=length(fileList);
        elseif str2num(event.Character)
            delta=str2num(event.Character);
            if length(event.Modifier) == 1 && strcmp(event.Modifier{:},'alt')
                ind=ind-delta;
            else
                ind=ind+delta;
            end
        end
        if ind < 1
            ind=1;
        elseif ind > length(fileList)
            ind=length(fileList);
        end
        dispSpectrogram(path,fileList(ind).name,fLO,numSpectra,Vgain,Vcal,fc)
    end

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
        
%         % compute statistics at multiples of 10 MHz
%         fi=[3500:10:3650];
%         Fi=repmat(fi',1,length(fMHz));
%         FMHz=repmat(fMHz,length(fi),1);
%         [temp, i]=min(abs(FMHz-Fi),[],2);   % i is the vector of bin indices
%         zisq=z(:,i).^2;
%         zsq_avg=mean(zisq,1);
%         zsq_75=quantile(zisq,0.75,1);
%         zsq_25=quantile(zisq,0.25,1);
%         fprintf(filename(1:17)); fprintf('\n');
%         fprintf('freq (MHz):    '); fprintf('%d ',fi); fprintf('\n');
%         fprintf('mean (dBm):    '); fprintf('%4.0f ',10.*log10(zsq_avg)-10*log10(100)+30); fprintf('\n');
%         fprintf('Q75-Q25 (dBm): '); fprintf('%4.0f ',10.*log10(zsq_75)-10*log10(zsq_25)); fprintf('\n\n');
    end
end