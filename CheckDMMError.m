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


%This function checks if the DMM has an error in its error queue.
%This is to be used with all .m example files for the 34460A/34461A
%Checks if there is an error in the queue. If yes, the, it continuously
%checks the queue until there is no error and throws and exception.
%Reports all errors in the exception.
%
%The command sent to the instrument is "SYST:ERR". If the returned string
%from the DMM contains "No error" the function returns. If if does not
%contain "No error", it will continue to send and read the SYST:ERR
%responses until "No error" is received. All the errors then are reported
%in the exception message.
function DmmErr = CheckDMMError(myDmm)
fprintf(myDmm,'SYST:ERR?');
errStr = fscanf(myDmm);

if (strfind(errStr,'No error')) %If no error, then return
    return;
    %If there is an error, read out all of the errors and return them in an exception
else
    errStr2 = errStr;
    NoErr = strfind(errStr2,'No error');
    while (isempty(NoErr));
        fprintf(myDmm,'SYST:ERR?');
        errStr2 = fscanf(myDmm);
        NoErr = strfind(errStr2,'No error');
        if (isempty(NoErr))
            errStr = strcat(errStr, '\n', errStr2);
        end
    end
    errStr = strcat('Exception: Encountered system error(s)\n',errStr)
    err = MException('ResultChk:BadInput',errStr);
    throw(err)
end

end