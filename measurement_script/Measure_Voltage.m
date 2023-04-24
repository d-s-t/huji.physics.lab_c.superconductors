close all;
MINIMUM_TEMPERATURE=80;
SAVE_PATH = '.\2nd_day\fourprobe\';

temperature_table = load('temperature_conversion.mat', 'table');
temperature_table = temperature_table.table;

%function RT_meas
tic;
didCloseDevices=false;

%  sampleCurrent=1; % Amps
try
    % Init:
    tempResDevice = ConfigTemperature();
    sampleVoltageDevice=openGPIBDevice('agilent',7,22);
    sampleCurrentDevice=openGPIBDevice('agilent',7,19);
    coilCurrentDevice=openGPIBDevice('agilent',7,4);
    % Output ON, duh
    fprintf(coilCurrentDevice,'OUTPUT ON');
    
    % Sample-current init:
    % Output ON, duh
    fprintf(sampleCurrentDevice,'OUTPUT ON');
    
    % Field and sample-current values for execution:
    coilCurrent=1 ; % Amps
    sampleCurrent=0.2; % Amps
    sampleCurrentMeas = sampleCurrent;
    heatCurr=0;
    heatVolt=0;
    
    pauseInterval=0.25; % Seconds
    
    %Saving to file in a chosen folder
    savePath = SAVE_PATH;
    fnamePattern='SupCondData';%File name
    fname=nextAvailableFilename(savePath,fnamePattern,'csv');
    fprintf(1, 'Saving data to %s\n', fname);
    header='Time(sec),TempRes(Ohm),Temperature(K),SampVolt(V),SampCurr(A),CoilCurr(A)\n';
    
    file=fopen(fname,'w+');
    fprintf(file,header);
    fclose(file);
    
    fprintf(tempResDevice, 'READ?');%Reading Temperature in Ohms
    tempResistance = readMeas(tempResDevice);
    temperature = interp1(temperature_table(:,1),temperature_table(:,2),tempResistance);

    startTime=clock;
    fprintf(coilCurrentDevice,sprintf ('APPL %f, %f',15,coilCurrent));%Setting Field current
    fprintf(sampleCurrentDevice,sprintf ('INST P6V; VOLT 6; CURR %f; INST P25V; VOLT %f; CURR %f',sampleCurrent,heatVolt,heatCurr));%Set sample (Hall) current and heat current
    flag=temperature>MINIMUM_TEMPERATURE;
    time=etime(clock,startTime);
    time_limit = 120000;
    figure
    hold on
    while(flag && (time<time_limit))
        pause(pauseInterval);
        time=etime(clock,startTime);
        
        % Read temperature
        fprintf(tempResDevice, 'READ?');
        tempResistance = readMeas(tempResDevice);
        temperature = interp1(temperature_table(:,1),temperature_table(:,2),tempResistance);
        
         % Read sample current
       fprintf(sampleCurrentDevice, 'INST P6V; CURRENT?');
       sampleCurrentMeas = readMeas(sampleCurrentDevice);
       fprintf(sampleCurrentDevice, 'INST P25V;');
        
        % Read sample voltage
        fprintf(sampleVoltageDevice, 'READ?');
        sampleVoltage = readMeas(sampleVoltageDevice);
        
        % Read coil current
        fprintf(coilCurrentDevice, 'CURRENT?');
        coilCurrentMeas = readMeas(coilCurrentDevice);
        
%         plot(sampleCurrent,sampleVoltage,'b.','MarkerSize',20)
         plot(temperature,sampleVoltage,'b.','MarkerSize',20)
        xlabel("Temprature [K]");
        ylabel("Voltage[V]");
        
        dlmwrite (fname,[time,tempResistance,temperature,...
            sampleVoltage,sampleCurrentMeas,...
            coilCurrentMeas],'-append');
        
        flag=temperature > MINIMUM_TEMPERATURE;
    end
    %setting the currents back to zero
%     fprintf(sampleCurrentDevice,sprintf ('INST P6V; CURR %f; INST P25V; CURR %f',0,0));
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
