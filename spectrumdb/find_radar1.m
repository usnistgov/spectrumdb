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
