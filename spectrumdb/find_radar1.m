function retval = find_radar1(datasetName,varargin)
% Return a list of TDMS files having radar1 identified and satisfying the given constraints.
%
%     Mandatory Parameters: 
%         - datasetName : The name of the dataset
%
%     Property value pair Parameters:
%         (Specify these as comma separated name value pairs)
%         - fc_mhz : the center frequency in mhz (default value = 3550)
%         - radar3 : (Y/N) whether or not to look for radar 3 
%                       (default is "U" undefined)
%         - minSnr = the minimum SNR value (default is 6)
%         - startDate : The start date.'%Y-%m-%d %H:%M:%S' format (default
%                       is 'U' Undefined)
%         - endDate : The end date '%Y-%m-%d %H:%M:%S' format (default is
%                        'U' Undefined)
% 
%     Return:
%         A list of TDMS files matching the query criteria.
%
%     Example:
%       find_radar1('SanDiego','fc_mhz',3570,'radar3','N')
%       ans = 'E:\TDMS_Files\VST11Apr16_093038.tdms'

    params.fc_mhz = 3550;
    params.radar3 = 'U';
    params.startDate = 'U';
    params.endDate = 'U';
    params.minSnr= 6;
    params=parse_pv_pairs(params,varargin); 
    tdmsFiles = py.spectrumdb.querydb.find_radar1(datasetName,...
            params.fc_mhz,params.radar3,params.minSnr, ...
            params.startDate,params.endDate);
    % Convert from python array to MATLAB array
    retval = cell(1,numel(tdmsFiles));
    for n=1:numel(tdmsFiles)
        strP = char(tdmsFiles{n});
        retval(n) = {strP};
    end
        
        
end
