function [ myDmm ] = ConfigTemperature(  )
%UNTITLED3 Summary of this function goes here
%   Detailed explanation goes here

%'' """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
%''  © Agilent Technologies, Inc. 2013
%''
%'' You have a royalty-free right to use, modify, reproduce and distribute
%'' the Sample Application Files (and/or any modified version) in any way
%'' you find useful, provided that you agree that Agilent Technologies has no
%'' warranty,  obligations or liability for any Sample Application Files.
%''
%'' Agilent Technologies provides programming examples for illustration only,
%'' This sample program assumes that you are familiar with the programming
%'' language being demonstrated and the tools used to create and debug
%'' procedures. Agilent Technologies support engineers can help explain the
%'' functionality of Agilent Technologies software components and associated
%'' commands, but they will not modify these samples to provide added
%'' functionality or construct procedures to meet your specific needs.
%'' """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


%
%     'This example program illustrates how to connect to an instrument
%        'Gives an example setup for all major function configurations (DCV, DCI, Ohms2W, Ohms 4W, ACV, ACI, Temp, Freq).
%        'Gets a single reading from the DMM for each function and reports the result.
%        'Ohms 4W shows an autorange setup while all other functions show a direct range setup.

% First clear any connections with instruments
newobjs = instrfind;
if isempty(newobjs) == 0
    fclose(newobjs);
    delete(newobjs);
    clear newobjs
end
try
    % enter user's instrument connection string
    % DutAddr = 'GPIB0::22''; %String for GPIB
    % DutAddr = 'TCPIP0::169.254.4.61';  %Example string for LAN
    %string DutAddr = 'USB0::0x0957::0x1A07::MY53000101'; %Example string for USB
    %DutAddrr = 'USB0::0x0957::0x1C07::US00000069::0::INSTR';
    DutAddr = 'GPIB0::24::INSTR';  %Example string for LAN
    
    %connects with instrument and configures
    myDmm = visa('agilent',DutAddr);
    set(myDmm,'EOSMode','read&write');
    set(myDmm,'EOSCharCode','LF') ;
    fopen(myDmm);
    
    
    
    
    
    
    
    
    
    %Configure for OHM 2 wire 100 Ohm range, 100uOhm resolution
    fprintf(myDmm,'CONF:RES 100, 0.0001');
    fprintf(myDmm,'READ?');
    Res2WResult = fscanf(myDmm);
    CheckDMMError(myDmm); %Check if the DMM has any errors
    
   
catch MExc
    MExc
    delete_all_objs()
    
end



end

