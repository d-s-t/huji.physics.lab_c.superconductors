% raising current by 50 mili amper and checking V-hall

%function RT_meas
tic;
didCloseDevices=false;
try
    % Init:d
    tempResDevice= ConfigTemperature();
    sampleVoltageDevice=openGPIBDevice('agilent',7,22);
    sampleCurrentDevice=openGPIBDevice('agilent',7,19);
    coilCurrentDevice=openGPIBDevice('agilent',7,4);
%    tempResistance = readMeas(tempResDevice);
    %%% Coil-current init ( for H field generation):
    % Current limit:
    %fprintf(coilCurrentDevice,'CURRENT:PROTECTION 4');
    % Voltage limit:
    %fprintf(coilCurrentDevice,'VOLTAGE:PROTECTION:STATE 0');
    % Output ON, duh
    fprintf(coilCurrentDevice,'OUTPUT ON');
    
    %%% Sample-current init:
    % Slect the +6V output:
    %fprintf (sampleCurrentDevice,'INSTRUMENT P6V');
    % Output ON, duh
    fprintf(sampleCurrentDevice,'OUTPUT ON');
    
    % Field and sample-current values for execution:
    coilCurrent= 0; % Amps
    dCoil = 0.002 ;

    sampleCurrent=0.021; % Amps
    heatCurr=0;
    
    temp = zeros(1, 2*length(sampleCurrent));
    
    temp(1:2:length(temp)) = sampleCurrent;
    sampleCurrent=temp;
    
    pauseInterval=0.2; % Seconds
    
    %Saving to file in a chosen folder
    savePath='C:\Documents and Settings\owner\Desktop\New folder\'; %chosen folder
    fnamePattern='SupCondData';%File name
    fname=nextAvailableFilename(savePath,fnamePattern,'csv');
    header='Time(sec),TempRes(Ohm),SampVolt(V),SampCurr(A),CoilCurr(A)\n';
    file=fopen(fname,'w+');
    fprintf(file,header);
    fclose(file);
    
    fprintf(tempResDevice, 'READ?');%Reading Temperature in Ohms
    tempResistance = readMeas(tempResDevice);
    
    startTime=clock;
    fprintf(coilCurrentDevice,sprintf ('APPL %f, %f',15,coilCurrent));%Setting Field current
    fprintf(sampleCurrentDevice,sprintf ('INST P6V; CURR %f; INST P25V; CURR %f',sampleCurrent,heatCurr));
    flag=tempResistance>19;
    time=etime(clock,startTime);
    time_limit = 120000;
    figure
    hold on
    should_zero = 0;
    while(flag && (time<time_limit))
        % Set coil current:
        
        %pause(pauseInterval);
        
        %Set sample current:
        
        %fprintf(sampleCurrentDevice,sprintf ('APPL P6V, %f, %f',6,sampleCurrent(j)));
        pause(pauseInterval);
        time=etime(clock,startTime);
        
        % Read:
        fprintf(tempResDevice, 'READ?');
        tempResistance = readMeas(tempResDevice);
        
        fprintf(sampleVoltageDevice, 'READ?');
        sampleVoltage = readMeas(sampleVoltageDevice);
        
        
        
        
        fprintf(sampleCurrentDevice, 'INST P6V; CURRENT?');
        sampleCurrentMeas = readMeas(sampleCurrentDevice);
        
        if should_zero == 0
            fprintf(coilCurrentDevice,sprintf ('APPL %f, %f',15,coilCurrent));%Setting Field current
            coilCurrent = coilCurrent + dCoil;
            should_zero = should_zero + 1;
            
            if coilCurrent >= 0.25
                dCoil = 0.004 ;
            end
            if coilCurrent >= 1
                dCoil = 0.007 ;
            end
            if coilCurrent >= 1.5
                dCoil = 0.012 ;
            end
            if coilCurrent >= 2.5
                break
            end
        else
            should_zero = should_zero + 1;

            if should_zero == 3
                should_zero = 0;
            end
            fprintf(coilCurrentDevice,sprintf ('APPL %f, %f',15,0));%Setting Field current zero
        end

        fprintf(coilCurrentDevice, 'CURRENT?');
        coilCurrentMeas = readMeas(coilCurrentDevice);
        
        plot(tempResistance,sampleVoltage,'.')
        
        dlmwrite (fname,[time,tempResistance,...
            sampleVoltage,sampleCurrentMeas,...
            coilCurrentMeas],'-append');
        
        
        
        
        %save (fname,'time','tempRes','sampVolt','sampCurr','recordNumber');
        
        
        
        flag=tempResistance>19;
%         flag=flag+1;
        disp(sampleVoltage)
    end
    %setting the currents back to zero
    fprintf(sampleCurrentDevice,sprintf ('INST P6V; CURR %f; INST P25V; CURR %f',0,0));
    fprintf(coilCurrentDevice,'OUTPUT OFF');
catch err
    disp (err);
    
    fclose(tempResDevice);
    fclose(sampleVoltageDevice);
    fclose(sampleCurrentDevice);
    fclose(coilCurrentDevice);
    
    didCloseDevices=true;
    rethrow (err);
end
if (~didCloseDevices)
    fclose(tempResDevice);
    fclose(sampleVoltageDevice);
    fclose(sampleCurrentDevice);
    fclose(coilCurrentDevice);
    
end
disp ('Done!');
toc;
%end
